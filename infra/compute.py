"""Cloud Run services for API and Web."""

import pulumi
import pulumi_gcp as gcp
from config import (
    environment, project, region, name,
    api_memory, api_cpu, api_min_instances, api_max_instances,
    web_memory, web_cpu, web_min_instances, web_max_instances,
    registry_location, registry_repo,
)
from database import instance as db_instance, connection_name as db_connection_name
from iam import service_account
from secrets import secret_ref

registry_url = f"{registry_location}-docker.pkg.dev/{project}/{registry_repo}"

# ---------- API Service ----------

api_service = gcp.cloudrunv2.Service(
    name("api"),
    name=f"josi-api-{environment}",
    location=region,
    project=project,
    ingress="INGRESS_TRAFFIC_ALL",
    template=gcp.cloudrunv2.ServiceTemplateArgs(
        service_account=service_account.email,
        execution_environment="EXECUTION_ENVIRONMENT_GEN2",
        max_instance_request_concurrency=80,
        timeout="300s",
        scaling=gcp.cloudrunv2.ServiceTemplateScalingArgs(
            min_instance_count=api_min_instances,
            max_instance_count=api_max_instances,
        ),
        volumes=[
            gcp.cloudrunv2.ServiceTemplateVolumeArgs(
                name="cloudsql",
                cloud_sql_instance=gcp.cloudrunv2.ServiceTemplateVolumeCloudSqlInstanceArgs(
                    instances=[db_connection_name],
                ),
            ),
        ],
        containers=[
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"{registry_url}/josi-api:latest",
                ports=gcp.cloudrunv2.ServiceTemplateContainerPortsArgs(container_port=8000, name="http1"),
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={"memory": api_memory, "cpu": api_cpu},
                    cpu_idle=True,
                ),
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="ENVIRONMENT", value=environment,
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="AUTO_DB_MIGRATION", value="true",
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="EPHEMERIS_PATH", value="/usr/share/swisseph",
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CORS_ORIGINS", value="*",
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="LOG_LEVEL", value="INFO" if environment == "prod" else "DEBUG",
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="RATE_LIMIT_ENABLED", value="true",
                    ),
                    # Database URL via Cloud SQL Auth Proxy (Unix socket)
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="DATABASE_URL",
                        value=db_connection_name.apply(
                            lambda cn: f"postgresql+asyncpg://josi@/josi?host=/cloudsql/{cn}"
                        ),
                    ),
                    # Secrets injected from Secret Manager
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="AUTH_PROVIDER",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=f"josiam-auth-provider-{environment}",
                                version="latest",
                            ),
                        ),
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLERK_SECRET_KEY",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=f"josiam-clerk-secret-key-{environment}",
                                version="latest",
                            ),
                        ),
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLERK_WEBHOOK_SECRET",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=f"josiam-clerk-webhook-secret-{environment}",
                                version="latest",
                            ),
                        ),
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="DESCOPE_PROJECT_ID",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=f"josiam-descope-project-id-{environment}",
                                version="latest",
                            ),
                        ),
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="DESCOPE_WEBHOOK_SECRET",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=f"josiam-descope-webhook-secret-{environment}",
                                version="latest",
                            ),
                        ),
                    ),
                ],
                volume_mounts=[
                    gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                        name="cloudsql",
                        mount_path="/cloudsql",
                    ),
                ],
            ),
        ],
    ),
)

# Allow unauthenticated access (API handles its own auth)
api_iam = gcp.cloudrunv2.ServiceIamMember(
    name("api-invoker"),
    name=api_service.name,
    location=region,
    project=project,
    role="roles/run.invoker",
    member="allUsers",
)

# ---------- Web Service ----------

web_service = gcp.cloudrunv2.Service(
    name("web"),
    name=f"josi-web-{environment}",
    location=region,
    project=project,
    ingress="INGRESS_TRAFFIC_ALL",
    template=gcp.cloudrunv2.ServiceTemplateArgs(
        service_account=service_account.email,
        execution_environment="EXECUTION_ENVIRONMENT_GEN2",
        max_instance_request_concurrency=80,
        timeout="60s",
        scaling=gcp.cloudrunv2.ServiceTemplateScalingArgs(
            min_instance_count=web_min_instances,
            max_instance_count=web_max_instances,
        ),
        containers=[
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"{registry_url}/josi-web:latest",
                ports=gcp.cloudrunv2.ServiceTemplateContainerPortsArgs(container_port=3000, name="http1"),
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={"memory": web_memory, "cpu": web_cpu},
                    cpu_idle=True,
                ),
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="NODE_ENV", value="production",
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="NEXT_PUBLIC_API_URL",
                        value=api_service.uri,
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="API_URL",
                        value=api_service.uri,
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=f"josiam-clerk-publishable-key-{environment}",
                                version="latest",
                            ),
                        ),
                    ),
                ],
            ),
        ],
    ),
)

# Allow unauthenticated access (public website)
web_iam = gcp.cloudrunv2.ServiceIamMember(
    name("web-invoker"),
    name=web_service.name,
    location=region,
    project=project,
    role="roles/run.invoker",
    member="allUsers",
)

# Exports
pulumi.export("api_url", api_service.uri)
pulumi.export("web_url", web_service.uri)
