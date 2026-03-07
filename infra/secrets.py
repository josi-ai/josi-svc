"""Secret Manager secret definitions.

Pulumi manages the secret containers. Values are set manually via gcloud
or CI/CD — never stored in Pulumi state.
"""

import pulumi
import pulumi_gcp as gcp
from config import environment, project, name


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
for secret_name in SECRET_NAMES:
    full_name = f"josiam-{secret_name}-{environment}"
    secrets[secret_name] = gcp.secretmanager.Secret(
        full_name,
        secret_id=full_name,
        project=project,
        replication=gcp.secretmanager.SecretReplicationArgs(
            auto=gcp.secretmanager.SecretReplicationAutoArgs(),
        ),
    )


def secret_ref(secret_name: str) -> str:
    """Return the secret reference string for Cloud Run --set-secrets."""
    return f"josiam-{secret_name}-{environment}:latest"


def secret_resource_name(secret_name: str) -> pulumi.Output:
    """Return the full resource name for a secret."""
    return secrets[secret_name].name


pulumi.export("secrets", {k: v.secret_id for k, v in secrets.items()})
