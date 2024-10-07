import random
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
    def load_manage_product(kw=None, page=1, **kwargs):
        products = db.session.query(Product.id,
                                    Product.name,
                                    Product.price,
                                    Product.category_id,
                                    Product.active,
                                    Product.image,
                                    Product.import_price,
                                    Category.name.label('category_name'),
                                    Provider.name.label('provider_name')) \
            .join(Category, Category.id == Product.category_id) \
            .join(Distribution, Distribution.product_id == Product.id) \
            .join(Provider, Provider.id == Distribution.provider_id)

        if kw:
            if kw.isdigit():
                products = products.filter(Category.id == int(kw))
            else:
                products = products.filter(Category.name.contains(kw))

        if kwargs.get('active'):
            active = kwargs.get('active')
            if active == 'True':
                products = products.filter(Product.active == True)
            elif active == 'False':
                products = products.filter(Product.active == False)

        if kwargs.get('provider_id'):
            provider_id = kwargs.get('provider_id')

            products = products.filter(Provider.id == provider_id)

        if kwargs.get('from_price'):
            from_price = kwargs.get('from_price')

            products = products.filter(Product.price.__ge__(from_price))

        if kwargs.get('to_price'):
            to_price = kwargs.get('to_price')

            products = products.filter(Product.price.__le__(to_price))

        if kwargs.get('from_import_price'):
            from_import_price = kwargs.get('from_import_price')

            products = products.filter(Product.import_price.__ge__(from_import_price))

        if kwargs.get('to_import_price'):
            to_import_price = kwargs.get('to_import_price')

            products = products.filter(Product.import_price.__le__(to_import_price))

        start = (page - 1) * app.config['VIEW_SIZE']
        end = start + app.config['VIEW_SIZE']

        products_count = products.count()

        return products.slice(start, end).all(), products_count

    count = load_manage_product('1')[1]
    print(count)
    print(load_manage_product('1'))