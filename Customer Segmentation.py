import pandas as pd
import datetime as dt

pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: "%.4f" % x)

df_ = pd.read_csv(r"C:\Users\ASUS\PycharmProjects\pythonProject\flo_data_20k.csv")
df = df_.copy()

df.describe().T
df.head()
df.shape
df.isnull().sum()
df.columns
df.dtypes
df.shape

df.nunique()
df["master_id"].nunique()
df["last_order_date"].nunique()


# Omnichannel means that customers shop from both online and offline platforms. Create new variables for the total number of purchases and spending of each customer

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["omnichannel_cv_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

df["order_num_total"].sum()
df["omnichannel_cv_total"].sum()

date_columns = df.columns[df.columns.str.contains("date")] 
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.dtypes

#df = [df.columns.apply(pd.to_datetime) if "date" in col for col in df.columns]


# See the distribution of the number of customers, total number of products purchased and total expenditure across shopping channels.

df.groupby("order_channel").agg({#"master_id": "count" ,
                                "order_num_total": ["sum", "count"],
                             "omnichannel_cv_total": ["sum", "mean"]}).head()

# List the top 10 most profitable customers
df.groupby("master_id").agg({"omnichannel_cv_total": lambda x: x.max()}).\
    sort_values("omnichannel_cv_total", ascending=False).head(10)


# List the top 10 customers who placed the most orders.
df.groupby("master_id").agg({"order_num_total": lambda x: x.max()}).\
    sort_values("order_num_total", ascending=False).head(10)


# Functionalise the data preparation process.

def create_prep(dataframe, csv=False):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["omnichannel_cv_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains ( "date" )]
    dataframe[date_columns] = dataframe[date_columns].apply ( pd.to_datetime )
    return dataframe

create_prep(df)

######################################################
# Define Recency, Frequency ve Monetary

df["last_order_date"].max()
today_date = dt.datetime(2021, 6, 1)
type(today_date)


rfm = df.groupby('master_id').agg({'last_order_date': lambda last_order_date: (today_date - last_order_date.max()).days,
                                     'order_num_total': lambda order_num_total: order_num_total.sum(),
                                     'omnichannel_cv_total': lambda omnichannel_cv_total: omnichannel_cv_total.sum()})


rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T

####################################################

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])


rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.describe().T
df.describe().T

###########################################

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm = rfm[["recency", "frequency", "monetary", "segment"]]

df_rfm = pd.merge(df, rfm, on="master_id")

rfm.head()
rfm.columns


##############################################################3

rfm.groupby("segment").agg({"recency": ["mean", "count"],
                            "frequency": ["mean", "count"],
                            "monetary": ["mean", "count"]})


# With the help of RFM analysis, find the customers in the relevant profile for the 2 cases given below and save the customer ids as csv
# a. FLO is incorporating a new women's footwear brand. The product prices of the brand it includes are determined by the general customer
# above their preferences. Therefore, for the promotion of the brand and product sales, we specially contact customers with the profile of interest
# to get in touch with you. Loyal customers (champions, loyal_customers) and shopping in the female category
# are customers to be specially contacted. Save the id numbers of these customers in the csv file.

target_segments_customer_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) &(df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
cust_ids.to_csv("yeni_marka_hedef_müşteri_id.csv", index=False)
cust_ids.shape

# priv_customer = df_rfm.loc[(df_rfm["segment"] == "champions") | (df_rfm["segment"] == "loyal_customers") & (df_rfm["interested_in_categories_12"].str.contains("KADIN")), "master_id"]
# priv_customer.shape
# priv_customer.head()

# priv_customer.to_csv("priv_customer_id")

# b. A discount of up to 40% is planned for Men's and Children's products. In the past interested in the categories related to this discount
# customers who are good customers but have not been shopping for a long time, customers who should not be lost, dormant customers and new customers
# incoming customers want to be targeted specifically. Save the ids of customers in the appropriate profile to csv file

target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","hibernating","new_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK"))|(df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("indirim_hedef_müşteri_ids.csv", index=False)

# df_rfm["segment"].value_counts()
# target = ["hibernating", "about_to_sleep", "new_customers"]

# target_id = df_rfm[(df_rfm['segment'].isin(target)) & (df["interested_in_categories_12"].str.contains("ERKEK")) | (df["interested_in_categories_12"].str.contains("COCUK"))]["master_id"]

# target_id.shape
# target_id.to_csv("target_customer_id")
