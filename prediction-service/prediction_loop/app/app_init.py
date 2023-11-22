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


def check_db_tables(logger, db_url):
    """
    Connects with database and tests for successful connection and 
    tables.

    Args:
        logger (logging.Logger): Initialized logger object
        db_url (str): Database connection string for SQLAlchemy

    Returns:
        bool: Returns 'False' if tables do not exist. Returns 'True' if
        tables exist.
    """
    from sqlalchemy import create_engine, inspect, text

    try:
        # check connection and create engine
        engine = create_engine(db_url)
        connection = engine.connect()
        result = connection.execute(text("SELECT version()"))
        logger.log(logging.INFO, f"database exists: {result.fetchone()[0]}")

        # inspect database for tables
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        if len(table_names) == 0:
            logger.log(logging.INFO, "tables do not exist")
            return False
        else:
            logger.log(logging.INFO, "tables exist")
            for table_name in table_names:
                logger.log(logging.INFO, f"table: {table_name}")
            return True

    except:
        logger.log(
            logging.INFO, "database does not exist or connection info invalid")


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
        from app.feature_service_models import Base
    elif database_service == 'prediction-service':
        from app.prediction_service_models import Base
    else:
        pass

    # create database engine
    logger.log(logging.INFO, "creating connection engine")
    engine = create_engine(db_url)

    # create tables with Base from models
    logger.log(logging.INFO, "creating model tables")
    Base.metadata.create_all(engine)

    # define session object and return session
    logger.log(logging.INFO, "defining and returning session object")
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
