import random
from datetime import datetime, timedelta
from itertools import product

from dateutil.relativedelta import relativedelta
from flask import request, redirect, flash, session
from flask_login import current_user
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import aliased
from Flask_App.models import Distribution, User, User_Role, Privileged, Product, Goods_Received_Note, Provider, \
    Goods_Delivery_Note, Delivery_Reason, Goods_Delivery_Note_Detail, Receipt, TimeUnitEnum, Warranty, Category, \
    Promotion, District, Ward, PromotionDetail, DiscountType, WarrantyDetail, ReceiptDetail
from Flask_App import app, db, utils
import requests
from Flask_App.utils import get_receipt_by_id
import pandas as pd
import json

with app.app_context():
    details, price1, price2 = utils.load_receipt_detail(58)

    parsed_details = []
    for r in details:
        parsed_detail = {
            "receipt_id": r[0],
            "product_id": r[1],
            "quantity": r[2],
            "unit_price": r[3],
            "discount": r[4],
            "discount_info": r[5],
            "on_warranty": r[6],
            "warranty_details": json.loads(r[7]),  # Parse chuỗi JSON ở đây
            "product_name": r[8],
            "product_image": r[9],
        }

        parsed_details.append(parsed_detail)

    for detail in parsed_details:
        for warranty in detail['warranty_details']:
            print(warranty['time_unit'])



