#!/bin/bash

# check file execution permissions
if [[ ! -x $0 ]]; then
    echo "making the script executable..."
    chmod +x $0
    exec $0 "$@"
fi

# define feature-service image
IMAGE_NAME="feature-service"
PROJECT_ID="$(gcloud config get-value project)"
GCR_HOSTNAME="gcr.io"

# build and push image to Google Cloud
docker build -t "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_NAME}:latest" ./run
gcloud auth configure-docker
docker push "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_NAME}:latest"

echo "feature-service images built and pushed successfully"

# configure cluster and deploy to GCKE
gcloud container clusters get-credentials project-cluster
kubectl apply -f feature-service-deployment.yaml

echo "feature-service deployed to GKE"