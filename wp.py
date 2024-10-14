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

data = {
    "districts": [
        {
            "name": "Quận 10",
            "wards": [
                {"name": "Phường 1"},
                {"name": "Phường 2"},
                {"name": "Phường 3"},
                {"name": "Phường 4"},
                {"name": "Phường 5"},
                {"name": "Phường 6"},
                {"name": "Phường 7"},
                {"name": "Phường 8"},
                {"name": "Phường 9"},
                {"name": "Phường 10"},
                {"name": "Phường 11"},
                {"name": "Phường 12"},
                {"name": "Phường 13"},
                {"name": "Phường 14"},
                {"name": "Phường 15"}
            ]
        },
        {
            "name": "Quận 11",
            "wards": [
                {"name": "Phường 1"},
                {"name": "Phường 2"},
                {"name": "Phường 3"},
                {"name": "Phường 4"},
                {"name": "Phường 5"},
                {"name": "Phường 6"},
                {"name": "Phường 7"},
                {"name": "Phường 8"},
                {"name": "Phường 9"},
                {"name": "Phường 10"},
                {"name": "Phường 11"},
                {"name": "Phường 12"},
                {"name": "Phường 13"},
                {"name": "Phường 14"},
                {"name": "Phường 15"},
                {"name": "Phường 16"}
            ]
        },
        {
            "name": "Quận 12",
            "wards": [
                {"name": "Phường An Phú Đông"},
                {"name": "Phường Đông Hưng Thuận"},
                {"name": "Phường Hiệp Thành"},
                {"name": "Phường Tân Chánh Hiệp"},
                {"name": "Phường Tân Hưng Thuận"},
                {"name": "Phường Tân Thới Hiệp"},
                {"name": "Phường Tân Thới Nhất"},
                {"name": "Phường Thạnh Lộc"},
                {"name": "Phường Thạnh Xuân"},
                {"name": "Phường Thới An"},
                {"name": "Phường Trung Mỹ Tây"}
            ]
        },
        {
            "name": "Quận Bình Tân",
            "wards": [
                {"name": "Phường An Lạc"},
                {"name": "Phường An Lạc A"},
                {"name": "Phường Bình Hưng Hòa"},
                {"name": "Phường Bình Hưng Hòa A"},
                {"name": "Phường Bình Hưng Hòa B"},
                {"name": "Phường Bình Trị Đông"},
                {"name": "Phường Bình Trị Đông A"},
                {"name": "Phường Bình Trị Đông B"},
                {"name": "Phường Tân Tạo"},
                {"name": "Phường Tân Tạo A"}
            ]
        },
        {
            "name": "Quận Phú Nhuận",
            "wards": [
                {"name": "Phường 1"},
                {"name": "Phường 2"},
                {"name": "Phường 3"},
                {"name": "Phường 4"},
                {"name": "Phường 5"},
                {"name": "Phường 7"},
                {"name": "Phường 8"},
                {"name": "Phường 9"},
                {"name": "Phường 10"},
                {"name": "Phường 11"},
                {"name": "Phường 12"},
                {"name": "Phường 13"},
                {"name": "Phường 14"},
                {"name": "Phường 15"},
                {"name": "Phường 17"}
            ]
        },
        {
            "name": "Quận Tân Phú",
            "wards": [
                {"name": "Phường Hiệp Tân"},
                {"name": "Phường Hòa Thạnh"},
                {"name": "Phường Phú Thạnh"},
                {"name": "Phường Phú Thọ Hòa"},
                {"name": "Phường Phú Trung"},
                {"name": "Phường Sơn Kỳ"},
                {"name": "Phường Tân Qúy"},
                {"name": "Phường Tân Sơn Nhì"},
                {"name": "Phường Tân Thành"},
                {"name": "Phường Tân Thới Hòa"},
                {"name": "Phường Tây Thạnh"}
            ]
        },
        {
            "name": "Quận Tân Bình",
            "wards": [
                {"name": "Phường 1"},
                {"name": "Phường 2"},
                {"name": "Phường 3"},
                {"name": "Phường 4"},
                {"name": "Phường 5"},
                {"name": "Phường 6"},
                {"name": "Phường 7"},
                {"name": "Phường 8"},
                {"name": "Phường 9"},
                {"name": "Phường 10"},
                {"name": "Phường 11"},
                {"name": "Phường 12"},
                {"name": "Phường 13"},
                {"name": "Phường 14"},
                {"name": "Phường 15"}
            ]
        }
    ]
}

with app.app_context():
    total = utils.calculate_total_revenue()
    print(total)