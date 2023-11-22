## Grafana Service Google Cloud Kubernetes Deployment

1. Initialize Google Cloud and connect to dev-ops-cluster
```bash
gcloud init

gcloud container clusters get-credentials project-cluster
```

2. Build and push images to Google Cloud Container Registry
```bash

kubectl create configmap grafana-config --from-file=grafana.ini

kubectl apply -f grafana-deployment-service.yaml
```

4. Create Google Cloud service account with "Monitoring Viewer" role

5. Ensure service account has "Cloud Monitoring API" access

6. Enable "Monitoring API" and "Cloud Resource Manager API"

7. Login to Grafana instance with defined username and password in yaml file. Access from grafana-service endpoint.

8. Add Google Cloud data source from the Menu links on the left side of "Home" page.

9. From Google Cloud Service Accounts home page, click on service account and "Add Key"/download JSON

10. Upload JSON file as JWT file to authenticate data source connection

```bash
gcloud container clusters create project-cluster
```














4. Configure 'kubectl' to gcloud cluster
```bash
gcloud container clusters get-credentials dev-ops-cluster
```

5. Set up Cloud SQL and get 'connectionName' (PROJECT_ID:REGION:INSTANCE_ID)

6. Create a Kubernetes Secret
```bash
kubectl create secret generic cloudsql-db-credentials \
    --from-literal=username=user \
    --from-literal=password=postgres

    # --from-literal=username=
    # --from-literal=password=[YOUR_PASSWORD]
```

7. Apply persistent volumes and claims
```bash
kubectl apply -f pvc.yaml
```

8. Apply deployment and service
```bash
kubectl apply -f frontend-backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

9. View logs
```bash
kubectl logs POD_NAME
```