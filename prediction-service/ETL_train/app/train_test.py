# ./app/train_test.py

def timeseries_manual_split(df, train_ratio=0.8):
    """
    """
    
    # define feature inputs (X) and output (y)
    X = df.drop(['hour_datetime_id', 'labels_values', 'labels_binary'], axis=1)
    y = df['labels_binary']
    
    # resize dataframes into training set
    train_size = int(train_ratio * len(df))
    
    # split into train and test sets where test size is 1 - train_size_percent
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    return X_train, y_train, X_test, y_test

def datetime_train_test_ranges(labels_datetime_list, train_ratio=0.8):
    """
    """
    import pandas as pd

    # resize dataframes into training set
    train_size = int(train_ratio * len(labels_datetime_list))
    
    # split into train and test sets where test size is 1 - train_size_percent
    train_dt, test_dt = labels_datetime_list[:train_size], labels_datetime_list[train_size:]
    datetime_train_test_ranges_list = []

    # Convert back to datetime
    datetime_train_test_ranges_list.append((train_dt[0], train_dt[-1], "lightblue"))
    datetime_train_test_ranges_list.append((test_dt[0], test_dt[-1], "lightyellow"))

    # Find the halfway point for train and test regions
    train_halfway_timestamp = (train_dt[-1] - train_dt[0])/2 + train_dt[0]
    test_halfway_timestamp = (test_dt[-1] - test_dt[0])/2 + test_dt[0]

    return datetime_train_test_ranges_list, train_halfway_timestamp, test_halfway_timestamp


