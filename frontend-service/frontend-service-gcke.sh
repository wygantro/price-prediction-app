#!/bin/bash

# check if the script has execution permissions
if [[ ! -x $0 ]]; then
    echo "making the script executable"
    chmod +x $0
    exec $0 "$@"
fi

# define frontend-service images
IMAGE_1_NAME="frontend-dashboard-backend"
IMAGE_2_NAME="frontend-dashboard"
PROJECT_ID="$(gcloud config get-value project)"
GCR_HOSTNAME="gcr.io"


# build and push image to Google Cloud
docker build -t "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_1_NAME}:latest" -f ./dashboard/Dockerfile1 ./dashboard 
gcloud auth configure-docker
docker push "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_1_NAME}:latest"

docker build -t "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_2_NAME}:latest" -f ./dashboard/Dockerfile2 ./dashboard
docker push "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_2_NAME}:latest"

echo "frontend-service images built and pushed successfully"

# configure cluster
gcloud container clusters get-credentials project-cluster

# apply frontend-service volume, deployment and service
kubectl apply -f frontend-pvc.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
#kubectl apply -f frontend-ingress.yaml

echo "frontend-service deployed to GKE"

# # config, pull and deploy Grafana instance
# kubectl create configmap grafana-config --from-file=./grafana/grafana.ini
# kubectl apply -f ./grafana/grafana-deployment-service.yaml

# echo "frontend-service Grafana image deployed to GKE"