"""Service accounts and IAM bindings."""

import pulumi_gcp as gcp
from config import environment, project, name


# Service account for Cloud Run services
service_account = gcp.serviceaccount.Account(
    name("sa"),
    account_id=f"josi-{environment}",
    display_name=f"Josi {environment} Cloud Run SA",
    project=project,
)

# Cloud SQL Client — allows Cloud Run to connect via Auth Proxy
sql_client_binding = gcp.projects.IAMMember(
    name("sa-sql-client"),
    project=project,
    role="roles/cloudsql.client",
    member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
)

# Secret Manager access — allows Cloud Run to read secrets
secret_accessor_binding = gcp.projects.IAMMember(
    name("sa-secret-accessor"),
    project=project,
    role="roles/secretmanager.secretAccessor",
    member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
)

# Cloud Storage access
storage_binding = gcp.projects.IAMMember(
    name("sa-storage"),
    project=project,
    role="roles/storage.objectUser",
    member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
)

# Artifact Registry reader — allows Cloud Run to pull images
ar_reader_binding = gcp.projects.IAMMember(
    name("sa-ar-reader"),
    project=project,
    role="roles/artifactregistry.reader",
    member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
)
