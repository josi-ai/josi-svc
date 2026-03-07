"""Cloud Build triggers for API and Web deployments.

Each trigger watches a specific branch and file path pattern,
then runs the corresponding cloudbuild YAML.
"""

import pulumi
import pulumi_gcp as gcp
from config import environment, project, region, name, branch_pattern, repo_connection


# --- API trigger ---
api_trigger = gcp.cloudbuild.Trigger(
    name("trigger-api"),
    name=f"josi-api-{environment}",
    project=project,
    location=region,
    repository_event_config=gcp.cloudbuild.TriggerRepositoryEventConfigArgs(
        repository=repo_connection,
        push=gcp.cloudbuild.TriggerRepositoryEventConfigPushArgs(
            branch=branch_pattern,
        ),
    ),
    included_files=[
        "src/**",
        "tests/**",
        "Dockerfile",
        "pyproject.toml",
        "poetry.lock",
        "alembic.ini",
    ],
    filename=f"deploy/api.cloudbuild.{environment}.yaml",
)

# --- Web trigger ---
web_trigger = gcp.cloudbuild.Trigger(
    name("trigger-web"),
    name=f"josi-web-{environment}",
    project=project,
    location=region,
    repository_event_config=gcp.cloudbuild.TriggerRepositoryEventConfigArgs(
        repository=repo_connection,
        push=gcp.cloudbuild.TriggerRepositoryEventConfigPushArgs(
            branch=branch_pattern,
        ),
    ),
    included_files=["web/**"],
    filename=f"deploy/web.cloudbuild.{environment}.yaml",
)

# --- Infra trigger ---
infra_trigger = gcp.cloudbuild.Trigger(
    name("trigger-infra"),
    name=f"josi-infra-{environment}",
    project=project,
    location=region,
    repository_event_config=gcp.cloudbuild.TriggerRepositoryEventConfigArgs(
        repository=repo_connection,
        push=gcp.cloudbuild.TriggerRepositoryEventConfigPushArgs(
            branch=branch_pattern,
        ),
    ),
    included_files=["infra/**"],
    filename=f"deploy/infra.cloudbuild.{environment}.yaml",
)

pulumi.export("api_trigger", api_trigger.name)
pulumi.export("web_trigger", web_trigger.name)
pulumi.export("infra_trigger", infra_trigger.name)
