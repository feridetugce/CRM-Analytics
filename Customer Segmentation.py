Skip to content
Search or jump to…
Pull requests
Issues
Codespaces
Marketplace
Explore
 
@feridetugce 
feridetugce
/
RFM-Analysis
Public
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
RFM-Analysis/Customer Segmentation.py /
@feridetugce
feridetugce Update Customer Segmentation.py
Latest commit 96c18e1 10 minutes ago
 History
 1 contributor
210 lines (153 sloc)  9.08 KB

#Veri seti Flo’dan son alışverişlerini 2020 - 2021 yıllarında OmniChannel (hem online hem offline alışveriş yapan)
#olarak yapan müşterilerin geçmiş alışveriş davranışlarından elde edilen bilgilerden oluşmaktadır.
#12 Değişken 19.945 Gözlem 2.7MB

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


import pandas as pd
import datetime as dt

pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: "%.4f" % x)

#Adım 1: flo_data_20K.csv verisini okuyunuz.Dataframe’in kopyasını oluşturunuz.
df_ = pd.read_csv(r"C:\Users\ASUS\PycharmProjects\pythonProject1_Bootcamp\flo_data_20k.csv")
df = df_.copy()


df.describe().T
df.head()
df.shape
df.isnull().sum()
df.columns

df.nunique()
df["master_id"].nunique()
df["last_order_date"].nunique()


#Adım 2: Veri setinde
#a. İlk 10 gözlem,
df.head(10)
#b. Değişken isimleri,
df.columns
#c. Betimsel istatistik,
df.describe().T
#d. Boş değer,
df.isnull().sum()
#e. Değişken tipleri, incelemesi yapını
df.dtypes
df.shape


#Adım 3: Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir.
# Her bir müşterinin toplam alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz
df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["omnichannel_cv_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

df["order_num_total"].sum()
df["omnichannel_cv_total"].sum()

#Adım 4: Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz
df.dtypes

date_columns = df.columns[df.columns.str.contains("date")] 


df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.dtypes

#df = [df.columns.apply(pd.to_datetime) if "date" in col for col in df.columns]


#Adım 5: Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız.
df.head()
df.shape

df.groupby("order_channel").agg({#"master_id": "count" ,
                                "order_num_total": ["sum", "count"],
                             "omnichannel_cv_total": ["sum", "mean"]}).head()


#Adım 6: En fazla kazancı getiren ilk 10 müşteriyi sıralayını
df.groupby("master_id").agg({"omnichannel_cv_total": lambda x: x.max()}).\
    sort_values("omnichannel_cv_total", ascending=False).head(10)


#Adım 7: En fazla siparişi veren ilk 10 müşteriyi sıralayınız.
df.groupby("master_id").agg({"order_num_total": lambda x: x.max()}).\
    sort_values("order_num_total", ascending=False).head(10)

#Adım 8: Veri ön hazırlık sürecini fonksiyonlaştırınız.

def create_prep(dataframe, csv=False):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["omnichannel_cv_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains ( "date" )]
    dataframe[date_columns] = dataframe[date_columns].apply ( pd.to_datetime )
    return dataframe

create_prep(df)

######################################################
#Görev 2: RFM Metriklerinin Hesaplanması
#Adım 1: Recency, Frequency ve Monetary tanımlarını yapını

df["last_order_date"].max()
today_date = dt.datetime(2021, 6, 1)
type(today_date)

#Adım 2: Müşteri özelinde Recency, Frequency ve Monetary metriklerini hesaplayınız.
#Adım 3: Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.

rfm = df.groupby('master_id').agg({'last_order_date': lambda last_order_date: (today_date - last_order_date.max()).days,
                                     'order_num_total': lambda order_num_total: order_num_total.sum(),
                                     'omnichannel_cv_total': lambda omnichannel_cv_total: omnichannel_cv_total.sum()})



#Adım 4: Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz
rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T

####################################################
#Görev 3: RF Skorunun Hesaplanması
#Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
#Adım 2: Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])


#Adım 3: recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydedin
#astype(srt) önemli yoksa sayısal alabilir
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.describe().T
df.describe().T

###########################################
#Görev 4: RF Skorunun Segment Olarak Tanımlanması
#Adım 1: Oluşturulan RF skorları için segment tanımlamaları yapınız
#Adım 2: Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.

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
#rfm segmente seg-mapten scorlara göre atama yapıyor
rfm = rfm[["recency", "frequency", "monetary", "segment"]]

#dataframe ile rfm i birleştirmek için bu işlemi yapıyoruz
df_rfm = pd.merge(df, rfm, on="master_id")

rfm.head()
rfm.columns


##############################################################3
#Görev 5
#Adım 1: Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.
rfm.groupby("segment").agg({"recency": ["mean", "count"],
                            "frequency": ["mean", "count"],
                            "monetary": ["mean", "count"]})


#Adım 2: RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz
#a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri
# tercihlerinin üstünde. Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak
# iletişime geçmek isteniliyor. Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş
# yapan kişiler özel olarak iletişim kurulacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına kaydediniz.

priv_customer = df_rfm.loc[(df_rfm["segment"] == "champions") | (df_rfm["segment"] == "loyal_customers") & (df_rfm["interested_in_categories_12"].str.contains("KADIN")), "master_id"]
priv_customer.shape
priv_customer.head()

priv_customer.to_csv("priv_customer_id")

#b. Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte
# iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni
# gelen müşteriler özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydedini


df_rfm["segment"].value_counts()
target = ["hibernating", "about_to_sleep", "new_customers"]

target_id = df_rfm[(df_rfm['segment'].isin(target)) & (df["interested_in_categories_12"].str.contains("ERKEK")) |
                                                         (df["interested_in_categories_12"].str.contains("COCUK"))]["master_id"]


target_id.shape
target_id.to_csv("target_customer_id")

