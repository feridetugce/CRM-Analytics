
#Veri seti Flo’dan son alışverişlerini 2020 - 2021 yıllarında OmniChannel (hem online hem offline alışveriş yapan)
#olarak yapan müşterilerin geçmiş alışveriş davranışlarından elde edilen bilgilerden oluşmaktadır.
#12 Değişken 19.945 Gözlem içermektedir

#master_id Eşsiz müşteri numarası
#order_channel Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile)
#last_order_channel En son alışverişin yapıldığı kanal
#first_order_date Müşterinin yaptığı ilk alışveriş tarihi
#last_order_date Müşterinin yaptığı son alışveriş tarihi
#last_order_date_online Müşterinin online platformda yaptığı son alışveriş tarihi
#last_order_date_offline Müşterinin offline platformda yaptığı son alışveriş tarihi
#order_num_total_ever_online Müşterinin online platformda yaptığı toplam alışveriş sayısı
#order_num_total_ever_offline Müşterinin offline'da yaptığı toplam alışveriş sayısı
#customer_value_total_ever_offline Müşterinin offline alışverişlerinde ödediği toplam ücret
#customer_value_total_ever_online Müşterinin online alışverişlerinde ödediği toplam ücret
#interested_in_categories_12 Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi
####################################################################################################


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
#Görev 1: Veriyi Hazırlama
#Adım 1: flo_data_20K.csv verisini okuyunuz.Dataframe’in kopyasını oluşturunuz.

df_ = pd.read_csv(r"C:\Users\ASUS\PycharmProjects\pythonProject1_Bootcamp\flo_data_20k.csv")
df = df_.copy()

#df.head()
#df.isnull().sum()
#df.describe().T


#Adım 2: Aykırı değerleri baskılamak için gerekli olan outlier_thresholds ve replace_with_thresholds fonksiyonlarını tanımlayınız.
#Not: cltv hesaplanırken frequency değerleri integer olması gerekmektedir.Bu nedenle alt ve üst limitlerini round() ile yuvarlayınız.

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



#Adım 3: "order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline",
#"customer_value_total_ever_online" değişkenlerinin aykırı değerleri varsa baskılayanız.

thresholds = ["order_num_total_ever_online","order_num_total_ever_offline","customer_value_total_ever_offline","customer_value_total_ever_online"]
for i in thresholds:
    replace_with_thresholds ( df, i)



#Adım 4: Omnichannel müşterilerin hem online'dan hem de offline platformlardan alışveriş yaptığını ifade etmektedir. Her bir müşterinin toplam
#alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df.head()


#Adım 5: Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.
df.dtypes

date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.dtypes


#########################################################################################
#Görev 2: CLTV Veri Yapısının Oluşturulması
#Adım 1: Veri setindeki en son alışverişin yapıldığı tarihten 2 gün sonrasını analiz tarihi olarak alınız

df["last_order_date"].max()

today_date = df["last_order_date"].max() + pd.DateOffset(days=2)
#ya da
today_date = dt.datetime(Year, Month, Day)


#Adım 2: customer_id, recency_cltv_weekly, T_weekly, frequency ve monetary_cltv_avg değerlerinin yer aldığı yeni bir cltv dataframe'i oluşturunuz.
#Monetary değeri satın alma başına ortalama değer olarak, recency ve tenure değerleri ise haftalık cinsten ifade edilecek.

# recency: Son satın alma üzerinden geçen zaman. Haftalık. (kullanıcı özelinde)
# T: Müşterinin yaşı. Haftalık. (analiz tarihinden ne kadar süre önce ilk satın alma yapılmış)
# frequency: tekrar eden toplam satın alma sayısı (frequency>1)
# monetary: satın alma başına ortalama kazanç

cltv_df = pd.DataFrame({"customer_id": df["master_id"],
                        "recency_cltv_weekly": ((df["last_order_date"] - df["first_order_date"]).dt.days)/ 7, #weekly istediği için 7ye böldük
                        "T_weekly": ((today_date - df["first_order_date"]).dt.days)/ 7, #musterinin yaşı=bugunun tarihinden ilk alısveris yaptıgı tarihi çıkarıyoruz, haftalık olması için 7'ye böldük
                        "frequency": df["order_num_total"],
                        "monetary_cltv_avg": df["customer_value_total"]/df["order_num_total"]}) #toplam harcama/toplam alısveris sayısı

cltv_df.head()
cltv_df.describe().T


###############################################################################
#Görev 3: BG/NBD, Gamma-Gamma Modellerinin Kurulması ve CLTV’nin Hesaplanması
#Adım 1: BG/NBD modelini fit ediniz- satışı hesaplıyoruz

bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df['frequency'],
        cltv_df['recency_cltv_weekly'],
        cltv_df['T_weekly'])

# 3 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_3_month olarak cltv dataframe'ine ekleyiniz.

cltv_df["expected_purc_3_month"] = bgf.predict(12,#4*3
                                                                                           cltv_df['frequency'] ,
                                                                                           cltv_df['recency_cltv_weekly'] ,
                                                                                           cltv_df['T_weekly']).sort_values(ascending=False)


cltv_df.describe().T

# 6 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_6_month olarak cltv dataframe'ine ekleyiniz
cltv_df["expected_purc_6_month"] = bgf.predict(24,#4*6
                                               cltv_df['frequency'] ,
                                               cltv_df['recency_cltv_weekly'] ,
                                               cltv_df['T_weekly'] ).sort_values(ascending=False)

cltv_df.describe().T

plot_period_transactions(bgf)
plt.show(block = True)


#Adım 2: Gamma-Gamma modelini fit ediniz. Müşterilerin ortalama bırakacakları değeri tahminleyip exp_average_value olarak cltvdataframe'ine ekleyiniz

ggf = GammaGammaFitter(penalizer_coef=0.001)
ggf.fit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])

ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                        cltv_df['monetary_cltv_avg'])


cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                             cltv_df['monetary_cltv_avg'])

cltv_df.sort_values("expected_average_profit", ascending=False).head(10)

cltv_df.describe().T



#Adım 3: 6 aylık CLTV hesaplayınız ve cltv ismiyle dataframe'e ekleyiniz.
#Cltv değeri en yüksek 20 kişiyi gözlemleyiniz

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
#Görev 4: CLTV Değerine Göre Segmentlerin Oluşturulmas
#Adım 1: 6 aylık CLTV'ye göre tüm müşterilerinizi 4 gruba (segmente) ayırınız ve grup isimlerini veri setine ekleyiniz.

cltv_df["segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])


#Adım 2: 4 grup içerisinden seçeceğiniz 2 grup için yönetime kısa kısa 6 aylık aksiyon önerilerinde bulununuz.

