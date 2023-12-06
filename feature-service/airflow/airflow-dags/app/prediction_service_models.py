# ./app/prediction_service_models.py

from sqlalchemy import Column, DateTime, Numeric, ForeignKey, String, LargeBinary, Boolean, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Labels_directory(Base):
    __tablename__ = 'labels_directory'

    labels_id = Column(String(), primary_key=True)

    datetime_created = Column(DateTime())
    target_output = Column(String())
    lookahead_value = Column(Integer())
    percent_change_threshold = Column(Float())
    labels_start_datetime = Column(DateTime())
    labels_end_datetime = Column(DateTime())

    # one-to-many relationship with model_directory
    model_info = relationship("Model_directory_info", back_populates="labels")


class Model_directory_info(Base):
    __tablename__ = 'model_directory_info'

    model_id = Column(String(), primary_key=True)
    model_labels_id = Column(String, ForeignKey('labels_directory.labels_id'))

    deployed_status = Column(Boolean, default=False)
    datetime_created = Column(DateTime())
    prediction_type = Column(String())
    model_type = Column(String())
    train_test_split_type = Column(String())
    train_percent = Column(Float())
    test_percent = Column(Float())
    train_accuracy = Column(Float())
    test_accuracy = Column(Float())
    roc_auc = Column(Float())
    running_accuracy = Column(Float())
    running_TPR = Column(Float())
    running_FPR = Column(Float())

    # many-to-one relationship with labels_directory
    labels = relationship("Labels_directory", back_populates="model_info")
    # one-to-one relationship with model_objects
    model_binaries = relationship(
        "Model_binaries", back_populates="model_directory_info", uselist=False)
    # one-to-many relationship with prediction_records
    prediction_records_info = relationship(
        "Prediction_records", back_populates="model")


class Model_binaries(Base):
    __tablename__ = 'model_binaries'

    model_binaries_id = Column(String(), primary_key=True)
    model_info_id = Column(String(), ForeignKey(
        'model_directory_info.model_id'), unique=True)

    model_binary = Column(LargeBinary())
    classification_test_report_binary = Column(LargeBinary())
    confusion_matrix_binary = Column(LargeBinary())
    fpr_binary = Column(LargeBinary())
    tpr_binary = Column(LargeBinary())
    thresholds_binary = Column(LargeBinary())

    # one-to-one relationship with model_directory
    model_directory_info = relationship(
        "Model_directory_info", back_populates="model_binaries")


class Prediction_records(Base):
    __tablename__ = 'prediction_records'

    prediction_entry_id = Column(String(), primary_key=True)
    model_prediction_id = Column(
        String, ForeignKey('model_directory_info.model_id'))

    prediction_id = Column(String())
    datetime_entry = Column(DateTime())
    current_datetime = Column(DateTime())
    current_price = Column(Numeric())
    percent_change_threshold = Column(Numeric())
    lookahead_steps = Column(Numeric())
    lookahead_datetime = Column(DateTime())
    prediction_threshold = Column(Numeric())
    prediction_value = Column(Numeric())
    prediction_classification_value = Column(Numeric())
    prediction_regression_value = Column(Numeric())
    prediction_timeseries_value = Column(Numeric())

    # many-to-one relationship with labels_directory
    model = relationship("Model_directory_info",
                         back_populates="prediction_records_info")
