import pandas as pd
import numpy as np
import scipy as sci
import math as math
import numpy.linalg as nla
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import dask.dataframe as dd
from utils import *

# Data Summary for 附件一
# dict sell_hist = {seller_no: {warehouse_no: {product_no: [(date, qty)]}}}
chunk_size = 100000
cache = pd.read_excel('./附件表/附件1-商家历史出货量表.xlsx', engine='openpyxl')
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
    
print(sell_hist)
# summary completed, elements stored in type dict sell_hist
for seller_no in sell_hist:
    for warehouse_no in sell_hist[seller_no]:
        for product_no in sell_hist[seller_no][warehouse_no]:
            product_data = sell_hist[seller_no][warehouse_no][product_no]
            # get product quantity for prediction
            product_quantity = [row[1] for row in product_data]
            feed = pd.Series(product_quantity)
            model = ARIMA(feed, order=(2, 0, 2))
            result = model.fit()
            # print(result.summary())
            preds = result.predict(start=len(feed), end=len(feed)+15)

            