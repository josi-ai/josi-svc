# Google Cloud Deployment Guide for Josi API

This guide provides step-by-step instructions for deploying the Josi API to Google Cloud Platform using either Cloud Run (serverless) or Google Kubernetes Engine (GKE).

## Prerequisites

1. Google Cloud Account with billing enabled
2. `gcloud` CLI installed and configured
3. `kubectl` installed (for GKE deployment)
4. Docker installed locally (for testing)
5. A domain name (optional, for custom domain)

## Architecture Overview

The deployment includes:
- **API Service**: Josi FastAPI application
- **Database**: Cloud SQL (PostgreSQL 16)
- **Cache**: Memorystore for Redis
- **Container Registry**: Artifact Registry
- **Load Balancer**: Google Cloud Load Balancing
- **CDN**: Cloud CDN (optional)
- **Monitoring**: Cloud Monitoring & Logging

## Option 1: Cloud Run Deployment (Recommended for Getting Started)

### 1. Set Up Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com
```

### 2. Set Up Cloud SQL

```bash
# Run the setup script
cd gcp
./setup-cloud-sql.sh
```

### 3. Set Up Memorystore Redis

```bash
# Run the setup script
./setup-memorystore.sh
```

### 4. Create Secrets

```bash
# Generate a secret key
export SECRET_KEY=$(openssl rand -hex 32)

# Create secrets in Secret Manager
echo -n "$SECRET_KEY" | gcloud secrets create josi-secret-key --data-file=-
echo -n "postgresql+asyncpg://josi:PASSWORD@/josi?host=/cloudsql/CONNECTION_NAME" | \
    gcloud secrets create josi-database-url --data-file=-
echo -n "redis://10.x.x.x:6379/0" | gcloud secrets create josi-redis-url --data-file=-
```

### 5. Deploy to Cloud Run

```bash
# Submit build and deploy
gcloud builds submit --config=cloudbuild.yaml
```

## Option 2: GKE Deployment (For Production Scale)

### 1. Run the Full Deployment Script

```bash
cd gcp
./deploy.sh $PROJECT_ID
```

This script will:
- Create a GKE cluster
- Set up networking and load balancing
- Deploy all Kubernetes resources
- Configure autoscaling

### 2. Manual Steps After Deployment

#### Update Secrets
```bash
# Get Cloud SQL connection details
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe josi-db \
    --format="value(connectionName)")

# Update database secret
echo -n "postgresql+asyncpg://josi:YOUR_PASSWORD@127.0.0.1:5432/josi" | \
    gcloud secrets versions add josi-database-url --data-file=-

# Get Redis details and update secret
REDIS_HOST=$(gcloud redis instances describe josi-redis \
    --region=us-central1 --format="value(host)")
echo -n "redis://:AUTH_STRING@$REDIS_HOST:6379/0" | \
    gcloud secrets versions add josi-redis-url --data-file=-
```

#### Configure DNS
```bash
# Get the static IP
STATIC_IP=$(gcloud compute addresses describe josi-api-ip \
    --global --format="value(address)")
echo "Add an A record pointing to: $STATIC_IP"
```

## Environment Variables

### Required Secrets (Store in Secret Manager)
- `SECRET_KEY`: JWT signing key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### Configuration (Set in Cloud Run or ConfigMap)
- `ENVIRONMENT`: `production`
- `AUTO_DB_MIGRATION`: `true` (runs migrations on startup)
- `EPHEMERIS_PATH`: `/usr/share/swisseph`
- `CORS_ORIGINS`: Your allowed origins
- `LOG_LEVEL`: `INFO` or `DEBUG`
- `RATE_LIMIT_ENABLED`: `true`
- `RATE_LIMIT_PER_MINUTE`: `60`

## Post-Deployment Tasks

### 1. Run Database Migrations

For Cloud Run:
```bash
gcloud run jobs create josi-migrate \
    --image=us-central1-docker.pkg.dev/$PROJECT_ID/josi/josi-api:latest \
    --command="poetry" \
    --args="run,alembic,upgrade,head" \
    --set-secrets="DATABASE_URL=josi-database-url:latest" \
    --region=us-central1

gcloud run jobs execute josi-migrate --region=us-central1
```

For GKE:
```bash
kubectl run migration --rm -i --tty \
    --image=us-central1-docker.pkg.dev/$PROJECT_ID/josi/josi-api:latest \
    --namespace=josi \
    -- poetry run alembic upgrade head
```

### 2. Create Initial Organization

```python
# Connect to the database and run:
from josi.models.organization_model import Organization
org = Organization(
    name="Default Organization",
    slug="default",
    api_key="your-api-key-here",
    is_active=True,
    plan_type="premium",
    monthly_api_limit=10000,
    current_month_usage=0
)
# Save to database
```

### 3. Set Up Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create josi-api-health \
    --display-name="Josi API Health Check" \
    --resource-type="https-public" \
    --host="api.yourdomain.com" \
    --path="/health/ready"
```

### 4. Configure Alerts

```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
    --notification-channels=YOUR_CHANNEL_ID \
    --display-name="High Error Rate" \
    --condition-display-name="Error rate > 1%" \
    --condition-type=threshold \
    --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"'
```

## Maintenance

### Update Application

```bash
# Trigger new build
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_TAG=v1.2.0
```

### Scale Resources

For Cloud Run:
```bash
gcloud run services update josi-api \
    --min-instances=2 \
    --max-instances=100 \
    --memory=2Gi \
    --cpu=2
```

For GKE:
```bash
kubectl scale deployment josi-api --replicas=5 -n josi
```

### Backup Database

```bash
# Create on-demand backup
gcloud sql backups create \
    --instance=josi-db \
    --description="Manual backup $(date +%Y%m%d)"
```

## Troubleshooting

### Check Logs

Cloud Run:
```bash
gcloud run logs read --service=josi-api --region=us-central1
```

GKE:
```bash
kubectl logs -f deployment/josi-api -n josi
```

### Database Connection Issues

1. Verify Cloud SQL Proxy is running (for GKE)
2. Check VPC peering is established
3. Verify database credentials in secrets

### Redis Connection Issues

1. Ensure Redis and application are in the same VPC
2. Check Redis auth string is correct
3. Verify firewall rules allow connection

### Performance Issues

1. Check CPU and memory metrics
2. Review slow query logs in Cloud SQL
3. Analyze Redis cache hit rates
4. Enable Cloud CDN for static assets

## Cost Optimization

1. **Use Preemptible VMs** for GKE nodes (70% cost savings)
2. **Enable autoscaling** with appropriate limits
3. **Set up budget alerts** in Cloud Billing
4. **Use Cloud CDN** to reduce egress costs
5. **Schedule downscaling** for non-production hours

## Security Best Practices

1. **Enable Binary Authorization** for container images
2. **Use Workload Identity** for service authentication
3. **Implement Cloud Armor** for DDoS protection
4. **Enable VPC Service Controls** for API security
5. **Regular security scanning** with Container Analysis
6. **Audit logging** with Cloud Audit Logs

## Backup and Disaster Recovery

1. **Database**: Automated daily backups with 7-day retention
2. **Redis**: Export snapshots to Cloud Storage
3. **Code**: Version controlled in Git
4. **Secrets**: Backed up in Secret Manager with versioning
5. **Infrastructure**: Terraform/Config Connector for IaC

## Support

For issues or questions:
1. Check application logs
2. Review Cloud Monitoring dashboards
3. Consult GCP documentation
4. Contact GCP support (if applicable)