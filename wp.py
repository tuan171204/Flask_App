from datetime import datetime

from flask import request, redirect, flash, session
from flask_login import current_user
from sqlalchemy import desc
from sqlalchemy.orm import aliased

from Flask_App.models import Distribution, User, User_Role, Privileged, Product, Goods_Received_Note, Provider, \
    Goods_Delivery_Note, Delivery_Reason, Goods_Delivery_Note_Detail, Receipt, TimeUnitEnum, Warranty, Category, \
    Promotion
from Flask_App import app, db, utils

import requests

from Flask_App.utils import get_receipt_by_id

with app.app_context():
    user = utils.get_user_by_id(1)
    print(user.password)