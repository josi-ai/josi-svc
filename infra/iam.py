"""Service accounts and IAM bindings."""

import pulumi
import pulumi_gcp as gcp
from config import environment, project, name


# Per-environment service account (josi-dev, josi-prod, etc.)
service_account = gcp.serviceaccount.Account(
    name("sa"),
    account_id=f"josi-{environment}",
    display_name=f"Josi {environment} service account",
    project=project,
)

# IAM roles for the service account
_roles = {
    "sql-client": "roles/cloudsql.client",
    "secret-accessor": "roles/secretmanager.secretAccessor",
    "storage-user": "roles/storage.objectUser",
    "ar-reader": "roles/artifactregistry.reader",
    "log-writer": "roles/logging.logWriter",
    # signBlob allows generating signed URLs without a JSON key
    "token-creator": "roles/iam.serviceAccountTokenCreator",
}

iam_bindings = {}
for suffix, role in _roles.items():
    iam_bindings[suffix] = gcp.projects.IAMMember(
        name(f"sa-{suffix}"),
        project=project,
        role=role,
        member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
    )

# Cloud Build SA needs to act as this SA for deployments
# Project number is 6486647520 (not project ID)
_cb_sa = "6486647520@cloudbuild.gserviceaccount.com"

cloud_build_act_as = gcp.serviceaccount.IAMMember(
    name("cb-act-as"),
    service_account_id=service_account.name,
    role="roles/iam.serviceAccountUser",
    member=f"serviceAccount:{_cb_sa}",
)

pulumi.export("service_account_email", service_account.email)
