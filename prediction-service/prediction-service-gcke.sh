#!/bin/bash

# check if the script has execution permissions
if [[ ! -x $0 ]]; then
    echo "Making the script executable..."
    chmod +x $0
    exec $0 "$@"
fi

# define prediction-service images
IMAGE_1_NAME="prediction-service-loop"
#IMAGE_2_NAME="prediction-etl-train"
PROJECT_ID="$(gcloud config get-value project)"
GCR_HOSTNAME="gcr.io"

# build and push image to Google Cloud
docker build -t "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_1_NAME}:latest" ./prediction_loop
gcloud auth configure-docker
docker push "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_1_NAME}:latest"


echo "prediction-service images built and pushed successfully"

# configure cluster
gcloud container clusters get-credentials project-cluster

# apply prediction-service volume and deployment
kubectl apply -f prediction-pvc.yaml
kubectl apply -f prediction-deployment.yaml

echo "prediction-service deployed to GKE"