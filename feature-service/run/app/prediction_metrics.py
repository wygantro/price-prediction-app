# ./app/prediction_metrics.py

def get_avg_prediction(logger, session, datetime_input):
    """
    Calculates average classfication and prediction values for all
    prediction entries in database greater than input datetime value.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        datetime_input (datetime.datetime): datetime query filter

    Returns:
        float: average of classified values
        float: average of prediction values
    """
    from app.prediction_service_models import Prediction_records

    # query prediction data
    predictions_query = session.query(Prediction_records).filter(
        Prediction_records.lookahead_datetime > datetime_input).all()

    # average classification and prediction values
    classification_lst = [
        classification.prediction_value for classification in predictions_query]
    classification_avg = sum(classification_lst) / len(classification_lst)
    predictions_lst = [
        prediction.prediction_threshold for prediction in predictions_query]
    predictions_avg = sum(predictions_lst) / len(predictions_lst)

    return classification_avg, predictions_avg


def get_current_prediction(logger, session, selected_model_id, current_datetime):
    """
    Query and return current prediction values for given model ID.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        selected_model_id (str): Selected model ID
        current_datetime (datetime.datetime): datetime query filter

    Returns:
        sqlalchemy.orm.query.Query: SQLAlchemy query object
    """
    from app.prediction_service_models import Prediction_records

    # get prediction_records data
    current_prediction = session.query(Prediction_records)\
        .filter(Prediction_records.model_prediction_id == selected_model_id)\
        .filter(Prediction_records.lookahead_datetime >= current_datetime)\
        .order_by(Prediction_records.lookahead_datetime.asc()).first()

    return current_prediction


def get_model_ranking(logger, session):
    """
    Query and return deployed model ranking for roc_auc

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object

    Returns:
        list: List of tuples
    """
    from app.prediction_service_models import Model_directory_info

    # query and rank a list of tuples for model ID and roc_auc
    model_ids = session.query(Model_directory_info.model_id,
                              Model_directory_info.roc_auc).order_by(
        Model_directory_info.roc_auc.desc()).all()

    return model_ids


def get_roc_values(X_data, y_data, model):
    """
    Calculate roc curve values for trained classification model.

    Args:
        X_data (list): Actual results
        y_data (list): Predicted results
        model (sklearn.linear_model): Trained classifier

    Returns:
        float: fpr value
        float: tpr value
        float: roc curve threshold value
        float: roc_auc value
    """
    from sklearn.metrics import roc_curve, auc

    # define and call roc_curve functions
    y_pred_prob = model.predict_proba(X_data)[:, 1]
    fpr, tpr, thresholds = roc_curve(y_data, y_pred_prob)
    roc_auc = auc(fpr, tpr)

    return fpr, tpr, thresholds, roc_auc


def get_live_roc_values(y_actual, y_predicted):
    """
    Calculate live roc curve values for running predicted and actual
    values.

    Args:
        y_actual (list): Actual results
        y_predicted (list): Predicted results

    Returns:
        float: fpr value
        float: tpr value
        float: roc curve threshold value
        float: roc_auc value
    """
    from sklearn.metrics import roc_curve, auc

    # define and call roc_curve functions
    fpr, tpr, thresholds = roc_curve(y_actual, y_predicted)
    roc_auc = auc(fpr, tpr)

    return fpr, tpr, thresholds, roc_auc


def get_live_predictions_df(logger, session, selected_model_id, current_datetime=None):
    """
    Query and return current prediction values for given model ID.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        selected_model_id (str): Selected model ID
        current_datetime (datetime.datetime): datetime query filter

    Returns:
        pandas.core.frame.DataFrame: live predictions dataframe
    """

    from app.prediction_service_models import Prediction_records
    import pandas as pd

    # get prediction_records data
    prediction_results = session.query(
        Prediction_records.lookahead_datetime,
        Prediction_records.prediction_threshold,
        Prediction_records.prediction_value
    ).filter(Prediction_records.model_prediction_id == selected_model_id)\
        .order_by(Prediction_records.lookahead_datetime.desc()).all()

    df_predictions = pd.DataFrame({
        'datetime': [dt for dt, _, _ in prediction_results],
        'prediction_price_threshold': [price_threshold for
                                       _, price_threshold, _ in prediction_results],
        'predicted': [price_classification for
                      _, _, price_classification in prediction_results]
    })

    df_predictions = df_predictions.sort_values(by='datetime', ascending=True)
    df_predictions['prediction_price_threshold'] = df_predictions['prediction_price_threshold']\
        .astype(float).round(2)

    if current_datetime:
        # slice for future predictions only
        df_predictions['datetime'] = pd.to_datetime(df_predictions['datetime'])
        df_predictions = df_predictions[df_predictions['datetime']
                                        > current_datetime]

        # calculate hours until next prediction and format values
        df_predictions['next_prediction'] = df_predictions['datetime'] - \
            current_datetime
        df_predictions['next_prediction'] = df_predictions['next_prediction']\
            .dt.components['hours']
        df_predictions['next_prediction'] = df_predictions['next_prediction'].apply(
            lambda x: f"{x} hours")
        
        # reorder/format and name headers
        df_predictions['predicted'] = df_predictions['predicted'].replace({0: 'down', 1: 'up'})
        df_predictions['prediction_price_threshold'] = df_predictions['prediction_price_threshold']\
            .apply(lambda x: f"${x:,.2f}")
        df_predictions = df_predictions.drop('datetime', axis=1)
        df_predictions = df_predictions[[
            'next_prediction', 'prediction_price_threshold', 'predicted']]
        df_predictions = df_predictions.rename(
            columns={'next_prediction': 'timeframe',
                     'prediction_price_threshold': 'threshold',
                     'predicted': 'prediction'})

        return df_predictions

    return df_predictions


def get_live_predicted_results_df(logger, session, model_id):
    """
    Query and return live predicted results history for given model ID.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        model_id (str): Selected model ID

    Returns:
        pandas.core.frame.DataFrame: live predictions dataframe
    """
    from app.prediction_service_models import Prediction_records
    import pandas as pd

    # get actual predicted results
    actual_results = session.query(
        Prediction_records.current_datetime,
        Prediction_records.current_price
    ).filter(Prediction_records.model_prediction_id == model_id)\
        .order_by(Prediction_records.current_datetime.desc()).all()

    df_actual_results = pd.DataFrame({
        'datetime': [dt for dt, _ in actual_results],
        'actual_price': [price for _, price in actual_results]
    })

    # get prediction records data
    prediction_results = session.query(
        Prediction_records.lookahead_datetime,
        Prediction_records.prediction_threshold,
        Prediction_records.prediction_value
    ).filter(Prediction_records.model_prediction_id == model_id)\
        .order_by(Prediction_records.lookahead_datetime.desc()).all()

    df_predictions = pd.DataFrame({
        'datetime': [dt for dt, _, _ in prediction_results],
        'prediction_price_threshold': [prediction_threshold for _,
                                       prediction_threshold, _ in prediction_results],
        'predicted': [prediction_value for _, _, prediction_value in prediction_results]
    })
    df = df_actual_results.merge(df_predictions, on='datetime', how='inner')

    # update dtypes and round price columns
    df['predicted'] = df['predicted'].astype(int)
    df['actual_price'] = df['actual_price'].astype(float).round(2)
    df['prediction_price_threshold'] = df['prediction_price_threshold'].astype(
        float).round(2)

    # update 'predicted' dtype and calculate actual classification
    df['actual'] = (df['actual_price'] >=
                    df['prediction_price_threshold']).astype(int)
    df['correct'] = (df['predicted'] == df['actual']).astype(int)

    # calculate TP, TN, FP, FN
    df['TP'] = ((df['predicted'] == 1) & (df['actual'] == 1)).astype(int)
    df['TN'] = ((df['predicted'] == 0) & (df['actual'] == 0)).astype(int)
    df['FP'] = ((df['predicted'] == 1) & (df['actual'] == 0)).astype(int)
    df['FN'] = ((df['predicted'] == 0) & (df['actual'] == 1)).astype(int)

    # calculate running_TPR, running_FPR, running_accuracy
    df['running_accuracy'] = df['correct'][::-1].cumsum() / (df.index + 1)
    df['running_TPR'] = df['TP'][::-1].cumsum() / (df['TP'][::-1].cumsum() +
                                                   df['FN'][::-1].cumsum())
    df['running_FPR'] = df['FP'][::-1].cumsum() / (df['FP'][::-1].cumsum() +
                                                   df['TN'][::-1].cumsum())

    # update datatype round/format values
    df['running_accuracy'] = df['running_accuracy'].astype(
        float).round(2).apply(lambda x: f"{x:,.2f}")
    df['running_TPR'] = df['running_TPR'].astype(
        float).round(2).apply(lambda x: f"{x:,.2f}")
    df['running_FPR'] = df['running_FPR'].astype(
        float).round(2).apply(lambda x: f"{x:,.2f}")
    df['actual_price'] = df['actual_price'].apply(lambda x: f"${x:,.2f}")
    df['prediction_price_threshold'] = df['prediction_price_threshold'].apply(
        lambda x: f"${x:,.2f}")

    df = df.sort_values(by='datetime', ascending=False)

    return df


def get_live_prediction_model_ranking(logger, session):
    """
    Query and return live prediction model ranking results.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object

    Returns:
        list: list of model ID strings
    """
    from app.prediction_service_models import Model_directory
    from app.query import get_model_ids
    from app.prediction_metrics import get_live_predicted_results_df

    # get model IDs and rank
    model_ids_list = get_model_ids(logger, session, labels_id_input=None)

    for model_id in model_ids_list:
        model_id_results = get_live_predicted_results_df(
            logger, session, model_id['value']).iloc[0]

    return model_ids_list
