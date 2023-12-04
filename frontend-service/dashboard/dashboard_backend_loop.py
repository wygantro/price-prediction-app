# dashboard_backend_loop.py

from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
from app.feature_service_models import Hour_price_data
from app.query import current_datetime, get_full_feature_dataframe

import logging
from sqlalchemy import desc
import time


def dashboard_backend_loop(initialize=False):
    """
    Dashboard backend scheduling loop to call query functions and update
    volume dataframes on hourly basis.

     Args:
        initialize (bool): Initialization boolean input

    Returns: None
    """
    # run and load logger object
    logger = init_logger('frontend-service')

    # db url connection and create engine
    database_service = 'feature-service'
    db_url = connect_url(database_service)
    session = create_db_models(logger, db_url, database_service)
    logger.log(logging.INFO, f"{database_service} session created")

    logger.log(logging.INFO, "getting latest database datetime record")
    latest_datetime_record = session.query(Hour_price_data).order_by(
        desc(Hour_price_data.hour_datetime_id)).first()
    hour_datetime_id = latest_datetime_record.hour_datetime_id
    logger.log(logging.INFO, f"initial hour datetime ID: {hour_datetime_id}")

    df = get_full_feature_dataframe(logger, session)
    df.to_csv('./dataframes/hour_data.csv', index=False)
    logger.log(
        logging.INFO,
        f"initial hour dataframe update and saved: {hour_datetime_id}")

    if not initialize:
        while True:
            # check and update hour ID
            if hour_datetime_id != current_datetime()[1]:
                hour_datetime_id = current_datetime()[1]
                df = get_full_feature_dataframe(logger, session)
                df.to_csv('./dataframes/hour_data.csv', index=False)
                logger.log(
                    logging.INFO,
                    f"hour dataframe updated and saved: {hour_datetime_id}")
            else:
                logger.log(logging.INFO, f"no data update")
                logger.log(logging.INFO, "query loop complete")
            time.sleep(60)

dashboard_backend_loop()