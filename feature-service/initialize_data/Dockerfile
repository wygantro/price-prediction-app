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
### removed host and port

# API keys
ENV POLYGON_API_KEY=???

CMD ["python", "initialize_data.py"]