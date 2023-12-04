# frontend-service container build, push and run locally


### frontend-dashboard-backend

1. Build docker file
```
docker build -t frontend-dashboard-backend:latest -f Dockerfile1 .
```


2. Mount docker managed dataframe_volume and run
```
docker run -d -p 7000:7000 -v dataframes_volume:/dataframes frontend-dashboard-backend:latest
```


### frontend-dashboard

1. Build docker file
```
docker build -t frontend-dashboard:latest -f Dockerfile2 .
```


2. Mount docker managed dataframe_volume and run
```
docker run -d -p 8050:8050 -v dataframes_volume:/dataframes frontend-dashboard:latest
```