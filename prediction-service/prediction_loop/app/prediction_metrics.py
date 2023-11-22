# ./app/prediction_metrics.py

def get_avg_prediction(logger, session, datetime_input):
    """
    """
    from app.prediction_service_models import Prediction_records
    import pandas as pd

    # get prediction_records data
    predictions_query = session.query(Prediction_records).filter(Prediction_records.lookahead_datetime > datetime_input).all()

    # get average classification
    classification_lst = [classification.prediction_value for classification in predictions_query]
    classification_avg = sum(classification_lst) / len(classification_lst)

    # get average predictions
    predictions_lst = [prediction.prediction_threshold for prediction in predictions_query]
    predictions_avg = sum(predictions_lst) / len(predictions_lst)

    return classification_avg, predictions_avg

def get_current_prediction(logger, session, selected_model_id, current_datetime):
    """
    """
    from app.prediction_service_models import Prediction_records
    import pandas as pd

    # get prediction_records data
    current_prediction = session.query(Prediction_records)\
        .filter(Prediction_records.model_prediction_id == selected_model_id)\
        .filter(Prediction_records.lookahead_datetime >= current_datetime)\
        .order_by(Prediction_records.lookahead_datetime.asc()).first()
        
    return current_prediction

####
def get_model_ranking(logger, session):
    """
    """
    from app.prediction_service_models import Model_directory_info
    
    model_ids = session.query(Model_directory_info.model_id, Model_directory_info.roc_auc).order_by(Model_directory_info.roc_auc.desc()).all()

    return model_ids

def get_roc_values(X_data, y_data, model):
    """
    """
    from sklearn.metrics import roc_curve, auc

    # ROC values
    y_pred_prob = model.predict_proba(X_data)[:, 1] # predict probabilities
    fpr, tpr, thresholds = roc_curve(y_data, y_pred_prob) # calculate ROC curve and area under the curve (auc)
    roc_auc = auc(fpr, tpr)

    return fpr, tpr, thresholds, roc_auc

def get_live_predictions_df(logger, session, selected_model_id, current_datetime=None):
    """
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
        'prediction_price_threshold': [price_threshold for _, price_threshold, _ in prediction_results],
        'predicted': [price_classification for _, _, price_classification in prediction_results]
        })
    
    # sort by datetime column
    df_predictions = df_predictions.sort_values(by='datetime', ascending=True)

    # update dtype for prediction_price_threshold
    df_predictions['prediction_price_threshold'] = df_predictions['prediction_price_threshold'].astype(float).round(2)

    if current_datetime:
        # slice dataframe for future predictions only
        df_predictions['datetime'] = pd.to_datetime(df_predictions['datetime'])
        df_predictions = df_predictions[df_predictions['datetime'] > current_datetime]

        # calculate hours until next prediction and format values
        df_predictions['next_prediction'] = df_predictions['datetime'] - current_datetime
        df_predictions['next_prediction'] = df_predictions['next_prediction'].dt.components['hours']
        df_predictions['next_prediction'] = df_predictions['next_prediction'].apply(lambda x: f"{x} hours")

        # reorder and name headers
        df_predictions = df_predictions.drop('datetime', axis=1)
        df_predictions = df_predictions[['next_prediction', 'prediction_price_threshold', 'predicted']]
        df_predictions = df_predictions.rename(columns={'next_prediction': 'next prediction', 'prediction_price_threshold': 'threshold', 'predicted': 'value'})

        return df_predictions

    return df_predictions

def get_live_predicted_results_df(logger, session, model_id):
    """
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
    
    # get prediction_records data
    prediction_results = session.query(
        Prediction_records.lookahead_datetime,
        Prediction_records.prediction_threshold,
        Prediction_records.prediction_value
        ).filter(Prediction_records.model_prediction_id == model_id)\
            .order_by(Prediction_records.lookahead_datetime.desc()).all()
    
    df_predictions = pd.DataFrame({
        'datetime': [dt for dt, _, _ in prediction_results],
        'prediction_price_threshold': [prediction_threshold for _, prediction_threshold, _ in prediction_results],
        'predicted': [prediction_value for _, _, prediction_value in prediction_results]
        })
    
    # merge
    df = df_actual_results.merge(df_predictions, on='datetime', how='inner')
    
    # update dtypes and round price columns
    df['predicted'] = df['predicted'].astype(int)
    df['actual_price'] = df['actual_price'].astype(float).round(2)
    df['prediction_price_threshold'] = df['prediction_price_threshold'].astype(float).round(2)

    # update 'predicted' dtype and calculate actual classification
    df['actual'] = (df['actual_price'] >= df['prediction_price_threshold']).astype(int)
    df['correct'] = (df['predicted'] == df['actual']).astype(int)

    # calculate TP, TN, FP, FN
    df['TP'] = ((df['predicted'] == 1) & (df['actual'] == 1)).astype(int)
    df['TN'] = ((df['predicted'] == 0) & (df['actual'] == 0)).astype(int)
    df['FP'] = ((df['predicted'] == 1) & (df['actual'] == 0)).astype(int)
    df['FN'] = ((df['predicted'] == 0) & (df['actual'] == 1)).astype(int)

    # calculate running_TPR, running_FPR, running_accuracy
    df['running_accuracy'] = df['correct'][::-1].cumsum() / (df.index + 1)
    df['running_TPR'] = df['TP'][::-1].cumsum() / (df['TP'][::-1].cumsum() + df['FN'][::-1].cumsum())
    df['running_FPR'] = df['FP'][::-1].cumsum() / (df['FP'][::-1].cumsum() + df['TN'][::-1].cumsum())

    # update datatype round/format values
    df['running_accuracy'] = df['running_accuracy'].astype(float).round(2).apply(lambda x: f"{x:,.2f}")
    df['running_TPR'] = df['running_TPR'].astype(float).round(2).apply(lambda x: f"{x:,.2f}")
    df['running_FPR'] = df['running_FPR'].astype(float).round(2).apply(lambda x: f"{x:,.2f}")

    # apply USD formatting to 'actual_price' and 'prediction_price_threshold' columns
    df['actual_price'] = df['actual_price'].apply(lambda x: f"${x:,.2f}")
    df['prediction_price_threshold'] = df['prediction_price_threshold'].apply(lambda x: f"${x:,.2f}")

    # sort by datetime column
    df = df.sort_values(by='datetime', ascending=False)

    # rename headers
    # df_predictions = df_predictions.rename(columns={'next_prediction': 'next prediction', 'prediction_price_threshold': 'threshold', 'predicted': 'value'})

    return df

def get_live_prediction_model_ranking(logger, session):
    """
    """
    from app.prediction_service_models import Model_directory
    from app.query import get_model_ids
    from app.prediction_metrics import get_live_predicted_results_df

    model_ids_list = get_model_ids(logger, session, labels_id_input=None)

    for model_id in model_ids_list:
        model_id_results = get_live_predicted_results_df(logger, session, model_id['value']).iloc[0]

    return model_ids_list