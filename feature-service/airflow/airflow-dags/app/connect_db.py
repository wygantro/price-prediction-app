# ./app/connect_db.py

def connect_url(database_service):
    """
    Configures Postgres database URL connection string from environemnt
    variables and desired database service input.

    Args:
        database_service (str): database service string input

    Returns:
        str: URL string specific to SQLAlchemy
        format: 
        postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}
    """
    import os

    # check connection service
    if database_service == 'feature-service':
        db_name = os.environ["DB_FEATURE_SERVICE_NAME"]
    elif database_service == 'prediction-service':
        db_name = os.environ["DB_PREDICTION_SERVICE_NAME"]
    else:
        pass

    # get production environment variables
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]

    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"