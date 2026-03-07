"""Cloud Storage buckets."""

import pulumi
import pulumi_gcp as gcp
from config import environment, project, bucket_location, name


# Main application bucket (user uploads, chart exports, etc.)
bucket = gcp.storage.Bucket(
    name("bucket"),
    name=f"josiam-{environment}",
    location=bucket_location,
    project=project,
    uniform_bucket_level_access=True,
    versioning=gcp.storage.BucketVersioningArgs(
        enabled=environment == "prod",
    ),
    lifecycle_rules=[
        # Auto-delete temp files after 7 days
        gcp.storage.BucketLifecycleRuleArgs(
            action=gcp.storage.BucketLifecycleRuleActionArgs(type="Delete"),
            condition=gcp.storage.BucketLifecycleRuleConditionArgs(
                age=7,
                matches_prefix=["tmp/"],
            ),
        ),
    ],
)

pulumi.export("bucket_name", bucket.name)
pulumi.export("bucket_url", bucket.url)
