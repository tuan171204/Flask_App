import random
from datetime import datetime, timedelta
from itertools import product
from flask import request, redirect, flash, session
from flask_login import current_user
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from Flask_App.models import Distribution, User, User_Role, Privileged, Product, Goods_Received_Note, Provider, \
    Goods_Delivery_Note, Delivery_Reason, Goods_Delivery_Note_Detail, Receipt, TimeUnitEnum, Warranty, Category, \
    Promotion, District, Ward, PromotionDetail, DiscountType
from Flask_App import app, db, utils
import requests
from Flask_App.utils import get_receipt_by_id
import pandas as pd


# with app.app_context():
#     receipt_list = Receipt.query.all()
#
#     data = [{
#         "id": receipt.id,
#         "created_date": receipt.created_date
#     } for receipt in receipt_list]
#
#     df = pd.DataFrame(data)
#
#     daily_counts = df['created_date'].dt.date.value_counts().sort_index()
#     print(daily_counts)
#
#     # Đếm số lượng hóa đơn theo tháng
#     monthly_counts = df['created_date'].dt.to_period('M').value_counts().sort_index()
#     print(monthly_counts)



with app.app_context():
    sale_month_stats_last_year = utils.product_months_stats(datetime.now().year - 1)

    customer_month_stats = utils.customer_months_stats(datetime.now().year)

    print(sale_month_stats_last_year)
    for s in sale_month_stats_last_year:
        print(s[0])

    print(customer_month_stats)