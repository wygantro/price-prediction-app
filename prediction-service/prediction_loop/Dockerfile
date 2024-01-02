FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /prediction_loop

ENV APP_HOME /prediction_loop
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r ./config/requirements.txt

# database env
ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_FEATURE_SERVICE_NAME=feature-service-db
ENV DB_PREDICTION_SERVICE_NAME=prediction-service-db
ENV DB_MLFLOW_NAME=mlflow-db
### removed host and port

EXPOSE 8000

# Run app.py using gunicorn when the container launches
CMD ["python", "prediction_loop.py"]