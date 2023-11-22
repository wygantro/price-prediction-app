## Feature service initialization build image and deploy container locally

1. Build docker image
```
docker build -t feature-service-initialize:latest .
```


2. Run local container
```
docker run -d -p 3000:3000 feature-service-initialize:latest 
```