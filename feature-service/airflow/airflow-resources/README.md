## Apache Airflow Helm Chart Google Cloud Kubernetes Deployment

1. Initialize Google Cloud and connect to dev-ops-cluster
```bash
gcloud init

gcloud container clusters get-credentials project-cluster
```


2. Build and push images to Google Cloud Container Registry
```bash

# # config map
# kubectl create configmap airflow-config --from-file=airflow.ini

# # dag volume
# kubectl apply -f airflow-pvc.yaml

# apploy deployment/service
./airflow-helm-deployment-service.sh
```


3. Access and delete namespace
```bash
kubectl get namespaces

kubectl delete namespace airflow

```