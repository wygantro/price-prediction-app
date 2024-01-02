# Dockerfile

FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /feature-service

ENV APP_HOME /feature-service
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r ./config/requirements.txt

EXPOSE 4000

# database env
ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_FEATURE_SERVICE_NAME=feature-service-db
### removed host and port

# API keys
ENV POLYGON_API_KEY=68V4qcNzPdz7NuKkNvG5Hj2Z1O4hbvJj

CMD ["python", "feature_service_run.py"]