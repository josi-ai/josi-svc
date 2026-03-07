"""Stack-aware configuration for Josi infrastructure."""

import pulumi

config = pulumi.Config("josi")
gcp_config = pulumi.Config("gcp")

# Core
environment = config.require("environment")  # "dev" or "prod"
project = gcp_config.require("project")
region = gcp_config.get("region") or "us-central1"

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

# Storage
bucket_location = config.get("bucket_location") or "us-central1"

# Artifact Registry
registry_location = region
registry_repo = "josi"


def name(resource: str) -> str:
    """Generate environment-suffixed resource name."""
    return f"josiam-{resource}-{environment}"
