"""Josi infrastructure entry point.

Each module defines resources for its concern.
Import order matters — modules with dependencies come after their deps.

Cloud Run services are NOT managed here — they are created and updated
by Cloud Build via `gcloud run deploy` in the cloudbuild YAML files.
This avoids config drift between Pulumi and Cloud Build.
"""

import pulumi
from config import environment, project, region

# Import all resource modules (order: independent -> dependent)
import registry      # Artifact Registry (no deps)
import storage       # GCS buckets (no deps)
import secrets       # Secret Manager (no deps)
import iam           # Service accounts (no deps)
import database      # Cloud SQL (reads secrets)
import triggers      # Cloud Build triggers (no deps, references deploy/ YAMLs)
import loadbalancer  # Global LB + Cloud Armor (reads config domains)

pulumi.export("environment", environment)
pulumi.export("project", project)
pulumi.export("region", region)
