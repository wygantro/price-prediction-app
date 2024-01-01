# etl_train.py

import mlflow.sklearn
import mlflow
from mlflow import MlflowClient
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.exceptions import ConvergenceWarning

from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
from app.query import create_df_labels, get_full_feature_dataframe
from app.ETL import ETL_transform
from app.train_test import timeseries_manual_split
from app.prediction_metrics import get_roc_values
from app.prediction_service_models import Model_directory_info, Model_binaries

import datetime
import logging
import pickle
import warnings

# run and load logger object
logger = init_logger('prediction-service')
logger.log(logging.INFO, "starting ETL")

# connect to feature-service-db and get hour feature dataframe
database_service = 'feature-service'
db_url = connect_url(database_service)
session_feature_service = create_db_models(logger,
                                           db_url,
                                           database_service)
logger.log(logging.INFO, f"{database_service} session created")
# get hour feature dataframe
df_hour_data = get_full_feature_dataframe(logger,
                                          session_feature_service)
logger.log(logging.INFO, "hour dataframe ready")

# Connect to prediction-service-db and recreate labeled dataframe
database_service = 'prediction-service'
db_url = connect_url(database_service)
session_prediction_service = create_db_models(logger,
                                              db_url,
                                              database_service)
logger.log(logging.INFO, f"{database_service} session created")

# recreate labeled dataframe from labels id
labels_id_input = "labels_1704136177"
df_labels = create_df_labels(
    logger, session_prediction_service,
    df_hour_data, labels_id_input)

# ETL
# define model id
datetime_created = datetime.datetime.now()
model_id = f"model_{int(datetime_created.timestamp())}"
model_labels_id = labels_id_input

# train/test dataframe with inner join of hour_data features and labels
df = ETL_transform(df_hour_data, df_labels)

# train/test split
split_type = "timeseries_manual_split"
train_percent = 0.8
test_percent = 1 - train_percent

logger.log(logging.INFO, "starting train/test")
df_split = timeseries_manual_split(df, train_ratio=train_percent)

X_train = df_split[0]
y_train = df_split[1]
X_test = df_split[2]
y_test = df_split[3]
logger.log(logging.INFO, "train/test split complete")

# define SciKit learn model
#model = LogisticRegression()
model = RandomForestClassifier(n_estimators=100, random_state=42)
#model = GradientBoostingClassifier(n_estimators=300, learning_rate=1.0, max_depth=5, random_state=42)
# model = AdaBoostClassifier(DecisionTreeClassifier(max_depth=10), n_estimators=500, random_state=42)


prediction_type = "classification"
model_type = type(model).__name__
logger.log(logging.INFO, f"{model_type} model type for {model_id}")

# train
logger.log(logging.INFO, f"training {model_id} on {model_labels_id}")
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    model.fit(X_train, y_train)
    train_accuracy = model.score(X_train, y_train)

logger.log(
    logging.INFO,
    f"train model accuracy {train_accuracy} for {model_id}")

# test
logger.log(logging.INFO, f"testing {model_id}")
y_pred = model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_pred)
logger.log(
    logging.INFO,
    f"test model accuracy {test_accuracy} for {model_id}")

# classification report
classification_test_report = classification_report(
    y_test, y_pred, zero_division=0, output_dict=True)
classification_test_report_binary = pickle.dumps(classification_test_report)

# define model_binaries_id and save model as pickle
model_binaries_id = f"binary_{model_id}"

# confusion matrix
y_true = y_test
labels = [0, 1]
confusion_matrix = confusion_matrix(y_true, y_pred, labels=labels)
confusion_matrix_binary = confusion_matrix.tobytes()

# ROC score
roc_values = get_roc_values(X_test, y_test, model)
fpr = roc_values[0]
fpr_binary = fpr.tobytes()
tpr = roc_values[1]
tpr_binary = tpr.tobytes()
thresholds = roc_values[2]
thresholds_binary = thresholds.tobytes()
roc_auc = roc_values[3]
logger.log(logging.INFO, f"trained roc_auc for {model_id}: {roc_auc}")

###### commit to prediction-service-db ######
logger.log(
    logging.INFO, f"committing {model_id} and data to prediction-service-db")
try:
    new_model_directory_info = Model_directory_info(
        model_id=model_id,
        model_labels_id=model_labels_id,
        deployed_status=False,
        datetime_created=datetime_created,
        prediction_type=prediction_type,
        model_type=model_type,
        train_test_split_type=split_type,
        train_percent=train_percent,
        test_percent=test_percent,
        train_accuracy=train_accuracy,
        test_accuracy=test_accuracy,
        roc_auc=roc_auc
    )
    session_prediction_service.add(new_model_directory_info)

    new_model_binaries = Model_binaries(
        model_binaries_id=model_binaries_id,
        classification_test_report_binary=classification_test_report_binary,
        confusion_matrix_binary=confusion_matrix_binary,
        fpr_binary=fpr_binary,
        tpr_binary=tpr_binary,
        thresholds_binary=thresholds_binary,
        model_info_id=model_id
    )
    session_prediction_service.add(new_model_binaries)

    session_prediction_service.commit()
except:
    session_prediction_service.rollback()
    raise

finally:
    session_prediction_service.close()
logger.log(
    logging.INFO,
    f"successfully committed {model_id} to prediction-service-db")


###### upload to MLflow ######
# model params
params_dict = model.get_params()

# model metrics
metrics_dict = {
    "train_percent": train_percent,
    "test_percent": test_percent,
    "train_accuracy": train_accuracy,
    "test_accuracy": test_accuracy,
    "roc_auc": roc_auc
}

# set public CloudSQL database URI
mlflow.set_tracking_uri("http://34.31.62.132:5000/")

# start mlflow experiment run
with mlflow.start_run() as run:

    # log model
    mlflow.sklearn.log_model(model, model_id)

    # log model parameters and metrics
    mlflow.log_params(params_dict)
    mlflow.log_metrics(metrics_dict)

    # save run id and name
    run_id = run.info.run_id
    run_name = run.info.run_name
    print("Run ID:", run_id)
    print("Run Name:", run_name)

# end mlflow run
mlflow.end_run()

# define model URI and model name
model_uri = f"runs:/{run_id}/artifacts/model"
model_name = model_id
print("Model URI:", model_uri)
print("Model name:", model_name)

# name and register the model
registered_model_name = mlflow.register_model(model_uri, model_name)

# initialize an MLflow Client and stage
client = MlflowClient()

# set version
client.transition_model_version_stage(
    name=model_name, version=1, stage="Staging"
)

# set registered model tags
client.set_registered_model_tag(model_name, "prediction type", prediction_type)
client.set_registered_model_tag(model_name, "model type", model_type)
client.set_registered_model_tag(model_name, "split type", split_type)
client.set_registered_model_tag(model_name, "labels ID", model_labels_id)
