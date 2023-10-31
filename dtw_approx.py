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
        for i in range(0, len(qty_1)-len_5):
            distance, _ = fastdtw(qty_5, qty_1[i:i+len_5], dist=euclidean)
            if distance < min_distance:
                min_distance = distance
                most_similar = groupData1[['seller_no', 'product_no', 'warehouse_no']].iloc[0]
                matched = groupData1
                index_in_1 = i
    dtwed = {
        'seller_no': current_info[0],
        'product_no': current_info[1],
        'warehouse_no': current_info[2],
        'qty_new': qty_5,
        'qty_matched': qty_1[index_in_1:index_in_1+len_5],
        'dtw_distance': min_distance,
        'seller_no_matched': most_similar[0],
        'product_no_matched': most_similar[1],
        'warehouse_no_matched': most_similar[2]
    }
    output_data_frame = pd.concat([output_data_frame, pd.DataFrame(dtwed)])
output_data_frame.to_excel('dtw_result.xlsx', index=False)