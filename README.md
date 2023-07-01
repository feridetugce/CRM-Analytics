# RFM ANALYSIS FOR CUSTOMER SEGMENTATION AND CLTV PREDICTION

FLO is one of Turkey's largest footwear companies. In this project, two analyses will be conducted to enable FLO to segment its customers and take action with targeted campaigns for each segment.

1. Customer Segmentation with RFM Analysis
2. CLTV (Customer Lifetime Value) Prediction with BG-NBD and Gamma-Gamma Models

Dataset Story:
The dataset consists of information derived from the past shopping behavior of customers who made purchases from FLO through OmniChannel (both online and offline) between 2020 and 2021.

- master_id: Unique customer number
- order_channel: Channel used for the purchase (Android, iOS, Desktop, Mobile)
- last_order_channel: Channel used for the most recent purchase
- first_order_date: Date of the customer's first purchase
- last_order_date: Date of the customer's most recent purchase
- last_order_date_online: Date of the customer's most recent online purchase
- last_order_date_offline: Date of the customer's most recent offline purchase
- order_num_total_ever_online: Total number of purchases made by the customer online
- order_num_total_ever_offline: Total number of purchases made by the customer offline
- customer_value_total_ever_online: Total amount spent by the customer on online purchases
- customer_value_total_ever_offline: Total amount spent by the customer on offline purchases
- interested_in_categories_12: List of categories in which the customer made purchases in the last 12 months

BUSINESS PROBLEM:
FLO, an online shoe store, aims to segment its customers and develop marketing strategies based on these segments. To achieve this, customer behaviors will be defined, and groups will be formed based on clustering patterns within these behaviors.
