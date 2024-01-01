## Feature Service Google Cloud Kubernetes Deployment

1. Initialize Google Cloud
```bash
gcloud init
```


2. Create api-keys for feature-service API connections
```bash
kubectl create secret generic api-keys \
    --from-literal=polygon_api_key=???
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


## Feature Service Alembic Database Migration

1. Initialize Alembic directory for prediction-service-db
```bash
alembic init alembic
```


2. Modify alembic.ini sqlalchemy url address


3. Modify env.py to import prediction_service_models
```bash
from run.app import feature_service_models
target_metadata = feature_service_models.Base.metadata
```


4. Create migration
```bash
alembic revision --autogenerate -m "message"
alembic revision --autogenerate -m "added ETH price data tables"
```


5. Apply the migration
```bash
alembic upgrade head
```


6. Rollback migration (if needed)
```bash
alembic downgrade -1
```