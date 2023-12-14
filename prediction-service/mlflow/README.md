## MLflow Google Cloud Kubernetes Deployment

1. Initialize Google Cloud and connect to dev-ops-cluster
```bash
gcloud init

gcloud container clusters get-credentials project-cluster

```

2. Get values.yaml from helm chart and update (if applicable)
```bash
helm show values community-charts/mlflow > values.yaml

```


3. Build and push MLflow Helm chart
```bash
./mlflow-gcke.sh

```


4. Build and push MLflow Helm chart
```bash
# delete mlflow namespace
kubectl delete namespace mlflow

```


5. View logs
```bash
kubectl get pods --all-namespaces
kubectl logs POD_NAME

# reset pod
kubectl delete pod my-pod
```