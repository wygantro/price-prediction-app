# ./app/app_init.py

import logging


def init_logger(database_service):
    """
    Initializes logger settings and returns logger object specific to 
    application service.

    Args: None

    Returns:
        logging.Logger: Application logger object from logging module.
    """
    import sys

    # initialize logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # database_service = 'feature_service'
    formatter = logging.Formatter(
        f"[%(asctime)s] %(levelname)s:{database_service}:%(lineno)d:%(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(f"./logs/{database_service}-logger.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def create_db_models(logger, db_url, database_service):
    """
    Connects with database and returns session object for database 
    interaction.

    Args:
        logger (logging.Logger): Initialized logger object
        db_url (str): Database connection string for SQLAlchemy

    Returns:
        sqlalchemy.orm.session.Session: Returns SQLAlchemy session 
        object.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    if database_service == 'feature-service':
        from app.feature_service_models import Base as Base_feature_service

        # create database engine
        logger.log(logging.INFO, "creating connection engine")
        engine = create_engine(db_url)

        # create tables with Base object from models
        logger.log(logging.INFO, "creating model tables")
        Base_feature_service.metadata.create_all(engine)

        # define and return session object
        logger.log(logging.INFO, "defining and returning session object")
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    elif database_service == 'prediction-service':
        from app.prediction_service_models import Base as Base_prediction_service

        # create database engine
        logger.log(logging.INFO, "creating connection engine")
        engine = create_engine(db_url)

        # create tables with Base object from models
        logger.log(logging.INFO, "creating model tables")
        Base_prediction_service.metadata.create_all(engine)

        # define and return session object
        logger.log(logging.INFO, "defining and returning session object")
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    elif database_service == 'mlflow':
        # create database engine
        logger.log(logging.INFO, "creating connection engine")
        engine = create_engine(db_url)

        # define and return session object
        logger.log(logging.INFO, "defining and returning session object")
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    else:
        pass
