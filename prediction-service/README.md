## Prediction Service Google Cloud Kubernetes Deployment

1. Initialize Google Cloud
```bash
gcloud init
```


2. Build and push images to Google Cloud Container Registry
```bash
./prediction-service-gcke.sh
```


3. View logs
```bash
kubectl get pods --all-namespaces
kubectl logs POD_NAME

# reset pod
kubectl delete pod my-pod
```