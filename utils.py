import pandas as pd
import numpy as np
from scipy import stats
import math as math
import numpy.linalg as nla
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error
from pmdarima import auto_arima
import re
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

def extract_number(s):
    match = re.search(r'\d+', s)
    if match:
        number = int(match.group())
        return number
    else:
        return None
def xlsx_extract(cache):
    sell_hist = {}
    for _, row in cache.iterrows():
        seller_no = row['seller_no']
        product_no = row['product_no']
        warehouse_no = row['warehouse_no']
        # seller_no and product_no and warehouse_no are all strings
        date = row['date']
        qty = row['qty']
        # print(date, qty)
        if seller_no not in sell_hist:
            sell_hist[seller_no] = {}
        if warehouse_no not in sell_hist[seller_no]:
            sell_hist[seller_no][warehouse_no] = {}
        if product_no not in sell_hist[seller_no][warehouse_no]:
            sell_hist[seller_no][warehouse_no][product_no] = []
        sell_hist[seller_no][warehouse_no][product_no].append([date, qty])

    for seller_no in sell_hist:
        for warehouse_no in sell_hist[seller_no]:
            for product_no in sell_hist[seller_no][warehouse_no]:
                #sort by date
                sell_hist[seller_no][warehouse_no][product_no].sort(key = lambda x: x[0])
    return sell_hist

# BEGIN: kalman_filter
from pykalman import KalmanFilter
def filter(grouped):
    result = []
    for group_name, group_data in grouped:
        # calculate z-score
        group_data['z_score'] = np.abs(stats.zscore(group_data['qty']))
        # if z_score is greater than 3, replace it with NaN
        group_data.loc[group_data['z_score'] > 3, 'qty'] = np.nan
        # interpolate NaN values
        group_data['qty'].interpolate(method='linear', inplace=True)
        # drop z_score column
        group_data = group_data.drop(columns='z_score')  
        # append to filtered_data
        result.append(group_data)
    return result  
  
def find_most_similar(new_series, historical_data):
    min_distance = float('inf')
    most_similar_series = None
    
    # interpolate historical data to fill in missing values
    interpolated_data = []
    for series in historical_data:
        series = pd.DataFrame(series, columns=['date', 'qty']).set_index('date')
        series.index = pd.to_datetime(series.index)  # convert index to DatetimeIndex
        if series.isna().all().item():  # skip if series is empty or contains only missing values
            continue
        series = series.resample('D').asfreq().interpolate(method='linear')
        interpolated_data.append(series['qty'].values)
    
    for historical_series in interpolated_data:
        distance, _ = fastdtw(new_series, historical_series, dist=euclidean)
        if distance < min_distance:
            min_distance = distance
            most_similar_series = historical_series
            
    return most_similar_series
