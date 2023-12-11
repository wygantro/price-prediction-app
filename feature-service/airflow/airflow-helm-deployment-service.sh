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

# add Airflow Helm Stable Repo
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# create namespace
export NAMESPACE=airflow
kubectl create namespace $NAMESPACE

# apply variables config map
kubectl apply -f variables.yaml

# install apache-airflow chart and airflow-values.yaml
helm install airflow apache-airflow/airflow --namespace $NAMESPACE -f values.yaml

# confirm pods
kubectl get pods --namespace $NAMESPACE
helm list --namespace $NAMESPACE

echo "airflow-helm-deployment-service to GKE complete"