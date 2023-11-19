from utils import *
# utilities

# Data Summary
chunk_size = 100000
data1 = pd.read_excel('附件表/附件1-商家历史出货量表.xlsx', engine = 'openpyxl')
data2 = pd.read_excel('附件表/附件2-商品信息表.xlsx', engine = 'openpyxl')
data3 = pd.read_excel('附件表/附件3-商家信息表.xlsx', engine = 'openpyxl')
data4 = pd.read_excel('附件表/附件4-仓库信息表.xlsx', engine = 'openpyxl')
data = pd.merge(data1,data2)
data = pd.merge(data,data3)
data = pd.merge(data,data4)
data = data.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])

output_data_frame = pd.DataFrame()
data['qty'].interpolate(method='linear', inplace=True)
# convert date to datetime
data['date'] = pd.to_datetime(data['date'])
# grouped by seller_no, product_no, warehouse_no
grouped = data.groupby(['seller_no', 'product_no', 'warehouse_no'])
# summary completed, elements stored in type dict sell_hist
# get product quantity for prediction
# apply z-score filter
filtered_data = filter(grouped)
i = 0;
# prediction
for index, groupData in enumerate(filtered_data):
    # fill NaN with mean
    groupData['qty'].fillna(groupData['qty'].mean(), inplace=True)
    # find the appropriate parameter for `q` `d` `p`
    model = auto_arima(groupData['qty'].values, seasonal=True, m=7)
    # generate model
    sarima_model = SARIMAX(groupData['qty'].values, order=model.order, seasonal_order=model.seasonal_order)
    # fit model
    sarima_model_fit = sarima_model.fit()
    # predict future 15 days product selling quantity
    preds = sarima_model_fit.predict(start=len(groupData), end=len(groupData)+14)
    group_name = groupData[['seller_no', 'product_no', 'warehouse_no']].iloc[0]
    # generate date range
    date_range = pd.date_range(start='2023/05/16', periods=15, freq='D')
    # pack prediction for concat
    prediction = {
        'seller_no': group_name[0],
        'product_no': group_name[1],
        'warehouse_no': group_name[2],
        'date': date_range,
        'forecast_qty': preds
    }
    # if i == 8:
    #     ts = pd.Series(groupData['qty'].values, index=groupData['date'])
    #     pred = pd.Series(preds, index=date_range)
    #     plt.plot(ts, color = 'blue', label = 'Original')
    #     plt.plot(pred, color='orange', label='Predicted')
    #     plt.title(f'{group_name[0]}-{group_name[1]}-{group_name[2]} Prediction')
    #     plt.legend()
    #     plt.show()
    #     break
    # update output_data_frame
    output_data_frame = pd.concat([output_data_frame, pd.DataFrame(prediction)])
    # i += 1
# output_data_frame.to_excel('结果表/结果表1-预测结果表.xlsx', index=False)