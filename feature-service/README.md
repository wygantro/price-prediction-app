## Feature Service Google Cloud Kubernetes Deployment

1. Initialize Google Cloud
```bash
gcloud init
```


2. Create api-keys for feature-service API connections
```bash
kubectl create secret generic api-keys \
    --from-literal=polygon_api_key=68V4qcNzPdz7NuKkNvG5Hj2Z1O4hbvJj
```


3. Build, push and deploy images to Google Cloud Container Registry and Kubernetes Engine
```bash
./feature-service-gcke.sh
```


4. View logs
```bash
kubectl get pods --all-namespaces
kubectl logs POD_NAME
```