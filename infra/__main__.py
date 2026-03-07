"""Josi infrastructure entry point.

Each module defines resources for its concern.
Import order matters — modules with dependencies come after their deps.
"""

import pulumi
from config import environment, project, region

# Import all resource modules (order: independent -> dependent)
import registry    # Artifact Registry (no deps)
import storage     # GCS buckets (no deps)
import secrets     # Secret Manager (no deps)
import iam         # Service accounts + JSON key (no deps)
import database    # Cloud SQL (reads secrets)
import compute     # Cloud Run (depends on database, iam, registry, secrets)
import triggers    # Cloud Build triggers (no deps, references deploy/ YAMLs)

pulumi.export("environment", environment)
pulumi.export("project", project)
pulumi.export("region", region)
