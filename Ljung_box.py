from utils import *

data1 = pd.read_excel('附件表/附件1-商家历史出货量表.xlsx', engine = 'openpyxl')

data1 = data1.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
data1['qty'].interpolate(method='linear', inplace=True)
data1['date'] = pd.to_datetime(data1['date'])
grouped_1 = data1.groupby(['seller_no', 'product_no', 'warehouse_no'])
filtered_data_1 = filter(grouped_1)

for index, groupData in enumerate(filtered_data_1):
    groupData['qty'].fillna(groupData['qty'].mean(), inplace=True)
    qty = np.array(groupData['qty'].values.tolist()).flatten()
    gp_time_series = pd.Series(qty, index=groupData['date'])
    ljung_box_results = acorr_ljungbox(gp_time_series, lags=[10], return_df=True)
    curr_info = groupData[['seller_no', 'product_no', 'warehouse_no']].iloc[0]
    print(f'current_info:\n{curr_info[0]} {curr_info[1]} {curr_info[2]}\n{ljung_box_results}\n\n')
    