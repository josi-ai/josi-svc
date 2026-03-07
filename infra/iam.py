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
# This SA is used for both Cloud Run runtime AND Cloud Build triggers
_roles = {
    # Runtime
    "sql-client": "roles/cloudsql.client",
    "secret-accessor": "roles/secretmanager.secretAccessor",
    "storage-user": "roles/storage.objectUser",
    "token-creator": "roles/iam.serviceAccountTokenCreator",
    # Build + deploy
    "ar-writer": "roles/artifactregistry.writer",
    "run-admin": "roles/run.admin",
    "log-writer": "roles/logging.logWriter",
    "sa-user": "roles/iam.serviceAccountUser",
}

iam_bindings = {}
for suffix, role in _roles.items():
    iam_bindings[suffix] = gcp.projects.IAMMember(
        name(f"sa-{suffix}"),
        project=project,
        role=role,
        member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
    )

pulumi.export("service_account_email", service_account.email)
