# ./app/train_test.py

def timeseries_manual_split(df, train_ratio=0.8):
    """
    Splits timeseries labeled dataframe into test and train set and
    returns X, y train and test dataframes.

    Args:
         df (pandas.core.frame.DataFrame): training dataframe
         train_ratio (float): train ratio

    Returns:
         pandas.core.frame.DataFrame: trained feature inputs
         pandas.core.frame.DataFrame: trained results
         pandas.core.frame.DataFrame: test feature inputs
         pandas.core.frame.DataFrame: test results
    """

    # define feature inputs and output and split
    X = df.drop(['hour_datetime_id', 'labels_values', 'labels_binary'], axis=1)
    y = df['labels_binary']
    train_size = int(train_ratio * len(df))

    # split into train and test sets where test size is 1 - train_size_percent
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    return X_train, y_train, X_test, y_test


def datetime_train_test_ranges(labels_datetime_list, train_ratio=0.8):
    """
    Splits timeseries labeled list dataframe into test and train set.

    Args:
         df (list): Initialized logger object
         train_ratio (float): train ratio

    Returns:
         list: list of datetimes for test range
         datetime.datetime: train halfway timestamp
         datetime.datetime: test halfway timestamp
    """

    # resize dataframes into training set and split
    train_size = int(train_ratio * len(labels_datetime_list))
    train_dt, test_dt = labels_datetime_list[:train_size],
    labels_datetime_list[train_size:]
    datetime_train_test_ranges_list = []

    # convert back to datetime
    datetime_train_test_ranges_list.append(
        (train_dt[0], train_dt[-1], "lightblue"))
    datetime_train_test_ranges_list.append(
        (test_dt[0], test_dt[-1], "lightyellow"))

    # find the halfway point for train and test regions
    train_halfway_timestamp = (train_dt[-1] - train_dt[0])/2 + train_dt[0]
    test_halfway_timestamp = (test_dt[-1] - test_dt[0])/2 + test_dt[0]

    return datetime_train_test_ranges_list, train_halfway_timestamp, test_halfway_timestamp
