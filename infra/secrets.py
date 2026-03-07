"""Secret Manager secret definitions.

Pulumi manages the secret containers. Values are set manually via gcloud
or CI/CD — never stored in Pulumi state.

Note: SA credentials secret is managed in iam.py (auto-populated with JSON key).
"""

import pulumi
import pulumi_gcp as gcp
from config import environment, project, secret_name


# Define all secrets this environment needs
SECRET_NAMES = [
    "db-password",
    "db-user",
    "db-instance-password",
    "auth-provider",
    "clerk-secret-key",
    "clerk-publishable-key",
    "clerk-webhook-secret",
    "descope-project-id",
    "descope-management-key",
    "descope-webhook-secret",
]

secrets = {}
for sname in SECRET_NAMES:
    full_name = secret_name(sname)
    secrets[sname] = gcp.secretmanager.Secret(
        full_name,
        secret_id=full_name,
        project=project,
        replication=gcp.secretmanager.SecretReplicationArgs(
            auto=gcp.secretmanager.SecretReplicationAutoArgs(),
        ),
    )


def secret_ref(sname: str) -> str:
    """Return the secret reference string for Cloud Run --set-secrets."""
    return f"{secret_name(sname)}:latest"


def secret_resource_name(sname: str) -> pulumi.Output:
    """Return the full resource name for a secret."""
    return secrets[sname].name


pulumi.export("secrets", {k: v.secret_id for k, v in secrets.items()})
