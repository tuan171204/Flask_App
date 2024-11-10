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

with app.app_context():
    details = utils.load_receipt_detail(51)[0]

    print(details)
