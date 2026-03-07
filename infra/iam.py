"""Service accounts and IAM bindings.

Two SAs:
- josi-{env}: Runtime SA for Cloud Run (minimal permissions)
- josi-infra: Shared SA for Cloud Build + Pulumi (admin permissions)

IAM bindings are managed locally (not via Cloud Build) because
GCP restricts SAs from modifying project IAM policies.
When adding a new env, run: pulumi up --target 'urn:...:iam*' locally.
"""

import pulumi
import pulumi_gcp as gcp
from config import environment, project, name


# ---------- Runtime SA (Cloud Run) ----------

service_account = gcp.serviceaccount.Account(
    name("sa"),
    account_id=f"josi-{environment}",
    display_name=f"Josi {environment} Cloud Run SA",
    project=project,
)

_runtime_roles = {
    "sql-client": "roles/cloudsql.client",
    "secret-accessor": "roles/secretmanager.secretAccessor",
    "storage-user": "roles/storage.objectUser",
    "log-writer": "roles/logging.logWriter",
    "token-creator": "roles/iam.serviceAccountTokenCreator",
}

for suffix, role in _runtime_roles.items():
    gcp.projects.IAMMember(
        name(f"sa-{suffix}"),
        project=project,
        role=role,
        member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
    )


# ---------- Infra SA (Cloud Build + Pulumi) ----------
# Shared across envs — manages all GCP resources via Pulumi

infra_sa = gcp.serviceaccount.Account(
    "josi-infra-sa",
    account_id="josi-infra",
    display_name="Josi Infrastructure SA (Pulumi + Cloud Build)",
    project=project,
)

_infra_roles = {
    "sql-admin": "roles/cloudsql.admin",
    "secret-admin": "roles/secretmanager.admin",
    "storage-admin": "roles/storage.admin",
    "ar-admin": "roles/artifactregistry.admin",
    "run-admin": "roles/run.admin",
    "cb-editor": "roles/cloudbuild.builds.editor",
    "iam-security": "roles/iam.securityAdmin",
    "sa-admin": "roles/iam.serviceAccountAdmin",
    "sa-user": "roles/iam.serviceAccountUser",
    "log-writer": "roles/logging.logWriter",
}

for suffix, role in _infra_roles.items():
    gcp.projects.IAMMember(
        f"josi-infra-{suffix}",
        project=project,
        role=role,
        member=infra_sa.email.apply(lambda e: f"serviceAccount:{e}"),
    )

pulumi.export("service_account_email", service_account.email)
pulumi.export("infra_sa_email", infra_sa.email)
