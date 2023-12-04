# prediction loop build, push and run locally

## Local image build and run on Docker

1. Build docker file
```
docker build -t prediction-loop:latest .
```

2. Mount docker managed dataframe_volume and run
```
docker run -d -p 8000:8000 -v dataframes_volume:/dataframes prediction-loop:latest

```