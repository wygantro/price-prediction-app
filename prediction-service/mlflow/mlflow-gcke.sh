#!/bin/bash

# check if the script has execution permissions
if [[ ! -x $0 ]]; then
    echo "making the script executable"
    chmod +x $0
    exec $0 "$@"
fi

# configure cluster
gcloud auth configure-docker
gcloud container clusters get-credentials project-cluster

# add MLflow Helm Stable Repo
helm repo add community-charts https://community-charts.github.io/helm-charts
helm repo update

# create namespace
export NAMESPACE=mlflow
kubectl create namespace $NAMESPACE

# install apache-airflow chart and airflow-values.yaml
helm install community-charts/mlflow --namespace $NAMESPACE --generate-name -f values.yaml

# confirm pods
kubectl get pods --namespace $NAMESPACE
helm list --namespace $NAMESPACE

echo "mlflow-helm-deployment to GKE complete"