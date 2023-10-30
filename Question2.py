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
grouped_5 = data5.groupby(['seller_no', 'product_no', 'warehouse_no'])
grouped_1 = data1.groupby(['seller_no', 'product_no', 'warehouse_no'])

# filtered_data_5 = filter(grouped_5)
# filtered_data_1 = filter(grouped_1)
qty_1 = []
for group_name, group_data in grouped_1:
    time_series = group_data['qty']
    qty_1.append(time_series)
qty_5 = []
for group_name, group_data in grouped_5:
    time_series = group_data['qty']
    qty_5.append(time_series)

# pad the shorter sequences with zeros
max_len = max(len(qty_1), len(qty_5))
for i in range(len(qty_1)):
    qty_1[i] = np.pad(qty_1[i], (0, max_len - len(qty_1[i])), 'constant')
for i in range(len(qty_5)):
    qty_5[i] = np.pad(qty_5[i], (0, max_len - len(qty_5[i])), 'constant')

# fastdtw
distance, path = fastdtw(qty_5, qty_1, dist=euclidean)
# similar = find_most_similar(qty_5, qty_1)
# print(similar)
print("distance: {}".format(distance)) 
print("path: {}".format(path))