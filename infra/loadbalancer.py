"""Global Application Load Balancer with Cloud Armor.

Per environment, creates:
- Reserved global static IP
- Google-managed SSL certificates (auto-provisioned when DNS points to IP)
- Serverless NEGs for Cloud Run services (api + web)
- Cloud Armor security policy (WAF + rate limiting + DDoS)
- Backend services with Cloud Armor attached
- URL map with host-based routing (api domain → api, web domain → web)
- HTTPS proxy + forwarding rule
- HTTP → HTTPS redirect
- IAM bindings so the LB service agent can invoke Cloud Run

After `pulumi up`, point DNS A records to the exported `lb_ip` value.
SSL certs auto-provision once DNS resolves (can take 15-60 minutes).
"""

import pulumi
import pulumi_gcp as gcp
from config import (
    environment, project, region, name,
    api_domain, web_domain, www_redirect, enable_custom_domains,
)

if not enable_custom_domains:
    pulumi.log.info("Custom domains not configured — skipping load balancer setup")
else:
    # ---- Static IP ----
    global_ip = gcp.compute.GlobalAddress(
        name("lb-ip"),
        project=project,
    )

    # ---- Managed SSL Certificates ----
    # Auto-provision once DNS A records point to the static IP
    api_ssl_cert = gcp.compute.ManagedSslCertificate(
        name("api-ssl"),
        managed=gcp.compute.ManagedSslCertificateManagedArgs(
            domains=[api_domain],
        ),
        project=project,
    )

    # SSL cert domains: web_domain + www.web_domain if redirect enabled
    web_ssl_domains = [web_domain]
    if www_redirect:
        web_ssl_domains.append(f"www.{web_domain}")

    web_ssl_cert = gcp.compute.ManagedSslCertificate(
        name("web-ssl"),
        managed=gcp.compute.ManagedSslCertificateManagedArgs(
            domains=web_ssl_domains,
        ),
        project=project,
    )

    # ---- Serverless NEGs (point to Cloud Run services) ----
    api_neg = gcp.compute.RegionNetworkEndpointGroup(
        name("api-neg"),
        region=region,
        network_endpoint_type="SERVERLESS",
        cloud_run=gcp.compute.RegionNetworkEndpointGroupCloudRunArgs(
            service=name("api"),  # e.g. josi-api-dev
        ),
        project=project,
    )

    web_neg = gcp.compute.RegionNetworkEndpointGroup(
        name("web-neg"),
        region=region,
        network_endpoint_type="SERVERLESS",
        cloud_run=gcp.compute.RegionNetworkEndpointGroupCloudRunArgs(
            service=name("web"),  # e.g. josi-web-dev
        ),
        project=project,
    )

    # ---- Cloud Armor Security Policy ----
    is_prod = environment == "prod"

    security_policy = gcp.compute.SecurityPolicy(
        name("cloud-armor"),
        project=project,
        adaptive_protection_config=gcp.compute.SecurityPolicyAdaptiveProtectionConfigArgs(
            layer7_ddos_defense_config=gcp.compute.SecurityPolicyAdaptiveProtectionConfigLayer7DdosDefenseConfigArgs(
                enable=True,
            ),
        ),
    )

    # Rate limiting rule
    rate_limit_rule = gcp.compute.SecurityPolicyRule(
        name("rate-limit"),
        security_policy=security_policy.name,
        priority=1000,
        action="rate_based_ban",
        rate_limit_options=gcp.compute.SecurityPolicyRuleRateLimitOptionsArgs(
            conform_action="allow",
            exceed_action="deny(429)",
            rate_limit_threshold=gcp.compute.SecurityPolicyRuleRateLimitOptionsRateLimitThresholdArgs(
                count=60 if is_prod else 200,
                interval_sec=60,
            ),
            ban_duration_sec=300,
            ban_threshold=gcp.compute.SecurityPolicyRuleRateLimitOptionsBanThresholdArgs(
                count=120 if is_prod else 400,
                interval_sec=60,
            ),
            enforce_on_key="IP",
        ),
        match=gcp.compute.SecurityPolicyRuleMatchArgs(
            versioned_expr="SRC_IPS_V1",
            config=gcp.compute.SecurityPolicyRuleMatchConfigArgs(
                src_ip_ranges=["*"],
            ),
        ),
        project=project,
    )

    # OWASP ModSecurity CRS (prod: deny, dev: log-only via preview)
    owasp_rules = [
        ("sqli", "sqli-v33-stable", 2000),
        ("xss", "xss-v33-stable", 2001),
        ("lfi", "lfi-stable", 2002),
        ("rfi", "rfi-stable", 2003),
        ("rce", "rce-stable", 2004),
        ("scanner", "scannerdetection-stable", 2005),
        ("protocol-attack", "protocolattack-stable", 2006),
        ("session-fixation", "sessionfixation-stable", 2007),
    ]

    for rule_name, expression, priority in owasp_rules:
        gcp.compute.SecurityPolicyRule(
            name(f"waf-{rule_name}"),
            security_policy=security_policy.name,
            priority=priority,
            action="deny(403)",
            preview=not is_prod,  # dev: evaluate only (preview mode)
            match=gcp.compute.SecurityPolicyRuleMatchArgs(
                expr=gcp.compute.SecurityPolicyRuleMatchExprArgs(
                    expression=f"evaluatePreconfiguredWaf('{expression}')",
                ),
            ),
            project=project,
        )

    # ---- Backend Services ----
    api_backend = gcp.compute.BackendService(
        name("api-backend"),
        project=project,
        load_balancing_scheme="EXTERNAL_MANAGED",
        protocol="HTTPS",
        backends=[gcp.compute.BackendServiceBackendArgs(
            group=api_neg.id,
        )],
        security_policy=security_policy.id,
        log_config=gcp.compute.BackendServiceLogConfigArgs(
            enable=True,
            sample_rate=1.0 if not is_prod else 0.5,
        ),
    )

    web_backend = gcp.compute.BackendService(
        name("web-backend"),
        project=project,
        load_balancing_scheme="EXTERNAL_MANAGED",
        protocol="HTTPS",
        backends=[gcp.compute.BackendServiceBackendArgs(
            group=web_neg.id,
        )],
        security_policy=security_policy.id,
        enable_cdn=True,
        cdn_policy=gcp.compute.BackendServiceCdnPolicyArgs(
            cache_mode="CACHE_ALL_STATIC",
            default_ttl=3600,
            signed_url_cache_max_age_sec=0,
        ),
        log_config=gcp.compute.BackendServiceLogConfigArgs(
            enable=True,
            sample_rate=0.5,
        ),
    )

    # ---- URL Map (host-based routing) ----
    host_rules = [
        gcp.compute.URLMapHostRuleArgs(
            hosts=[api_domain],
            path_matcher="api",
        ),
        gcp.compute.URLMapHostRuleArgs(
            hosts=[web_domain],
            path_matcher="web",
        ),
    ]
    path_matchers = [
        gcp.compute.URLMapPathMatcherArgs(
            name="api",
            default_service=api_backend.id,
        ),
        gcp.compute.URLMapPathMatcherArgs(
            name="web",
            default_service=web_backend.id,
        ),
    ]

    # Redirect www.{web_domain} → web_domain
    if www_redirect:
        host_rules.append(gcp.compute.URLMapHostRuleArgs(
            hosts=[f"www.{web_domain}"],
            path_matcher="www-redirect",
        ))
        path_matchers.append(gcp.compute.URLMapPathMatcherArgs(
            name="www-redirect",
            default_url_redirect=gcp.compute.URLMapPathMatcherDefaultUrlRedirectArgs(
                host_redirect=web_domain,
                https_redirect=True,
                strip_query=False,
                redirect_response_code="MOVED_PERMANENTLY_DEFAULT",
            ),
        ))

    url_map = gcp.compute.URLMap(
        name("url-map"),
        project=project,
        default_service=web_backend.id,
        host_rules=host_rules,
        path_matchers=path_matchers,
    )

    # ---- HTTPS Proxy + Forwarding Rule ----
    https_proxy = gcp.compute.TargetHttpsProxy(
        name("https-proxy"),
        project=project,
        url_map=url_map.id,
        ssl_certificates=[api_ssl_cert.id, web_ssl_cert.id],
    )

    https_forwarding = gcp.compute.GlobalForwardingRule(
        name("https-fwd"),
        project=project,
        target=https_proxy.id,
        port_range="443",
        ip_address=global_ip.address,
        load_balancing_scheme="EXTERNAL_MANAGED",
    )

    # ---- HTTP → HTTPS Redirect ----
    redirect_url_map = gcp.compute.URLMap(
        name("http-redirect"),
        project=project,
        default_url_redirect=gcp.compute.URLMapDefaultUrlRedirectArgs(
            https_redirect=True,
            strip_query=False,
            redirect_response_code="MOVED_PERMANENTLY_DEFAULT",
        ),
    )

    http_proxy = gcp.compute.TargetHttpProxy(
        name("http-proxy"),
        project=project,
        url_map=redirect_url_map.id,
    )

    http_forwarding = gcp.compute.GlobalForwardingRule(
        name("http-fwd"),
        project=project,
        target=http_proxy.id,
        port_range="80",
        ip_address=global_ip.address,
        load_balancing_scheme="EXTERNAL_MANAGED",
    )

    # ---- IAM: Allow unauthenticated invocation via LB ----
    # EXTERNAL_MANAGED LBs don't authenticate to Cloud Run with a service agent.
    # Security is handled at two layers:
    #   1. Network: --ingress=internal-and-cloud-load-balancing (only LB traffic)
    #   2. Application: JWT validation in the app
    # Org policy overridden at project level to allow allUsers.
    for svc in ["api", "web"]:
        gcp.cloudrun.IamMember(
            name(f"{svc}-lb-invoker"),
            service=name(svc),
            location=region,
            project=project,
            role="roles/run.invoker",
            member="allUsers",
        )

    # ---- Exports ----
    pulumi.export("lb_ip", global_ip.address)
    pulumi.export("api_domain", api_domain)
    pulumi.export("web_domain", web_domain)
    dns_lines = [
        "Add these A records in GoDaddy:\n",
        "  ", api_domain, " → ", global_ip.address, "\n",
        "  ", web_domain, " → ", global_ip.address, "\n",
    ]
    if www_redirect:
        dns_lines.extend(["  www.", web_domain, " → ", global_ip.address, "\n"])
    dns_lines.append("SSL certs auto-provision once DNS resolves (15-60 min).")
    pulumi.export("dns_instructions", pulumi.Output.concat(*dns_lines))
