"""Artifact Registry for container images.

Shared across dev and prod — images are tagged per environment.
"""

import pulumi
import pulumi_gcp as gcp
from config import project, registry_location, registry_repo


# Single Docker repo shared by dev and prod (images tagged differently)
repository = gcp.artifactregistry.Repository(
    "josi-docker",
    repository_id=registry_repo,
    location=registry_location,
    format="DOCKER",
    project=project,
    description="Josi platform container images",
    cleanup_policies=[
        gcp.artifactregistry.RepositoryCleanupPolicyArgs(
            id="keep-recent",
            action="KEEP",
            most_recent_versions=gcp.artifactregistry.RepositoryCleanupPolicyMostRecentVersionsArgs(
                keep_count=10,
            ),
        ),
    ],
)

# Export the registry URL for use in CI/CD
registry_url = pulumi.Output.concat(
    registry_location, "-docker.pkg.dev/", project, "/", registry_repo
)

pulumi.export("registry_url", registry_url)
