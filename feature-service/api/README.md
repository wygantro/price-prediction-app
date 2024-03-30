## Feature Service API Test build image and deploy container locally

1. Build docker image
```
docker build -t feature-service-api:latest .
```


2. Run local container
```
docker run -d -p 5000:5000 feature-service-api:latest 
```

## Feature Service API build and deploy Google Cloud Run

1. Initialize Google Cloud
```bash
gcloud init
```


2. Build, push and deploy images to Google Cloud Container Registry and Kubernetes Engine
```bash
./feature-service-api-gcr.sh
```


3. Launch in Google Cloud Run and set up Cloud Scheduler Cron Job
```bash
# Note: in cloud run enable network setting "Connect to a VPC for outbound traffic"

### cron job syntax ###
# daily: 0 0 * * *
# hour: 0 * * * *
# minute: * * * * *

### API extensions to call ###
# /feature-data-daily

# /btc-daily
# /btc-hour
# /btc-minute

# /eth-daily
# /eth-hour
# /eth-minute


# https://feature-service-api-wpyj5eetua-uc.a.run.app/
```