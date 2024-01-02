## MLFlow Local Deployment

1. Install MLFlow (if applicable)
```bash
pip install mlflow
```

2. Configure mlflow.server.yaml file

3. Initialize MLflow server and database
```bash
mlflow server \
    --backend-store-uri # mlflow db uri \
    --default-artifact-root ./mlflow-artifacts \
    --host 0.0.0.0 \
    --port 5000 \
    --file-store ./mlflow

Example :

mlflow server \
    --backend-store-uri # mlflow db uri \   
    --default-artifact-root gs://mlflow_warehouse
```

3. Access MLflow UI
```bash
http://<MLFLOW_SERVER_HOST>:<MLFLOW_SERVER_PORT>
``
mlflow db upgrade --url # mlflow db uri
# Replace <MLFLOW_SERVER_HOST> and <MLFLOW_SERVER_PORT> with the host and port where you started the MLflow
```