# ./app/binary_classification.py

def binary_classification_lookahead(timeseries, lookahead=12, threshold_percent=2.0):
    """
    Transforms timeseries price values into binary labels based on
    future percent change.

    Args:
        timeseries (list): The time series data.
        lookahead (int): How many time steps to look ahead for the
        percent change.
        threshold_percent (float): The threshold for percent change.

    Returns:
        list: list of percent change values and list of binary labels.
    """

    n = len(timeseries)
    labels_value = [0] * n

    # calculate percent change
    for i in range(len(labels_value)):
        if i + lookahead < len(timeseries):
            current_value = timeseries[i]
            future_value = timeseries[i + lookahead]
            percent_change = (
                (future_value - current_value) / current_value) * 100.0
            labels_value[i] = percent_change
        else:
            labels_value[i] = 0

    # classify percent change threshold
    labels_binary = []
    for value in labels_value:
        if value >= threshold_percent:
            labels_binary.append(1)
        else:
            labels_binary.append(0)

    return labels_value, labels_binary


def datetime_classified_lst(labels, datetime_input):
    """
    Sorts list of datetime values to include only labeled datetimes
    based on indices of labeled price change input.

    Args:
        labels (list): Labeled lookahead price change values
        datetime_input (list): List of datetime values corresponding
        by index position

    Returns:
        list: list of only datetime values with labels
    """
    import datetime

    # define datetime classified list and append values
    datetime_classified_lst = []
    for i in range(len(labels)):
        if labels[i] == 1:
            datetime_classified_lst.append(datetime.datetime.strptime(
                datetime_input[i], "%Y-%m-%d %H:%M:%S"))
            
    return datetime_classified_lst


def datetime_classified_ranges(labels_list, datetime_lst):
    """
    Creates a list of tuples defining datetime range pairs of labeled
    price data.

    Args:
        labels_list (list): Labeled lookahead price change values
        datetime_lst (list): List of datetime values corresponding by
        index position

    Returns:
        list: list of tuples defining datetime range pairs for the
        price labels
    """

    # default return empty list
    if not labels_list:
        return []
    
    # define labels range list and append start/end datetime tuples
    ranges = []
    start_idx = None
    for i, value in enumerate(labels_list):
        if value == 1 and (i == 0 or labels_list[i-1] == 0):
            start_idx = i
        elif value == 0 and labels_list[i-1] == 1:
            ranges.append((datetime_lst[start_idx], datetime_lst[i - 1]))
            start_idx = None
        elif i == len(labels_list) - 1 and value == 1:
            ranges.append((datetime_lst[start_idx], datetime_lst[i]))

    return ranges
