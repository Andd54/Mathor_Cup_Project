from utils import *
import numpy as np

# For this problem, our primary mindset is to use Kalman Filter
# The primary goal is to find similar data to the predicted data from file 5

data1 = pd.read_excel('附件表/附件1-商家历史出货量表.xlsx', engine = 'openpyxl')
data5 = pd.read_excel('附件表/附件5-新品历史出货量表.xlsx', engine = 'openpyxl')
data5.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
prediction = pd.read_excel('结果表/结果表1-预测结果表.xlsx', engine = 'openpyxl')
output_data_frame = pd.DataFrame()
# grouped by seller_no, product_no, warehouse_no
data5['qty'].interpolate(method='linear', inplace=True)
# convert date to datetime
data5['date'] = pd.to_datetime(data5['date'])
data1.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
data1['qty'].interpolate(method='linear', inplace=True)
data1['date'] = pd.to_datetime(data1['date'])
data1.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
data5.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
grouped_5 = data5.groupby(['seller_no', 'product_no', 'warehouse_no'])
grouped_1 = data1.groupby(['seller_no', 'product_no', 'warehouse_no'])
most_similar = {}
# filter data with extreme z-score
filtered_data_5 = filter(grouped_5)
filtered_data_1 = filter(grouped_1)
qty_5 = None
qty_1 = None
# dynamic time warping
for index_5, groupData5 in enumerate(filtered_data_5):
    groupData5['qty'].fillna(groupData5['qty'].mean(), inplace=True)
    qty_5 = groupData5['qty'].values.tolist()
    qty_5 = np.array([qty_5])
    qty_5 = qty_5.T
    len_5 = len(qty_5)
    # convert the data to valid format
    min_distance = float('inf')
    current_info = groupData5[['seller_no', 'product_no', 'warehouse_no']].iloc[0]
    matched = None
    index_in_1 = 0
    for index_1, groupData1 in enumerate(filtered_data_1):
        min_distance = float('inf')
        groupData1['qty'].fillna(groupData1['qty'].mean(), inplace=True)
        qty_1 = groupData1['qty'].values.tolist()
        qty_1 = np.array([qty_1])
        qty_1 = qty_1.T
        distance, _ = fastdtw(qty_5, qty_1, dist=euclidean)
        if distance < min_distance:
            min_distance = distance
            most_similar = groupData1[['seller_no', 'product_no', 'warehouse_no']].iloc[0]
            matched = groupData1

    # prediction based on matched and current groupData5
    # find the appropriate parameter for `q` `d` `p`
    # try to merge matched and current groupData5 as time series of qty
    merged_data = pd.concat([matched, groupData5])
    merge_data = merged_data.sort_values(by=['date'])
    merged_data = merged_data.groupby('date')['qty'].mean()
    # print(merged_data)
    # break
    merged_data.interpolate(method='linear', inplace=True)
    model = auto_arima(merged_data, seasonal=True, m=7)
    # generate model
    sarima_model = SARIMAX(merged_data, order=model.order, seasonal_order=model.seasonal_order)
    # fit model
    sarima_model_fit = sarima_model.fit()
    # predict future 15 days product selling quantity
    preds = sarima_model_fit.predict(start=len(matched), end=len(matched)+14)
    prediction = {
        'seller_no': current_info[0],
        'product_no': current_info[1],
        'warehouse_no': current_info[2],
        'date': pd.date_range(start='2023/05/16', periods=15, freq='D'),
        'forecast_qty': preds
    }
    output_data_frame=pd.concat([output_data_frame, pd.DataFrame(prediction)])
output_data_frame.to_excel('结果表/结果表2-预测结果表.xlsx', index=False)