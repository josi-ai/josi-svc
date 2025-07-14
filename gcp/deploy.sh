#!/bin/bash
# Main deployment script for Josi API to Google Cloud

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION="us-central1"
ZONE="us-central1-a"
CLUSTER_NAME="josi-cluster"
ARTIFACT_REGISTRY="josi"

if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo "Usage: ./deploy.sh <PROJECT_ID>"
    exit 1
fi

echo "Deploying Josi API to Google Cloud Project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    container.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    compute.googleapis.com \
    --project=$PROJECT_ID

# Create Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create $ARTIFACT_REGISTRY \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Josi API" \
    --project=$PROJECT_ID || echo "Repository already exists"

# Create GKE cluster
echo "Creating GKE cluster..."
gcloud container clusters create $CLUSTER_NAME \
    --region=$REGION \
    --num-nodes=2 \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --machine-type=e2-standard-4 \
    --disk-size=50 \
    --enable-cloud-logging \
    --enable-cloud-monitoring \
    --network=default \
    --enable-ip-alias \
    --workload-pool=$PROJECT_ID.svc.id.goog \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
    --project=$PROJECT_ID || echo "Cluster already exists"

# Get cluster credentials
echo "Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID

# Create secrets in Secret Manager
echo "Creating secrets in Secret Manager..."
echo -n "your-secret-key-here" | gcloud secrets create josi-secret-key \
    --data-file=- \
    --project=$PROJECT_ID || echo "Secret already exists"

# Create service accounts
echo "Creating service accounts..."
gcloud iam service-accounts create josi-sa \
    --display-name="Josi API Service Account" \
    --project=$PROJECT_ID || echo "Service account already exists"

# Grant permissions
echo "Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:josi-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:josi-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Enable workload identity
kubectl create serviceaccount josi-sa --namespace josi || echo "Service account already exists"

gcloud iam service-accounts add-iam-policy-binding \
    josi-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[josi/josi-sa]" \
    --project=$PROJECT_ID

kubectl annotate serviceaccount josi-sa \
    iam.gke.io/gcp-service-account=josi-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --namespace josi || echo "Annotation already exists"

# Reserve static IP
echo "Reserving static IP..."
gcloud compute addresses create josi-api-ip \
    --global \
    --project=$PROJECT_ID || echo "IP already reserved"

STATIC_IP=$(gcloud compute addresses describe josi-api-ip \
    --global \
    --project=$PROJECT_ID \
    --format="value(address)")

echo "Static IP: $STATIC_IP"

# Update k8s manifests with project ID
echo "Updating Kubernetes manifests..."
find ../k8s -name "*.yaml" -type f -exec sed -i.bak "s/PROJECT_ID/$PROJECT_ID/g" {} \;

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f ../k8s/namespace.yaml
kubectl apply -f ../k8s/configmap.yaml
kubectl apply -f ../k8s/service-account.yaml
kubectl apply -f ../k8s/service.yaml
kubectl apply -f ../k8s/deployment.yaml
kubectl apply -f ../k8s/hpa.yaml
kubectl apply -f ../k8s/ingress.yaml

# Build and deploy using Cloud Build
echo "Triggering Cloud Build..."
gcloud builds submit --config=../cloudbuild.yaml \
    --substitutions=_PROJECT_ID=$PROJECT_ID \
    ..

echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Update the database URL secret: gcloud secrets versions add josi-database-url --data-file=-"
echo "2. Update the Redis URL secret: gcloud secrets versions add josi-redis-url --data-file=-"
echo "3. Update DNS to point to IP: $STATIC_IP"
echo "4. Monitor deployment: kubectl get pods -n josi"
echo "5. View logs: kubectl logs -f deployment/josi-api -n josi"