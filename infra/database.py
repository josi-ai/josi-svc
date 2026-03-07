"""Cloud SQL PostgreSQL instance, database, and user."""

import pulumi
import pulumi_gcp as gcp
from config import (
    environment, project, region, name,
    db_tier, db_edition, db_version, db_disk_size,
    db_availability, db_deletion_protection,
)


# Cloud SQL instance
instance = gcp.sql.DatabaseInstance(
    name("db"),
    name=f"josiam-{environment}",
    database_version=db_version,
    region=region,
    project=project,
    deletion_protection=db_deletion_protection,
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier=db_tier,
        edition=db_edition,
        disk_size=db_disk_size,
        disk_type="PD_SSD",
        disk_autoresize=True,
        availability_type=db_availability,
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=True,
            # In production, restrict to Cloud Run egress IPs or use private IP
        ),
        database_flags=[
            gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
                name="max_connections",
                value="100",
            ),
        ],
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=environment == "prod",
            start_time="03:00",
            point_in_time_recovery_enabled=environment == "prod",
            backup_retention_settings=gcp.sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
                retained_backups=7,
            ),
        ),
        insights_config=gcp.sql.DatabaseInstanceSettingsInsightsConfigArgs(
            query_insights_enabled=True,
            query_plans_per_minute=5,
        ),
    ),
)

# Database
database = gcp.sql.Database(
    name("db-josi"),
    name="josi",
    instance=instance.name,
    project=project,
)

# User — password is managed in Secret Manager, referenced here
db_password_secret = gcp.secretmanager.get_secret_version(
    secret=f"josiam-db-password-{environment}",
    project=project,
)

user = gcp.sql.User(
    name("db-user"),
    name="josi",
    instance=instance.name,
    password=db_password_secret.secret_data,
    project=project,
)

# Connection name for Cloud Run's built-in SQL connector
connection_name = instance.connection_name

# Export
pulumi.export("db_connection_name", connection_name)
pulumi.export("db_instance_ip", instance.public_ip_address)
