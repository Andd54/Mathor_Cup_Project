from utils import *

data1 = pd.read_excel('附件表/附件1-商家历史出货量表.xlsx', engine = 'openpyxl')
data2 = pd.read_excel('附件表/附件2-商品信息表.xlsx', engine = 'openpyxl')
data3 = pd.read_excel('附件表/附件3-商家信息表.xlsx', engine = 'openpyxl')
data4 = pd.read_excel('附件表/附件4-仓库信息表.xlsx', engine = 'openpyxl')
data = pd.merge(data1,data2)
data = pd.merge(data,data3)
data = pd.merge(data,data4)
data = data.sort_values(by=['seller_no', 'product_no', 'warehouse_no', 'date'])
data['qty'].interpolate(method='linear', inplace=True)

seller_dict = {f'seller_{i}': i for i in range(38)}
product_dict = {f'product_{i}': i for i in range(2001)}
warehouse_dict = {f'wh_{i}': i for i in range(60)}
seller_category_dict = {'宠物健康':0,'宠物生活':1,'厨具':2,'电脑、办公':3,'服饰内衣':4,'个人护理':5,'家居日用':6,'家具':7,'家用电器':8,'家装建材':9,'居家生活':10,'美妆护肤':11,'食品饮料':12,'手机通讯':13,'数码':14,'玩具乐器':15,'医疗保健':16}
inventory_category_dict = {'A':0,'B':1,'C':2,'D':3}
seller_level_dict = {'Large':0,'Medium':1,'New':2,'Small':3,'Special':4}
warehouse_category_dict = {'区域仓':0,'中心仓':1}
warehouse_region = {'东北':0,'华北':1,'华东':2,'华南':3,'华中':4,'西北':5,'西南':6}
mapped_data=data
mapped_data['seller_no'] = mapped_data['seller_no'].map(seller_dict)
mapped_data['product_no'] = mapped_data['product_no'].map(product_dict)
mapped_data['warehouse_no'] = mapped_data['warehouse_no'].map(warehouse_dict)
mapped_data['seller_category'] = mapped_data['seller_category'].map(seller_category_dict)
mapped_data['inventory_category'] = mapped_data['inventory_category'].map(inventory_category_dict)
mapped_data['seller_level'] = mapped_data['seller_level'].map(seller_level_dict)
mapped_data['warehouse _category'] = mapped_data['warehouse _category'].map(warehouse_category_dict)
mapped_data['warehouse _region'] = mapped_data['warehouse _region'].map(warehouse_region)


columns_to_drop = ['date', 'category1', 'category2','category3']

mapped_data.drop(columns=columns_to_drop, inplace=True)

grouped = mapped_data.groupby(['seller_no', 'product_no', 'warehouse_no'])
grouped = filter(grouped)

averages = np.zeros((1996, 9))
for i in range(1996):
    group = grouped[i]
    for j in range(9):
        column_average = np.mean(group.iloc[:, j])
        averages[i, j] = column_average

averages_new = averages[:, 3:]

sse = []
k_values = range(1, 11)

for k in k_values:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(averages_new)
    sse.append(kmeans.inertia_)

kmeans = KMeans(n_clusters=2)

labels = kmeans.fit_predict(averages_new)

centers = kmeans.cluster_centers_

print(labels)
print(centers)

plt.scatter(averages_new[:, 0], averages_new[:, 1], c=labels)
plt.scatter(centers[:, 0], centers[:, 1], marker='x', c='red')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Clustering Results')
plt.show()