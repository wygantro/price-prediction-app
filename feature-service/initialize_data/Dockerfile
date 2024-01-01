# Dockerfile

FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /feature-service-intialize

ENV APP_HOME /feature-service-initialize
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r ./config/requirements.txt

EXPOSE 3000

# database env
ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_FEATURE_SERVICE_NAME=feature-service-db
ENV DB_PREDICTION_SERVICE_NAME=prediction-service-d
ENV DB_MLFLOW_NAME=mlflow-db
#ENV DB_HOST=172.30.192.3
ENV DB_HOST=35.184.60.255
ENV DB_PORT=5432

# API keys
ENV POLYGON_API_KEY=68V4qcNzPdz7NuKkNvG5Hj2Z1O4hbvJj

CMD ["python", "initialize_data.py"]