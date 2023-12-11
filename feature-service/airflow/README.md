## Apache Airflow Helm Chart Google Cloud Kubernetes Deployment

1. Initialize Google Cloud and connect to dev-ops-cluster
```bash
gcloud init

gcloud container clusters get-credentials project-cluster

```


2. Get values.yaml from helm chart and update (if not already)
```bash
helm show values apache-airflow/airflow > values.yaml

# update airflow-ui endpoint type to loadbalancer

#   service:
#     type: LoadBalancer
#     ## service annotations

# executor: "KubernetesExecutor"

# extraEnvFrom: |
#   - configMapRef:
#       name: 'airflow-variables'

```


3. Build and push images to Google Cloud Container Registry
```bash
# apply deployment/service
./airflow-helm-deployment-service.sh

```


## gitSync with GitHub dags repository

4. Set up SSH key locally
```bash
ssh-keygen -t rsa -b 4096 -C "robert.wygant3@gmail.com"

# view key
cat ~/.ssh/id_rsa.pub

```


5. Deploy on github repository
```bash
#1) enter repository settings and click deploy keys
#2) copy generated key
cat ~/.ssh/id_rsa.pub

#3) add deploy keys and copy/paste
#4) save deployed key

```


6. Create and connect secrets and config map
```bash
# kubectl create secret generic airflow-ssh-secret --from-file=gitSshKey=id_rsa -n airflow
# /c/Users/Robert Wygant/.ssh/id_rsa

kubectl create secret generic airflow-ssh-secret --from-file="/c/Users/Robert Wygant/.ssh/id_rsa" -n airflow

kubectl apply -f variables.yaml
```


7. Update values.yaml
```bash
# update gitsync settings

  gitSync:
    enabled: true
    # github public keys
    knownHosts: |
      github.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCj7ndNxQowgcQnjshcLrqPEiiphnt+VTTvDP6mHBL9j1aNUkY4Ue1gvwnGLVlOhGeYrnZaMgRK6+PKCUXaDbC7qtbW8gIkhL7aGCsOr/C56SJMy/BCZfxd1nWzAOxSDPgVsmerOBYfNqltV9/hWCqBywINIR+5dIg6JTJ72pcEpEjcYgXkE2YEFXV1JHnsKgbLWNlhScqb2UmyRkQyytRLtL+38TGxkxCflmO+5Z8CSSNY7GidjMIZ7Q4zMjA2n1nGrlTDkzwDCsw+wqFPGQA179cnfGWOWRVruj16z6XyvxvjJwbz0wQZ75XK5tKSb7FNyeIEs4TT4jk+S4dhPeAUC5y+bDYirYgM4GC7uEnztnZyaVWQ7B381AK4Qdrwt51ZqExKbQpTUNn+EjqoTwvqNj4kqx5QUCI0ThS/YkOxJCXmPUWZbhjpCg56i+2aB6CmK2JGhn57K5mj0MNdBXA4/WnwH6XoPWJzK5Nyu2zB3nAZp+S5hpQs+p1vN1/wsjk=

    # git repo clone url
    # ssh example: git@github.com:apache/airflow.git
    # https example: https://github.com/apache/airflow.git
    #repo: https://github.com/apache/airflow.git

    repo: git@github.com:wygantro/price-prediction-app.git
    branch: main
    rev: HEAD
    depth: 1
    # the number of consecutive failures allowed before aborting
    maxFailures: 0
    # subpath within the repo where dags are located
    # should be "" if dags are at repo root
    subPath: "feature-service/airflow/dags"

# uncomment airflow-ssh-secret connection ref
sshKeySecret: airflow-ssh-secret

```


8. Update helm chart deployment with values.yaml
```bash
## 
helm upgrade --install airflow apache-airflow/airflow -n airflow -f values.yaml --debug
```


9. Access or delete namespace
```bash
kubectl get namespaces

kubectl delete namespace airflow

# pod status
kubectl get pods -n airflow
kubectl describe pod <pod-name>

# logs
kubectl logs <pod-name> -c <container-name>

```