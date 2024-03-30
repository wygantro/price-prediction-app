# Dockerfile

FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /feature-service

ENV APP_HOME /feature-service-api
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r ./config/requirements.txt

EXPOSE 5000

# database env
ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_FEATURE_SERVICE_NAME=???
ENV DB_PREDICTION_SERVICE_NAME=???
ENV DB_MLFLOW_NAME=???
ENV DB_HOST=???
#ENV DB_HOST=???
ENV DB_PORT=???

# API keys
ENV POLYGON_API_KEY=????

CMD ["python", "feature_service_api.py"]