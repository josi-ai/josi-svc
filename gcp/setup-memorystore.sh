#!/bin/bash
# Setup Memorystore for Redis instance for Josi

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
INSTANCE_NAME="josi-redis"
REGION="us-central1"
ZONE="us-central1-a"
TIER="STANDARD"  # BASIC or STANDARD
MEMORY_SIZE_GB="5"
REDIS_VERSION="REDIS_7_0"
NETWORK_NAME="default"

echo "Setting up Memorystore for Redis in project: $PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable redis.googleapis.com \
    servicenetworking.googleapis.com \
    --project=$PROJECT_ID

# Reserve IP range for VPC peering (if not already done)
echo "Checking VPC peering..."
if ! gcloud compute addresses describe google-managed-services-$NETWORK_NAME --global --project=$PROJECT_ID 2>/dev/null; then
    echo "Creating IP address range for VPC peering..."
    gcloud compute addresses create google-managed-services-$NETWORK_NAME \
        --global \
        --purpose=VPC_PEERING \
        --prefix-length=16 \
        --network=projects/$PROJECT_ID/global/networks/$NETWORK_NAME \
        --project=$PROJECT_ID

    # Create VPC peering
    echo "Creating VPC peering connection..."
    gcloud services vpc-peerings connect \
        --service=servicenetworking.googleapis.com \
        --ranges=google-managed-services-$NETWORK_NAME \
        --network=$NETWORK_NAME \
        --project=$PROJECT_ID
fi

# Create Memorystore instance
echo "Creating Memorystore Redis instance..."
gcloud redis instances create $INSTANCE_NAME \
    --size=$MEMORY_SIZE_GB \
    --region=$REGION \
    --zone=$ZONE \
    --redis-version=$REDIS_VERSION \
    --network=projects/$PROJECT_ID/global/networks/$NETWORK_NAME \
    --tier=$TIER \
    --enable-auth \
    --maintenance-window-day=sunday \
    --maintenance-window-hour=4 \
    --project=$PROJECT_ID

# Wait for instance to be ready
echo "Waiting for Redis instance to be ready..."
gcloud redis instances describe $INSTANCE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(state)" | grep -q "READY" || \
    (echo "Waiting for instance creation..." && sleep 60)

# Get instance details
REDIS_HOST=$(gcloud redis instances describe $INSTANCE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(host)")

REDIS_PORT=$(gcloud redis instances describe $INSTANCE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(port)")

REDIS_AUTH=$(gcloud redis instances get-auth-string $INSTANCE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID)

echo "Memorystore Redis setup complete!"
echo "Redis Host: $REDIS_HOST"
echo "Redis Port: $REDIS_PORT"
echo "Redis Auth String: $REDIS_AUTH"
echo ""
echo "Redis URL format: redis://:$REDIS_AUTH@$REDIS_HOST:$REDIS_PORT/0"
echo ""
echo "Store the Redis URL in Google Secret Manager:"
echo "echo -n 'redis://:AUTH_STRING@$REDIS_HOST:$REDIS_PORT/0' | gcloud secrets create josi-redis-url --data-file=-"
echo ""
echo "Note: Replace AUTH_STRING with the actual auth string from the output above"