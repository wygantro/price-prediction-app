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


3. Upgrade Helm deployment
```bash

```


4. Access or delete namespace
```bash
kubectl get namespaces

kubectl delete namespace airflow

# pod status
kubectl get pods -n airflow

# logs for git-sync
kubectl logs <airflow-scheduler> -c git-sync -n airflow

kubectl logs airflow-scheduler-6dbb64b784-hz29w -c git-sync -n airflow

```




## get values.yaml file from helm chart
helm show values apache-airflow/airflow > values.yaml


## modifications to values.yaml
1) update service type to LoadBalancer (line 1241)
2) update executor to KubernetesExecutor (line 264)
3) ??? config map ???

## sync dags
4) 

# ssh key for github

ssh-keygen -t ed25519 -C "robert.wygant3l@gmail.com"

cloud composer???



# ref gitsync tutorial link ref

https://blog.devgenius.io/setting-up-apache-airflow-on-kubernetes-with-gitsync-beaac2e397f3


https://www.astronomer.io/events/webinars/airflow-helm-chart/