"""Stack-aware configuration for Josi infrastructure.

To add a new environment (e.g., staging):
1. Create infra/Pulumi.staging.yaml (copy from dev, adjust values)
2. Create deploy/{api,web,infra}.cloudbuild.staging.yaml
3. Run: pulumi stack init govindnewform/staging && pulumi up
4. Create git branch: git checkout -b staging
5. Push — Cloud Build auto-deploys
"""

import pulumi

config = pulumi.Config("josi")
gcp_config = pulumi.Config("gcp")

# Core
environment = config.require("environment")
project = gcp_config.require("project")
region = gcp_config.get("region") or "us-central1"

# Git branch this env deploys from
branch_pattern = config.get("branch_pattern") or f"^{environment}$"
# Override for prod which uses main
if environment == "prod":
    branch_pattern = config.get("branch_pattern") or "^main$"

# GitHub repo (Cloud Build connection)
repo_connection = config.get("repo_connection") or f"projects/{project}/locations/{region}/connections/josiam/repositories/josi-ai-josi-svc"

# Database
db_tier = config.get("db_tier") or "db-f1-micro"
db_edition = config.get("db_edition") or "ENTERPRISE"
db_version = config.get("db_version") or "POSTGRES_17"
db_disk_size = config.get_int("db_disk_size") or 10
db_availability = config.get("db_availability") or "ZONAL"
db_deletion_protection = config.get_bool("db_deletion_protection") or False

# Cloud Run - API
api_memory = config.get("api_memory") or "512Mi"
api_cpu = config.get("api_cpu") or "1"
api_min_instances = config.get_int("api_min_instances") or 0
api_max_instances = config.get_int("api_max_instances") or 3

# Cloud Run - Web
web_memory = config.get("web_memory") or "512Mi"
web_cpu = config.get("web_cpu") or "1"
web_min_instances = config.get_int("web_min_instances") or 0
web_max_instances = config.get_int("web_max_instances") or 3

# Domains
api_domain = config.get("api_domain") or ""
web_domain = config.get("web_domain") or ""
enable_custom_domains = bool(api_domain and web_domain)

# API Gateway
enable_api_gateway = config.get_bool("enable_api_gateway") or False

# Storage
bucket_location = config.get("bucket_location") or "us-central1"

# Artifact Registry (shared across envs)
registry_location = region
registry_repo = "josi"


def name(resource: str) -> str:
    """Generate environment-suffixed resource name. e.g., name('api') -> 'josi-api-dev'"""
    return f"josi-{resource}-{environment}"


def secret_name(key: str) -> str:
    """Generate secret name. e.g., secret_name('db-password') -> 'josiam-db-password-dev'"""
    return f"josiam-{key}-{environment}"
