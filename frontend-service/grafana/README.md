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