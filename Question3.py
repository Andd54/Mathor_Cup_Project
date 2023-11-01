from utils import *

output_data_frame = pd.DataFrame()

data1 = pd.read_excel('附件表/附件1-商家历史出货量表.xlsx', engine = 'openpyxl')
data6 = pd.read_excel('附件表/附件6-促销期间商家出货量表.xlsx', engine = 'openpyxl')

data1 = data1.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
data1['qty'].interpolate(method='linear', inplace=True)
data1['date'] = pd.to_datetime(data1['date'])

data6 = data6.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
data6['qty'].interpolate(method='linear', inplace=True)
data6['date'] = pd.to_datetime(data6['date'])

grouped_1 = data1.groupby(['seller_no', 'product_no', 'warehouse_no'])
grouped_6 = data6.groupby(['seller_no', 'product_no', 'warehouse_no'])

ngrouped_1 = data1.groupby(['seller_no', 'product_no', 'warehouse_no']).ngroups
ngrouped_6 = data6.groupby(['seller_no', 'product_no', 'warehouse_no']).ngroups

print(f'grouped_1: {ngrouped_1}, grouped_6: {ngrouped_6}')

filtered_data_6 = filter(grouped_6)

# set the corresponding seller_no, product_no, warehouse_no as index

cumulative_11_11 = np.array([])

for index6, groupData6 in enumerate(filtered_data_6):
    groupData6['qty'].fillna(groupData6['qty'].mean(), inplace=True)
    qty_6 = groupData6['qty'].values.tolist()
    qty_6 = np.array([qty_6])
    qty_6 = qty_6.T
    qty_6 = qty_6.flatten()  # flatten the array
    len_6 = len(qty_6)
    series = pd.Series(qty_6, index = groupData6['date'])
    #STL decomposition
    stl_6 = STL(qty_6, period = 11, trend = 21, seasonal = 7)
    result_6 = stl_6.fit()
    name_6 = groupData6[['seller_no', 'product_no', 'warehouse_no']].iloc[0]
    seller_no_6, product_no_6, warehouse_no_6 = name_6[0], name_6[1], name_6[2]
    seasonal_6, trend_6, resid_6 = result_6.seasonal, result_6.trend, result_6.resid
    # find corresponding data 
    groupData1 = grouped_1.get_group((seller_no_6, product_no_6, warehouse_no_6))
    groupData1 = filter(grouped_1)[0]
    groupData1['qty'].fillna(groupData1['qty'].mean(), inplace=True)
    qty_1 = groupData1['qty'].values.tolist()
    qty_1 = np.array([qty_1])
    qty_1 = qty_1.T
    len_1 = len(qty_1)
    qty_1 = qty_1.flatten()
    # STL decomposition for data1
    stl_1 = STL(qty_1, period = len_1, trend = 317, seasonal = 7)
    result_1 = stl_1.fit()
    seasonal_1, trend_1, resid_1 = result_1.seasonal, result_1.trend, result_1.resid
    # calculate the shortest dtw distance between the seasonal_1 and seasonal_6
    min_distance = float('inf')
    index = 0
    season_1 = np.array([seasonal_1])
    season_6 = np.array([seasonal_6])
    for i in range(0, len(season_1)-len(season_6)):
        distance, _ = fastdtw(season_1[i:i+len(season_6)].flatten(), season_6.flatten(), dist=euclidean)
        if distance < min_distance:
            min_distance = distance
            index = i
    trend_1[index:index+len(trend_6)] = trend_6
    Y_1 = seasonal_1 + trend_1 + resid_1
    # start SARIMAX model with updated trend_1
    model = auto_arima(Y_1, seasonal=True, m=7)
    sarima_model = SARIMAX(Y_1, order=model.order, seasonal_order=model.seasonal_order)
    sarima_model_fit = sarima_model.fit()
    # predict future 35 days product selling quantity
    preds = sarima_model_fit.predict(start=len(Y_1), end=len(Y_1)+34)
    preds = preds[-20:] 
    # get the last 20 elements in preds
    # update output_data_frame
    date_range = pd.date_range(start='2023/06/01', periods=20, freq='D')
    prediction ={
        'seller_no': seller_no_6,
        'product_no': product_no_6,
        'warehouse_no': warehouse_no_6,
        'date': date_range,
        'forecast_qty': preds
    }
    output_data_frame = pd.concat([output_data_frame, pd.DataFrame(prediction)])
output_data_frame.to_excel('结果表/结果表3-预测结果表.xlsx', index=False)
    