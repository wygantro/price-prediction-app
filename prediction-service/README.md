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

## Prediction Service Alembic Database Migration

1. Initialize Alembic directory for prediction-service-db
```bash
alembic init alembic
```


2. Modify alembic.ini sqlalchemy url address


3. Modify env.py to import prediction_service_models
```bash
from prediction_loop.app import prediction_service_models
target_metadata = prediction_service_models.Base.metadata
```


4. Create migration
```bash
alembic revision --autogenerate -m "message"
alembic revision --autogenerate -m "initial migration"
```


5. Apply the migration
```bash
alembic upgrade head
```


6. Rollback migration (if needed)
```bash
alembic downgrade -1

# get current migration status
alembic current
```