
import datetime as dt
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 100)
pd.set_option('display.float_format', lambda x: '%.4f' % x)
from sklearn.preprocessing import MinMaxScaler

########################################################################

df_ = pd.read_csv(r"C:\Users\ASUS\PycharmProjects\pythonProject1_Bootcamp\flo_data_20k.csv")
df = df_.copy()

#df.head()
#df.isnull().sum()
#df.describe().T


def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    low_limit = low_limit.round()
    up_limit = up_limit.round()
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


thresholds = ["order_num_total_ever_online","order_num_total_ever_offline","customer_value_total_ever_offline","customer_value_total_ever_online"]
for i in thresholds:
    replace_with_thresholds ( df, i)

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df.head()

df.dtypes

date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.dtypes



df["last_order_date"].max()

today_date = df["last_order_date"].max() + pd.DateOffset(days=2)
#today_date = dt.datetime(Year, Month, Day)


# recency: The amount of time that has passed since the customer's last purchase. Measured on a weekly basis. (calculated for each individual user)
# T: Customer tenure. Measured on a weekly basis. It represents the time that has elapsed since the customer's first purchase from the analysis date.
# frequency: The total number of repeat purchases made by the customer. This metric considers only purchases with a frequency greater than 1.
# monetary: The average earnings or revenue generated per purchase. It indicates the average amount of money spent by the customer in each transaction.

cltv_df = pd.DataFrame({"customer_id": df["master_id"],
                        "recency_cltv_weekly": ((df["last_order_date"] - df["first_order_date"]).dt.days)/ 7, #weekly istediği için 7ye böldük
                        "T_weekly": ((today_date - df["first_order_date"]).dt.days)/ 7, #musterinin yaşı=bugunun tarihinden ilk alısveris yaptıgı tarihi çıkarıyoruz, haftalık olması için 7'ye böldük
                        "frequency": df["order_num_total"],
                        "monetary_cltv_avg": df["customer_value_total"]/df["order_num_total"]}) #toplam harcama/toplam alısveris sayısı

cltv_df.head()
cltv_df.describe().T


###############################################################################

bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df['frequency'],
        cltv_df['recency_cltv_weekly'],
        cltv_df['T_weekly'])

# Please predict the expected purchases from customers within a 3-month period and add it as "exp_sales_3_month" to the CLTV dataframe.

cltv_df["expected_purc_3_month"] = bgf.predict(12,#4*3
                                                                                           cltv_df['frequency'] ,
                                                                                           cltv_df['recency_cltv_weekly'] ,
                                                                                           cltv_df['T_weekly']).sort_values(ascending=False)


cltv_df.describe().T

# Please predict the expected purchases from customers within a 6-month period and add it as "exp_sales_6_month" to the CLTV dataframe. 
cltv_df["expected_purc_6_month"] = bgf.predict(24,#4*6
                                               cltv_df['frequency'] ,
                                               cltv_df['recency_cltv_weekly'] ,
                                               cltv_df['T_weekly'] ).sort_values(ascending=False)

cltv_df.describe().T

plot_period_transactions(bgf)
plt.show(block = True)


ggf = GammaGammaFitter(penalizer_coef=0.001)
ggf.fit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])

ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                        cltv_df['monetary_cltv_avg'])


cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                             cltv_df['monetary_cltv_avg'])

cltv_df.sort_values("expected_average_profit", ascending=False).head(10)

cltv_df.describe().T



cltv_df["cltv"] = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency_cltv_weekly'],
                                   cltv_df['T_weekly'],
                                   cltv_df['monetary_cltv_avg'],
                                   time=6,  # 6 aylık
                                   freq="W",  # T'nin frekans bilgisi.
                                   discount_rate=0.01)

cltv_df.sort_values("cltv",ascending=False)
cltv_df.describe().T

################################################################

cltv_df["segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])
