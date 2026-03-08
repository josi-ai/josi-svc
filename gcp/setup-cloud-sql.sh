#!/bin/bash
# Setup Cloud SQL for PostgreSQL instance for Josi

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
INSTANCE_NAME="josi-db"
REGION="us-central1"
TIER="db-g1-small"  # For production, use db-n1-standard-2 or higher
DB_VERSION="POSTGRES_16"
DB_NAME="josi"
DB_USER="josi"
NETWORK_NAME="default"

echo "Setting up Cloud SQL for Josi in project: $PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable sqladmin.googleapis.com \
    compute.googleapis.com \
    servicenetworking.googleapis.com \
    --project=$PROJECT_ID

# Create Cloud SQL instance
echo "Creating Cloud SQL instance..."
gcloud sql instances create $INSTANCE_NAME \
    --database-version=$DB_VERSION \
    --tier=$TIER \
    --region=$REGION \
    --network=projects/$PROJECT_ID/global/networks/$NETWORK_NAME \
    --no-assign-ip \
    --backup \
    --backup-start-time=03:00 \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=4 \
    --maintenance-release-channel=production \
    --enable-point-in-time-recovery \
    --retained-backups-count=7 \
    --transaction-log-retention-days=7 \
    --database-flags=max_connections=200,shared_buffers=256MB \
    --root-password=changeme \
    --project=$PROJECT_ID

# Create database
echo "Creating database..."
gcloud sql databases create $DB_NAME \
    --instance=$INSTANCE_NAME \
    --project=$PROJECT_ID

# Create user
echo "Creating database user..."
gcloud sql users create $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=changeme \
    --project=$PROJECT_ID

# Create service account for Cloud SQL proxy
echo "Creating service account for Cloud SQL proxy..."
gcloud iam service-accounts create cloudsql-proxy \
    --display-name="Cloud SQL Proxy" \
    --project=$PROJECT_ID

# Grant permissions
echo "Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloudsql-proxy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Create key for service account
echo "Creating service account key..."
gcloud iam service-accounts keys create cloudsql-proxy-key.json \
    --iam-account=cloudsql-proxy@$PROJECT_ID.iam.gserviceaccount.com \
    --project=$PROJECT_ID

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --format="value(connectionName)")

echo "Cloud SQL setup complete!"
echo "Connection name: $CONNECTION_NAME"
echo "Database URL format: postgresql+asyncpg://$DB_USER:PASSWORD@127.0.0.1:5432/$DB_NAME"
echo ""
echo "To connect using Cloud SQL Proxy:"
echo "cloud_sql_proxy -instances=$CONNECTION_NAME=tcp:5432"
echo ""
echo "IMPORTANT: Change the passwords for root and $DB_USER users!"
echo "Store the database URL in Google Secret Manager:"
echo "echo -n 'postgresql+asyncpg://$DB_USER:PASSWORD@127.0.0.1:5432/$DB_NAME' | gcloud secrets create josi-database-url --data-file=-"