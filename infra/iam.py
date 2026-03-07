"""Service accounts, IAM bindings, and JSON key for signed URLs."""

import pulumi
import pulumi_gcp as gcp
from config import environment, project, name, secret_name


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
}

iam_bindings = {}
for suffix, role in _roles.items():
    iam_bindings[suffix] = gcp.projects.IAMMember(
        name(f"sa-{suffix}"),
        project=project,
        role=role,
        member=service_account.email.apply(lambda e: f"serviceAccount:{e}"),
    )

# JSON key for signed URLs (stored in Secret Manager)
sa_key = gcp.serviceaccount.Key(
    name("sa-key"),
    service_account_id=service_account.name,
    public_key_type="TYPE_X509_PEM_FILE",
)

sa_credentials_secret = gcp.secretmanager.Secret(
    secret_name("sa-credentials"),
    secret_id=secret_name("sa-credentials"),
    project=project,
    replication=gcp.secretmanager.SecretReplicationArgs(
        auto=gcp.secretmanager.SecretReplicationAutoArgs(),
    ),
)

sa_credentials_version = gcp.secretmanager.SecretVersion(
    name("sa-credentials-version"),
    secret=sa_credentials_secret.id,
    secret_data=sa_key.private_key,
)

# Cloud Build service account needs to act as this SA for deployments
cloud_build_sa_email = pulumi.Output.concat(
    project, "@cloudbuild.gserviceaccount.com"
)

cloud_build_act_as = gcp.serviceaccount.IAMMember(
    name("cb-act-as"),
    service_account_id=service_account.name,
    role="roles/iam.serviceAccountUser",
    member=cloud_build_sa_email.apply(lambda e: f"serviceAccount:{e}"),
)

pulumi.export("service_account_email", service_account.email)
