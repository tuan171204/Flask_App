import math
import os
import string
import random
from datetime import datetime, timedelta
from PIL import Image
from dateutil.relativedelta import relativedelta
from matplotlib.ticker import FuncFormatter
from numpy import record
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce

from Flask_App import app, db, ALLOWED_EXTENSIONS
from Flask_App.models import Category, Product, User, Receipt, ReceiptDetail, User_Role, Comment, Payment, \
    Provider, Distribution, Receipt_Status, Privileged, Report_Type, Receipt_Report, Delivery_Reason, \
    Goods_Received_Note, Goods_Received_Note_Detail, Goods_Delivery_Note, Goods_Delivery_Note_Detail, Promotion, \
    Warranty, Brand, PromotionDetail, District, Ward, WarrantyDetail, TimeUnitEnum, DiscountType
import hashlib
from flask_login import current_user
from sqlalchemy import func, and_, or_, desc, Integer, literal_column
from sqlalchemy.sql import extract
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import matplotlib.pyplot as plt


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_categories_client():
    return Category.query.all()


def get_child_category(category_id):
    return Category.query.filter(Category.parent_id == category_id).all()


def load_categories(kw=None, page=1):
    start = (page - 1) * app.config['VIEW_SIZE']

    query = Category.query

    if kw:
        if kw.isdigit():
            query = query.filter(Category.id == int(kw))
        else:
            query = query.filter(Category.name.contains(kw))

    total_count = query.count()
    categories = query.offset(start).limit(app.config['VIEW_SIZE']).all()

    return categories, total_count


def load_products(cate_id=None, kw=None, page=1):
    products = Product.query.filter(Product.active.__eq__(True))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if kw:
        products = products.filter(Product.name.contains(kw))

    products = products.order_by(Product.category_id)
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size
    # select * from product limit 4 offset 0

    return products.slice(start, end).all()


def load_products_admin(cate_id=None, kw=None, page=1):
    products = Product.query.filter(Product.active.__eq__(True))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if kw:
        products = products.filter(Product.name.contains(kw))

    products = products.order_by(Product.category_id)
    page_size = app.config['VIEW_SIZE']
    start = (page - 1) * page_size
    end = start + page_size
    # select * from product limit 4 offset 0

    return products.slice(start, end).all()


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
            products = products.filter(Product.id == int(kw))
        else:
            products = products.filter(Product.name.contains(kw))

    if kwargs.get('active'):
        active = kwargs.get('active')
        if active == 'True':
            products = products.filter(Product.active == True)
        elif active == 'False':
            products = products.filter(Product.active == False)

    if kwargs.get('provider_id'):
        provider_id = kwargs.get('provider_id')

        products = products.filter(Provider.id == provider_id)

    if kwargs.get('import_price_asc'):
        if kwargs.get('import_price_asc') == 'True':
            products = products.order_by(Product.import_price)

        elif kwargs.get('import_price_asc') == 'False':
            products = products.order_by(desc(Product.import_price))

    if kwargs.get('price_asc'):
        if kwargs.get('price_asc') == 'True':
            products = products.order_by(Product.price)

        elif kwargs.get('price_asc') == 'False':
            products = products.order_by(desc(Product.price))

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


def load_all_products():
    products = Product.query.filter(Product.active.__eq__(True))
    products = products.order_by(Product.category_id)
    return products


def load_all_realtime_products():
    products = Product.query.all()

    return products


def count_product(cate_id=None, kw=None):
    if cate_id:
        return Product.query.filter(and_(Product.active.__eq__(True), Product.category_id.__eq__(cate_id))).count()

    if kw:
        return Product.query.filter(Product.name.contains(kw)).count()

    return Product.query.filter(Product.active.__eq__(True)).count()


def count_receipt(status_id=None):
    if status_id:
        return Receipt.query.filter(Receipt.status_id == status_id).count()

    return Receipt.query.count()


def count_receive_note(confirmed=None, received_note_code=None):
    if received_note_code:
        return 1

    if confirmed is not None:
        if confirmed == 'True':
            return Goods_Received_Note.query.filter(Goods_Received_Note.confirmed == True).count()

        elif confirmed == 'False':
            return Goods_Received_Note.query.filter(Goods_Received_Note.confirmed == False).count()

    return Goods_Received_Note.query.count()


def count_delivery_note(confirmed=None, delivery_code=None, reason=None, delivery_man_id=None):
    if delivery_code:
        return 1

    delivery_note_count = Goods_Delivery_Note.query

    if confirmed is not None:
        if confirmed == 'True':
            delivery_note_count = delivery_note_count.filter(Goods_Delivery_Note.confirmed == True)
        elif confirmed == 'False':
            delivery_note_count = delivery_note_count.filter(Goods_Delivery_Note.confirmed == False)

    if reason:
        delivery_note_count = delivery_note_count.filter(Goods_Delivery_Note.reason == reason)

    if delivery_man_id:
        delivery_note_count = delivery_note_count.filter(Goods_Delivery_Note.delivery_man == delivery_man_id)

    return delivery_note_count.count()


def count_user(user_id=None, active=None, info=None):
    if user_id:
        return 1

    if active:
        if active == 'True':
            return User.query.filter(User.active == True).count()
        else:
            return User.query.filter(User.active == False).count()

    if info:
        return 1

    return User.query.count()


def get_product_by_id(product_id):
    product = Product.query.filter(Product.id == product_id).first()
    return product


def get_product_detail_info(product_id):
    product = db.session.query(Product.id,
                               Product.name,
                               Product.image,
                               Product.price,
                               Product.description,
                               PromotionDetail.discount_value.label('discount_value'),
                               PromotionDetail.discount_type.label('discount_type'),
                               Promotion.description.label('promotion_description')) \
        .outerjoin(PromotionDetail, PromotionDetail.product_id == Product.id) \
        .outerjoin(Promotion, Promotion.id == PromotionDetail.promotion_id) \
        .filter(Product.id == product_id) \
        .filter(Promotion.end_date > datetime.now()).first()

    if product is None:
        product = db.session.query(
            Product.id,
            Product.name,
            Product.image,
            Product.price,
            Product.description
        ).filter(Product.id == product_id).first()

    return product


def get_product_detail_info_admin(product_id):
    product = db.session.query(Product.id,
                               Product.name,
                               Product.image,
                               Product.price,
                               Product.import_price,
                               Product.description,
                               Product.category_id,
                               Category.name.label('category_name'),
                               PromotionDetail.discount_value.label('discount_value'),
                               PromotionDetail.discount_type.label('discount_type'),
                               Promotion.description.label('promotion_description')) \
        .outerjoin(PromotionDetail, PromotionDetail.product_id == Product.id) \
        .outerjoin(Promotion, Promotion.id == PromotionDetail.promotion_id) \
        .join(Category, Category.id == Product.category_id) \
        .filter(Product.id == product_id).first()

    return product


def get_cate_by_id(cate_id):
    return Category.query.get(cate_id)


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User.query.order_by(desc(User.id)).first()
    user_id = user.id + 1

    user = User(id=user_id,
                name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.flush()

    user_role = User_Role(id=user_id)

    privileged = Privileged(user_id=user_id,
                            user_role=user_id)

    db.session.add(user_role)
    db.session.flush()
    db.session.add(privileged)
    db.session.commit()


def add_staff(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User.query.order_by(desc(User.id)).first()
    user_id = user.id + 1

    user = User(id=user_id,
                name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.flush()

    user_role = User_Role(id=user_id,
                          view_customer=True,
                          receive_product=True,
                          login_admin=True,
                          view_receipt=True)

    privileged = Privileged(user_id=user_id,
                            user_role=user_id)

    db.session.add(user_role)
    db.session.flush()

    db.session.add(privileged)

    db.session.commit()


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def check_login_admin(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        user = User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()

        if user:
            user_permission = get_user_permission(user.id)

            if user_permission.User_Role.login_admin:
                return user

        return None


def login_without_pass(username):
    user = User.query.filter(User.username.__eq__(username.strip())).first()

    if user:
        user_permission = get_user_permission(user.id)

        if user_permission.User_Role.login_admin:
            return user


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_detail_admin(user_id):
    user = db.session.query(User.id,
                            User.name,
                            User.username,
                            User.password,
                            User.email,
                            User.active,
                            User.joined_date,
                            User.phone_number,
                            User.address,
                            User.avatar) \
        .filter(User.id == user_id).first()

    return user


def changes_user_info(user_id, **kwargs):
    user = get_user_by_id(user_id)
    user.name = kwargs.get('fullname')
    user.username = kwargs.get('username')
    user.email = kwargs.get('email')
    phone_number = kwargs.get('phone_number')
    address = kwargs.get('user_address')

    db.session.commit()


def count_cart(cart):
    total_quantity, total_amount, base_total_amount = 0, 0, 0

    try:
        if cart:
            for c in cart.values():
                id = int(c['id'])
                product = get_product_detail_info(id)
                print(f"Price: {c['price']}, Base Price: {product.price}")
                if product.discount_type.value == 1:
                    total_quantity += c['quantity']
                    total_amount += c['quantity'] * c['price']
                    base_total_amount += c['quantity'] * product.price

                elif product.discount_type.value == 2 and c['quantity'] > 1 and c['quantity'] % 2 == 0:
                    total_quantity += c['quantity']
                    total_amount += (c['quantity'] * c['price']) / 2
                    base_total_amount += c['quantity'] * c['price']

                elif product.discount_type.value == 2 and c['quantity'] > 1 and c['quantity'] % 2 != 0:
                    total_quantity += c['quantity']
                    total_amount += (math.floor(c['quantity'] / 2) + 1) * c['price']
                    base_total_amount += c['quantity'] * c['price']

                else:
                    total_quantity += c['quantity']
                    total_amount += c['quantity'] * c['price']
                    base_total_amount += c['quantity'] * c['price']

        return {
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'base_total_amount': base_total_amount
        }

    except Exception as e:
        return {'error': f'Lỗi server {str(e)}'}


def load_payment():
    payments = Payment.query.all()

    return payments


def load_brands():
    return Brand.query.all()


def add_receipt(cart, payment_id, delivery_address, customer_name):
    if cart:
        receipt = Receipt(user=current_user,
                          payment_id=payment_id,
                          delivery_address=delivery_address,
                          receiver_name=customer_name)
        db.session.add(receipt)

        for c in cart.values():
            id = int(c['id'])
            product = get_product_detail_info(id)

            if product.discount_type.value == 2 and c['quantity'] > 1:
                d = ReceiptDetail(receipt=receipt,
                                  product_id=int(c['id']),
                                  quantity=c['quantity'],
                                  unit_price=c['price'],
                                  discount=math.floor(c['quantity'] / 2) * c['price'],
                                  discount_info=c['promotion']
                                  )
            elif product.discount_type.value == 1:
                d = ReceiptDetail(receipt=receipt,
                                  product_id=int(c['id']),
                                  quantity=c['quantity'],
                                  unit_price=product.price,
                                  discount=(product.price - c['price']) * c['quantity'],
                                  discount_info=c['promotion']
                                  )

            else:
                d = ReceiptDetail(receipt=receipt,
                                  product_id=int(c['id']),
                                  quantity=c['quantity'],
                                  unit_price=c['price'], )
            db.session.add(d)

        db.session.commit()


def calculate_total_revenue():
    total_revenue = db.session.query(
        func.sum((ReceiptDetail.quantity * ReceiptDetail.unit_price) - func.coalesce(ReceiptDetail.discount, 0))
    ).join(Receipt, Receipt.id == ReceiptDetail.receipt_id)
    return total_revenue.scalar()


def count_total_check():
    total_check = db.session.query(func.count(Receipt.id)).scalar()
    return total_check


def count_complete_receipt():
    return db.session.query(func.count(Receipt.id)) \
        .filter(Receipt.status_id == 2).scalar()


def count_customer():
    return db.session.query(func.count(User.id)) \
        .filter(User.active == True).scalar()


def category_stats():
    '''
    SELECT C.id, c.name, count(p.id)
    FROM category c left outer join product p on c.id = p.category_id
    GROUP BY c.id, c.name
    '''

    # return Category.query.join(Product, Product.category_id.__eq__(Category.id), isouter=True)\
    #     .add_column(func.count(Product.id)).group_by(Category.id, Category.name).all()

    return db.session.query(Category.id, Category.name, func.count(Product.id)) \
        .join(Product, Category.id.__eq__(Product.category_id), isouter=True) \
        .group_by(Category.id, Category.name).all()


def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Product.id, Product.name, func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.product_id.__eq__(Product.id), isouter=True) \
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
        .group_by(Product.id, Product.name) \
        .order_by(Product.id)
    # .order_by( func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price))

    if kw:
        p = p.filter(Product.name.contains(kw))

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def product_months_stats(year):
    stats = db.session.query(extract('month', Receipt.created_date),
                             func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .outerjoin(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id)) \
        .filter(extract('year', Receipt.created_date) == year) \
        .group_by(extract('month', Receipt.created_date)) \
        .order_by(extract('month', Receipt.created_date)).all()

    monthly_data = {month: 0 for month in range(1, 13)}

    for month, total in stats:
        monthly_data[month] = total

    return [(month, monthly_data[month]) for month in range(1, 13)]


def product_profit_month_stats(year):
    stats = db.session.query(extract('month', Receipt.created_date),
                             func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price).label('total_revenue'),
                             func.sum(ReceiptDetail.quantity * Product.import_price).label('total_cost')) \
        .outerjoin(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id)) \
        .outerjoin(Product, Product.id.__eq__(ReceiptDetail.product_id)) \
        .filter(extract('year', Receipt.created_date) == year) \
        .group_by(extract('month', Receipt.created_date)) \
        .order_by(extract('month', Receipt.created_date)).all()

    monthly_data = {month: 0 for month in range(1, 13)}

    for month, total_revenue, total_cost in stats:
        monthly_data[month] = total_revenue - total_cost

    return [(month, monthly_data[month]) for month in range(1, 13)]


def customer_months_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.count(func.distinct(Receipt.user_id))) \
        .filter(extract('year', Receipt.created_date) == year) \
        .group_by(extract('month', Receipt.created_date)) \
        .order_by(extract('month', Receipt.created_date)).all()


def add_comment(content, product_id):
    c = Comment(content=content, product_id=product_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(product_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size

    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).slice(start,
                                                                                                   start + page_size).all()


def count_comment(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()


def load_provider():
    return Provider.query.all()


def get_provider_by_id(provider_id):
    provider = Provider.query.filter(Provider.id == provider_id).first()

    return provider


def load_distribution(product_id):
    if product_id:
        return Distribution.query.filter(Distribution.product_id.__eq__(product_id)).all()


def load_receipt(receipt_id=None, status_id=None, asc='True', page=1):
    receipts = db.session.query(
        Receipt.id,
        Receipt.status_id.label('status_id'),
        Receipt.delivery_address,
        Receipt.created_date,
        Receipt.exported,
        User.id.label('customer_id'),
        User.name.label('customer_name'),
        Payment.name.label('payment_name'),
        Receipt_Status.status_name.label('status_name'),
    ).join(User, Receipt.user_id == User.id) \
        .join(Payment, Receipt.payment_id == Payment.id) \
        .join(Receipt_Status, Receipt.status_id == Receipt_Status.id)

    if receipt_id:
        receipts = receipts.filter(Receipt.id.__eq__(receipt_id))

    if status_id:
        receipts = receipts.filter(Receipt.status_id.__eq__(status_id))

    if asc == 'False':
        receipts = receipts.order_by((Receipt.created_date))

    else:
        receipts = receipts.order_by(desc(Receipt.created_date))

    start = (page - 1) * app.config['VIEW_SIZE']
    end = start + app.config['VIEW_SIZE']

    return receipts.slice(start, end).all()


def get_receipt_by_id(receipt_id):
    receipt = db.session.query(
        Receipt.id,
        Receipt.status_id.label('status_id'),
        Receipt.delivery_address,
        Receipt.created_date,
        Receipt.exported,
        Receipt.payment_id,
        Payment.name.label('payment_name'),
        Payment.logo.label('payment_logo'),
        User.name.label('customer_name'),
    ).join(User, Receipt.user_id == User.id) \
        .join(Receipt_Status, Receipt_Status.id == Receipt.status_id)

    return receipt.filter(Receipt.id == receipt_id).first()


def get_receipt_by_id_2(receipt_id):
    receipt = db.session.query(
        Receipt.id,
        Receipt.created_date,
        Receipt.status_id,
        Receipt.promotion_id,
        Receipt.delivery_address,
        Receipt.receiver_name,
        Receipt_Status.status_name.label("status_name"),
        Payment.name.label("payment_name"),
        Payment.logo.label("payment_logo"),
        Payment.id).join(Payment, Payment.id == Receipt.payment_id) \
        .join(Receipt_Status, Receipt_Status.id == Receipt.status_id) \
        .filter(Receipt.id == receipt_id).first()

    return receipt


def load_receipt_detail(receipt_id, product_id=None, product_name=None):
    calculate_warranty_valid(receipt_id)

    receipt_details = db.session.query(
        ReceiptDetail.receipt_id,
        ReceiptDetail.product_id,
        ReceiptDetail.quantity,
        ReceiptDetail.unit_price,
        ReceiptDetail.discount,
        ReceiptDetail.discount_info,
        ReceiptDetail.on_warranty,
        WarrantyDetail.warranty_period.label('warranty_period'),
        WarrantyDetail.time_unit.label('time_unit'),
        Product.name.label('product_name'),
        Product.image.label('product_image')
    ).join(Product, Product.id == ReceiptDetail.product_id) \
        .outerjoin(WarrantyDetail, WarrantyDetail.product_id == ReceiptDetail.product_id) \
        .filter(ReceiptDetail.receipt_id.__eq__(receipt_id))

    receipt_details = receipt_details.distinct()

    base_total_price = sum(detail.quantity * detail.unit_price for detail in receipt_details)

    total_price = base_total_price
    for detail in receipt_details:
        if detail.discount:
            total_price -= detail.discount

    if product_id:
        receipt_details = receipt_details.filter(ReceiptDetail.product_id.__eq__(product_id))

    if product_name:
        receipt_details = receipt_details.filter(Product.name.contains(product_name))

    return receipt_details.all(), total_price, base_total_price


def load_receipt_status():
    return Receipt_Status.query.all()


def get_user_receipt(user_id, receipt_id=None, status_id=None, asc=True):
    user_receipt = db.session.query(
        Receipt.id,
        Receipt.created_date,
        Receipt.status_id,
        Receipt.delivery_address,
        Payment.name.label('payment_name'),
        Payment.logo.label('payment_logo'),
        Receipt_Status.status_name.label('status_name')
    ).join(Payment, Receipt.payment_id == Payment.id) \
        .join(Receipt_Status, Receipt.status_id == Receipt_Status.id)

    user_receipt = user_receipt.filter(Receipt.user_id == user_id)

    if receipt_id:
        user_receipt = user_receipt.filter(Receipt.id.__eq__(receipt_id))

    if status_id:
        user_receipt = user_receipt.filter(Receipt.status_id.__eq__(status_id))

    if asc == 'False':
        user_receipt = user_receipt.order_by((Receipt.created_date))

    else:
        user_receipt = user_receipt.order_by(desc(Receipt.created_date))

    return user_receipt.all()


def load_report_types():
    report_types = Report_Type.query.all()

    return report_types


def get_need_confirm_receipt(user_id):
    need_confirm_receipt = Receipt.query.filter(Receipt.user_id.__eq__(user_id),
                                                Receipt.status_id == 5).first()

    if need_confirm_receipt:
        return True

    return False


def confirm_receipt(receipt_id):
    receipt = Receipt.query.filter(Receipt.id == receipt_id).first()
    receipt.status_id = 1
    db.session.commit()


def complete_receipt(receipt_id):
    receipt = Receipt.query.filter(Receipt.id == (receipt_id)).first()
    receipt.status_id = 2

    db.session.commit()


def get_user_permission(user_id):
    user_permission = db.session.query(
        User.id,
        User_Role.privileged.label('user_privileged'),
        Privileged,
        User_Role
    ).join(Privileged, Privileged.user_id == User.id) \
        .join(User_Role, User_Role.id == Privileged.user_role) \
        .filter(User.id == user_id).first()

    return user_permission


def get_user_role_permission(user_id):
    user_role_permission = db.session.query(User_Role.privileged.label('user_privileged'),
                                            User_Role) \
        .join(Privileged, Privileged.user_role == User_Role.id) \
        .filter(Privileged.user_id == user_id).first()

    return user_role_permission


def load_user(user_id=None, asc='False', active=None, page=1, info=None):
    users = db.session.query(User)

    if user_id:
        users = users.filter(User.id == user_id)

    if asc == 'True':
        users = users.order_by((User.joined_date))

    else:
        users = users.order_by(desc(User.joined_date))

    if active is not None:
        if active == 'True':
            users = users.filter(User.active == True)
        elif active == 'False':
            users = users.filter(User.active == False)

    if info:
        users = users.filter(or_(User.id == int(info), User.phone_number.contains(info)))

    start = (page - 1) * app.config['VIEW_SIZE']
    end = start + app.config['VIEW_SIZE']

    return users.slice(start, end).all()


def load_user_role():
    users_role = User_Role.query.all()

    return users_role


def load_receipt_report():
    receipts_report = Receipt_Report.query.all()

    return receipts_report


def generate_code(prefix):
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    return prefix + random_part


def generate_delivery():
    while True:
        code = generate_code("DP04")
        if Goods_Delivery_Note.query.filter(Goods_Delivery_Note.code == code).first() is None:
            break

    return code


def generate_receive():
    while True:
        code = generate_code("RP04")
        if Goods_Received_Note.query.filter(Goods_Received_Note.code == code).first() is None:
            break

    return code


def create_receive_note(code, products_data, **kwargs):
    receive_note = Goods_Received_Note(
        code=code,
        order_date=kwargs.get('order_date'),
        provider_id=kwargs.get('provider_id'),
        total_price=kwargs.get('total_price')
    )

    for p in products_data:
        received_detail = Goods_Received_Note_Detail(
            goods_received_note_code=code,
            product_id=p['product'].id,
            quantity=p['quantity'],
            note=p['note']
        )

        db.session.add(received_detail)

    db.session.add(receive_note)
    db.session.commit()


def load_goods_received_note(received_note_code=None, confirmed=None, asc='False', page=1):
    g_note = db.session.query(Goods_Received_Note,
                              Provider.name.label('provider_name'),
                              Provider.address.label('provider_address'),
                              User.name.label('user_name_confirm')) \
        .outerjoin(Provider, Provider.id == Goods_Received_Note.provider_id) \
        .outerjoin(User, User.id == Goods_Received_Note.user_confirm)

    if received_note_code:
        g_note = g_note.filter(Goods_Received_Note.code.contains(received_note_code))

    if confirmed is not None:
        if confirmed == 'True':
            g_note = g_note.filter(Goods_Received_Note.confirmed == True)
        elif confirmed == 'False':
            g_note = g_note.filter(Goods_Received_Note.confirmed == False)

    if asc == 'False':
        g_note = g_note.order_by(Goods_Received_Note.order_date)

    else:
        g_note = g_note.order_by(desc(Goods_Received_Note.order_date))

    start = (page - 1) * app.config['VIEW_SIZE']
    end = start + app.config['VIEW_SIZE']

    return g_note.slice(start, end).all()


def get_goods_received_note(received_note_code):
    return db.session.query(Goods_Received_Note,
                            Provider.name.label('provider_name'),
                            Provider.address.label('provider_address'),
                            User.name.label('user_name_confirm')) \
        .outerjoin(Provider, Provider.id == Goods_Received_Note.provider_id) \
        .outerjoin(User, User.id == Goods_Received_Note.user_confirm) \
        .filter(Goods_Received_Note.code == received_note_code).first()


def get_goods_received_note_detail(received_note_code):
    total_value = db.session.query(
        func.sum(Goods_Received_Note_Detail.quantity * Product.import_price)
    ).join(
        Product, Goods_Received_Note_Detail.product_id == Product.id
    ).filter(
        Goods_Received_Note_Detail.goods_received_note_code == received_note_code
    ).scalar()

    return db.session.query(Goods_Received_Note_Detail,
                            Product.name.label('product_name'),
                            Product.import_price.label('product_import_price')) \
        .join(Product, Goods_Received_Note_Detail.product_id == Product.id) \
        .filter(Goods_Received_Note_Detail.goods_received_note_code == received_note_code).all()


def update_received_note_detail(goods_received_code, product_id, quantity):
    g_detail = Goods_Received_Note_Detail.query \
        .filter(and_(Goods_Received_Note_Detail.goods_received_note_code == goods_received_code,
                     Goods_Received_Note_Detail.product_id == product_id)).first()

    g_detail.received_quantity = quantity
    db.session.commit()


def update_g_note_delivery_man(delivery_man, goods_received_code):
    g_note = Goods_Received_Note.query.filter(Goods_Received_Note.code == goods_received_code).first()

    g_note.delivery_man = delivery_man

    db.session.commit()


def complete_received_note(goods_received_code):
    g_note = Goods_Received_Note.query.filter(Goods_Received_Note.code == goods_received_code).first()

    g_note.confirmed = True
    g_note.confirm_date = datetime.now()
    g_note.user_confirm = current_user.id

    db.session.commit()


def load_delivery_reason():
    reason = Delivery_Reason.query.all()

    return reason


def load_delivery_note(delivery_code=None, confirmed=None, asc='False', reason=None, delivery_man_id=None, page=1):
    user_created_alias = aliased(User)
    delivery_man_alias = aliased(User)

    delivery_notes = db.session.query(Goods_Delivery_Note,
                                      Delivery_Reason.name.label('delivery_reason'),
                                      user_created_alias.name.label('user_created'),
                                      delivery_man_alias.name.label('delivery_man')) \
        .join(Delivery_Reason, Delivery_Reason.id == Goods_Delivery_Note.reason) \
        .join(user_created_alias, user_created_alias.id == Goods_Delivery_Note.user_created) \
        .join(delivery_man_alias, delivery_man_alias.id == Goods_Delivery_Note.delivery_man)

    if delivery_code:
        delivery_notes = delivery_notes.filter(Goods_Delivery_Note.code.contains(delivery_code))

    if confirmed:
        if confirmed == "True":
            delivery_notes = delivery_notes.filter(Goods_Delivery_Note.confirmed.__eq__(True))
        elif confirmed == "False":
            delivery_notes = delivery_notes.filter(Goods_Delivery_Note.confirmed.__eq__(False))

    if reason:
        delivery_notes = delivery_notes.filter(Goods_Delivery_Note.reason == reason)

    if delivery_man_id:
        delivery_notes = delivery_notes.filter(Goods_Delivery_Note.delivery_man.contains(delivery_man_id))

    # Sắp xếp theo asc
    if asc == 'False':
        delivery_notes = delivery_notes.order_by(Goods_Delivery_Note.created_date)
    else:
        delivery_notes = delivery_notes.order_by(desc(Goods_Delivery_Note.created_date))

    start = (page - 1) * app.config['VIEW_SIZE']
    end = start + app.config['VIEW_SIZE']

    return delivery_notes.slice(start, end).all()


def create_delivery_note(delivery_code, products_data, **kwargs):
    if kwargs.get('receipt_id'):
        receipt_id = kwargs.get('receipt_id')
        receipt = Receipt.query.filter(Receipt.id == receipt_id).first()
        receipt.exported = True

    else:
        receipt_id = None

    goods_delivery_note = Goods_Delivery_Note(code=delivery_code,
                                              created_date=kwargs.get('created_date'),
                                              reason=kwargs.get('delivery_reason'),
                                              user_created=current_user.id,
                                              total_price=kwargs.get('total_price'),
                                              confirmed=kwargs.get('confirmed', False),
                                              confirm_date=kwargs.get('confirm_date', None),
                                              delivery_man=kwargs.get('delivery_man_id'),
                                              delivery_address=kwargs.get('delivery_address'),
                                              for_receipt_id=receipt_id
                                              )

    for product in products_data:
        goods_delivery_note_detail = Goods_Delivery_Note_Detail(
            goods_delivery_note_code=delivery_code,
            product_id=product['product_id'],
            quantity=product['base_quantity'],
            delivered_quantity=product['delivered_quantity'],
            note=product['note']
        )

        db.session.add(goods_delivery_note_detail)

    db.session.add(goods_delivery_note)
    db.session.commit()


def update_delivery_note(delivery_code, products_data, **kwargs):
    if kwargs.get('receipt_id'):
        receipt_id = kwargs.get('receipt_id')
        receipt = Receipt.query.filter(Receipt.id == receipt_id).first()
        receipt.exported = True

    else:
        receipt_id = None

    g_note = Goods_Delivery_Note.query.filter(Goods_Delivery_Note.code == delivery_code).first()

    g_note.delivery_man = kwargs.get('delivery_man_id')
    g_note.delivery_address = kwargs.get('delivery_address')

    for product in products_data:
        goods_delivery_note_detail = Goods_Delivery_Note_Detail.query \
            .filter(and_(Goods_Delivery_Note_Detail.goods_delivery_note_code == delivery_code,
                         Goods_Delivery_Note_Detail.product_id == product['product_id'])) \
            .first()

        goods_delivery_note_detail.delivered_quantity = product['delivered_quantity']

    db.session.commit()


def load_delivery_note_details(delivery_code):
    delivery_details = db.session.query(
        Goods_Delivery_Note_Detail.product_id,
        Goods_Delivery_Note_Detail.quantity,
        Goods_Delivery_Note_Detail.delivered_quantity,
        Product.id.label('product_id'),
        Product.name.label('product_name'),
        Product.price.label('product_price')
    ).join(Product, Product.id == Goods_Delivery_Note_Detail.product_id) \
        .filter(Goods_Delivery_Note_Detail.goods_delivery_note_code.__eq__(delivery_code))

    total_price = sum(detail.quantity * detail.product_price for detail in delivery_details)

    total_price2 = sum(detail.delivered_quantity * detail.product_price for detail in delivery_details)

    return delivery_details.all(), total_price, total_price2


def get_delivery_note(delivery_code=None, receipt_id=None):
    if delivery_code:
        return Goods_Delivery_Note.query.filter(Goods_Delivery_Note.code == delivery_code).first()

    elif receipt_id:
        return Goods_Delivery_Note.query.filter(Goods_Delivery_Note.for_receipt_id == receipt_id).first()


def confirm_delivery_note(delivery_code, products_data, **kwargs):
    if kwargs.get('receipt_id'):
        receipt_id = kwargs.get('receipt_id')
        receipt = Receipt.query.filter(Receipt.id == receipt_id).first()
        receipt.exported = True

    else:
        receipt_id = None

    g_note = Goods_Delivery_Note.query.filter(Goods_Delivery_Note.code == delivery_code).first()
    g_note.confirmed = True
    g_note.confirm_date = datetime.now()
    g_note.delivery_man = kwargs.get('delivery_man_id')
    g_note.delivery_address = kwargs.get('delivery_address')

    for product in products_data:
        goods_delivery_note_detail = Goods_Delivery_Note_Detail.query \
            .filter(and_(Goods_Delivery_Note_Detail.goods_delivery_note_code == delivery_code,
                         Goods_Delivery_Note_Detail.product_id == product['product_id'])) \
            .first()

        goods_delivery_note_detail.delivered_quantity = product['delivered_quantity']

    db.session.commit()


def check_category_id(category_id):
    category = Category.query.filter(Category.id == category_id).first()

    if category:
        return True

    else:
        return False


def check_change_category_id(base_id, category_id):
    if base_id == category_id:
        return False

    category = Category.query.filter(Category.id == category_id).first()

    if category:
        return True

    else:
        return False


def create_category(cate_id, cate_name):
    category = Category(id=cate_id,
                        name=cate_name)

    db.session.add(category)
    db.session.commit()


def is_id_exists(generated_id):
    try:
        # Kiểm tra xem ID có tồn tại trong bảng Product không
        existing_product = db.session.query(Product).filter_by(id=generated_id).one()
        return True  # ID tồn tại
    except NoResultFound:
        return False  # ID không tồn tại
    except Exception as e:
        print(f"Error checking ID: {e}")
        return False


def generate_id():
    while True:
        random_part = random.randint(100, 999)
        generated_id = int(f"630{random_part}")

        # Kiểm tra xem ID đã tồn tại chưa
        if not is_id_exists(generated_id):
            return generated_id


def resize_image(image, size=(600, 600)):
    img = Image.open(image)
    img = img.resize(size)
    return img


def add_product(product_name, **kwargs):
    image_path = kwargs.get('image', "")
    product_id = generate_id()
    product = Product(
        id=product_id,
        name=product_name,
        description=kwargs.get('description'),
        category_id=kwargs.get('category_id'),
        brand_id=kwargs.get('brand_id'),
        import_price=kwargs.get('import_price'),
        price=kwargs.get('price'),
        image=image_path,
        warranty=kwargs.get('warranty', 0),
        promotion_id=kwargs.get('promotion_id', 3)
    )

    distribution = Distribution(
        product_id=product_id,
        provider_id=kwargs.get('provider_id')
    )

    try:
        db.session.add(product)
        db.session.add(distribution)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving product: {e}")
        return False


def get_product_by_provider(provider_id):
    products = db.session.query(Product.id,
                                Product.name) \
        .join(Distribution, Product.id == Distribution.product_id) \
        .filter(Distribution.provider_id == provider_id)

    return products.all()


def get_address():
    districts = District.query.order_by(
        # Sắp xếp dựa trên số quận (nếu có)
        func.cast(func.substring(District.name, 6), Integer).asc(),
        # Sau đó sắp xếp theo bảng chữ cái với phần sau từ "Quận"
        func.substring(District.name, 6).asc()
    ).all()

    ward = Ward.query.all()

    return districts, ward


def get_promotion(kw=None, expired=None, current_time=datetime.now()):
    promotion = Promotion.query
    if kw:
        if kw.isdigit():
            promotion = promotion.filter(Promotion.id == int(kw))
        else:
            promotion = promotion.filter(Promotion.id.contains(kw))

    if expired:
        if expired == 'True':
            promotion = promotion.filter(Promotion.end_date.__le__(current_time))

        elif expired == 'False':
            promotion = promotion.filter(Promotion.end_date.__ge__(current_time))

    return promotion.all()


def get_promotion_detail(promotion_id):
    return PromotionDetail.query.filter(Promotion.id == promotion_id).first()


def get_product_with_promotion(promotion_id):
    products_with_promotion = db.session.query(Product.id,
                                               Product.name,
                                               Product.price,
                                               Product.import_price,
                                               Product.description,
                                               PromotionDetail.discount_value.label('discount_value'),
                                               PromotionDetail.discount_type.label('discount_type')) \
        .join(PromotionDetail, PromotionDetail.product_id == Product.id) \
        .filter(PromotionDetail.promotion_id.__eq__(promotion_id)).all()

    subquery = db.session.query(PromotionDetail.product_id) \
        .filter(PromotionDetail.promotion_id == promotion_id).subquery()

    products_not_applied = Product.query.filter(Product.id.notin_(subquery)).all()

    return products_with_promotion, products_not_applied


def update_product(product_id, **kwargs):
    product = Product.query.filter(Product.id == product_id).first()

    try:
        product.name = kwargs.get('product_name'),
        product.price = kwargs.get('price'),
        product.category_id = kwargs.get('category_id'),
        product.import_price = kwargs.get('import_price')

        db.session.commit()
        return "Cập nhật thông tin sản phẩm thành công"

    except Exception as e:
        db.session.rollback()
        return str(e)


def duplicate_product_with_new_id(product_id, up_product_id, **kwargs):
    try:
        # Lấy sản phẩm cũ
        old_product = Product.query.filter(Product.id == product_id).first()
        if not old_product:
            return f"Không tìm thấy Product {product_id}"

        # Tạo sản phẩm mới với ID mới
        new_product = Product(
            id=up_product_id,
            name=kwargs.get('product_name'),
            description=old_product.description,
            price=kwargs.get('price'),
            image=old_product.image,
            active=old_product.active,
            created_date=old_product.created_date,
            rating=old_product.rating,
            category_id=kwargs.get('category_id'),
            brand_id=old_product.brand_id,
            import_price=kwargs.get('import_price'),
            warranty=old_product.warranty
        )

        db.session.add(new_product)
        db.session.flush()

        Distribution.query.filter(Distribution.product_id == product_id).update({'product_id': up_product_id})
        ReceiptDetail.query.filter(ReceiptDetail.product_id == product_id).update({'product_id': up_product_id})
        Goods_Received_Note_Detail.query.filter(Goods_Received_Note_Detail.product_id == product_id).update(
            {'product_id': up_product_id})
        Goods_Delivery_Note_Detail.query.filter(Goods_Delivery_Note_Detail.product_id == product_id).update(
            {'product_id': up_product_id})
        PromotionDetail.query.filter(PromotionDetail.product_id == product_id).update({'product_id': up_product_id})

        db.session.delete(old_product)

        db.session.commit()

        return "Cập nhật thông tin sản phẩm thành công"

    except Exception as e:
        db.session.rollback()
        return str(e)


def send_email(subject, body, to_email):
    smtp_server = 'smtp.gmail.com'  # serversmtp gửi mail
    smtp_port = 587  # port mặc định gửi mail
    from_email = 'tuanthai17122004@gmail.com'  # mail người gửi
    from_password = 'kpkj hals ihln gppg'  # mật khẩu ứng dụng google

    msg = MIMEMultipart()
    # MIMEMultipart: Tạo một đối tượng email đa phần, cho phép bạn đính kèm các phần khác nhau
    # (như văn bản, tệp đính kèm, hình ảnh) vào email.

    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    # Thiết lập các trường cơ bản của email bao gồm người gửi, người nhận và tiêu đề.

    # attach Thêm nội dung vào email
    msg.attach(MIMEText(body, 'plain'))
    # Chỉ định kiểu nội dung là văn bản thuần túy ( plain ) không phải HTML.

    try:
        # Kết nối máy chủ SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Bắt đầu kết nối TLS để bảo mật
        server.login(from_email, from_password)

        # Gửi email
        server.send_message(msg)
        print("Email đã được gửi thành công!")

        server.quit()

    except Exception as e:
        print(f"Không thể gửi email. Lỗi: {e}")

    # Sử dụng hàm gửi email
    # code = generate_id()
    # subject = "Mail khôi phục mật khẩu"
    # body = f'{code} là mã khôi phục mật khẩu của bạn, vui lòng không chia sẻ với bất kỳ ai'
    # to_email = "titofood17122004@gmail.com"
    # subjetc: tiêu đề mai;
    # body: nội dung mail
    # to_email: mail người nhận
    # send_email(subject, body, to_email)


def check_restore_email_validation(username, email):
    user = User.query.filter(and_(User.username == username), (User.email == email)).first()

    if user:
        return True

    return False


def change_user_info(user_id, **kwargs):
    try:
        user = User.query.filter(User.id == user_id).first()

        if not user:
            return {"success": False, "message": "Không tìm thấy người dùng"}
        for key, value in kwargs.items():
            print(key, value)

        user.name = kwargs.get('name')
        user.username = kwargs.get('username')
        user.email = kwargs.get('email')
        user.phone_number = kwargs.get('phone_number')
        user.address = kwargs.get('address')
        db.session.commit()

        return {"success": True, "message": "Cập nhật thông tin thành công"}
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}


def load_product_warranty(product_id):
    warranty = db.session.query(Warranty.description,
                                WarrantyDetail.product_id,
                                WarrantyDetail.warranty_period,
                                WarrantyDetail.time_unit) \
        .join(WarrantyDetail, Warranty.id == WarrantyDetail.warranty_id) \
        .filter(WarrantyDetail.product_id == product_id).all()
    return warranty


def load_warranty(info=None):
    warranty = Warranty.query
    if info:
        if info.isdigit():
            warranty = warranty.filter(Warranty.id == int(info))
        else:
            warranty = warranty.filter(Warranty.description.contains(info))
    return warranty.all()


def get_warranty(warranty_id):
    return Warranty.query.filter(Warranty.id == warranty_id).first()


def get_void_warranty_detail(warranty_id):
    return db.session.query(Warranty.description.label('warranty_description'),
                            Warranty.id.label('warranty_id')) \
        .filter(Warranty.id == warranty_id).all()


def get_warranty_detail(warranty_id):
    warranty_detail = db.session.query(Warranty.description.label('warranty_description'),
                                       Product.id.label('product_id'),
                                       Product.name.label('product_name'),
                                       WarrantyDetail.warranty_id,
                                       WarrantyDetail.warranty_period,
                                       WarrantyDetail.time_unit) \
        .outerjoin(Warranty, Warranty.id == WarrantyDetail.warranty_id) \
        .outerjoin(Product, Product.id == WarrantyDetail.product_id) \
        .filter(WarrantyDetail.warranty_id == warranty_id)

    return warranty_detail.all()


def calculate_warranty_valid(receipt_id):
    receipt = Receipt.query.filter(Receipt.id == receipt_id).first()

    if not receipt:
        return {"success": False, "message": "Receipt không tồn tại."}

    created_date = receipt.created_date

    receipt_details = db.session.query(ReceiptDetail,
                                       WarrantyDetail.warranty_period,
                                       WarrantyDetail.time_unit) \
        .join(WarrantyDetail, ReceiptDetail.product_id == WarrantyDetail.product_id) \
        .filter(ReceiptDetail.receipt_id == receipt.id).all()

    if receipt_details:
        for detail, warranty_period, time_unit in receipt_details:
            if time_unit == TimeUnitEnum.YEAR:
                warranty_end_date = created_date + relativedelta(years=warranty_period)
            elif time_unit == TimeUnitEnum.MONTH:
                warranty_end_date = created_date + relativedelta(months=warranty_period)
            elif time_unit == TimeUnitEnum.WEEK:
                warranty_end_date = created_date + timedelta(weeks=warranty_period)
            else:
                continue

            if datetime.now() <= warranty_end_date:
                detail.on_warranty = True
            else:
                detail.on_warranty = False
        else:
            detail = ReceiptDetail
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Lỗi: {str(e)}"}


def apply_warranty_for_all(warranty_id, warranty_period, time_unit):
    products = Product.query.all()
    try:
        for product in products:
            warranty_detail = WarrantyDetail(
                product_id=product.id,
                warranty_id=warranty_id,
                warranty_period=int(warranty_period),
                time_unit=TimeUnitEnum[time_unit]
            )
            db.session.add(warranty_detail)
        db.session.commit()
        return {'success': True}

    except Exception as e:
        return {'success': False, 'msg': f'Lỗi xảy ra {str(e)}'}


def delete_warranty(warranty_id):
    warranty = Warranty.query.get(warranty_id)

    warranty_details = WarrantyDetail.query.filter(WarrantyDetail.warranty_id == warranty_id).all()

    for detail in warranty_details:
        db.session.delete(detail)

    db.session.delete(warranty)

    db.session.commit()


def delete_promotion(promotion_id):
    try:
        promotion = Promotion.query.get(promotion_id)

        promotion_details = PromotionDetail.query.filter(PromotionDetail.promotion_id == promotion_id).all()

        for detail in promotion_details:
            db.session.delete(detail)

        db.session.delete(promotion)

        db.session.commit()

        return {"success": True, "message": "Đã xóa chương trình khuyến mãi !"}

    except Exception as e:
        return {"success": False, "message": f'Lỗi: {str(e)}'}


def load_product_applied_warranty_yet(warranty_id):
    subquery = db.session.query(WarrantyDetail.product_id) \
        .filter(WarrantyDetail.warranty_id == warranty_id).subquery()

    products = Product.query.filter(Product.id.notin_(subquery)).all()

    return products


def load_product_applied_promotion_yet(promotion_id):
    subquery = db.session.query(WarrantyDetail.product_id) \
        .filter(PromotionDetail.promotion_id == promotion_id).subquery()

    products = Product.query.filter(Product.id.notin_(subquery)).all()

    return products


def apply_warranty(product_id, warranty_id, warranty_period, time_unit):
    warranty_detail = WarrantyDetail(
        product_id=product_id,
        warranty_id=warranty_id,
        warranty_period=warranty_period,
        time_unit=TimeUnitEnum[time_unit]
    )

    db.session.add(warranty_detail)
    db.session.commit()


def delete_warranty_detail(warranty_id, product_id):
    detail = WarrantyDetail.query.filter(
        and_(WarrantyDetail.warranty_id == warranty_id, WarrantyDetail.product_id == product_id)).first()

    db.session.delete(detail)
    db.session.commit()


def update_warranty_detail(warranty_id, product_id, period, time_unit):
    detail = WarrantyDetail.query.filter(
        and_(WarrantyDetail.warranty_id == warranty_id, WarrantyDetail.product_id == product_id)).first()

    if not detail:
        raise Exception("Không tìm thấy thông tin bảo hành cho sản phẩm này.")

    detail.warranty_period = period
    try:
        detail.time_unit = time_unit
    except KeyError:
        raise Exception("Giá trị time_unit không hợp lệ.")

    db.session.commit()


# ------------- BUSINESS STATS ---------------

def get_revenue_data():
    receipts_data = db.session.query(
        Receipt.id,
        Receipt.created_date,
        func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price - coalesce(ReceiptDetail.discount, 0)) \
            .label("total_amount")) \
        .outerjoin(ReceiptDetail) \
        .group_by(Receipt.id).all()

    data = pd.DataFrame(receipts_data, columns=['id', 'created_date', 'total_amount'])
    data['created_date'] = pd.to_datetime(data['created_date'])

    return data


def calculate_revenue_statistics():
    data = get_revenue_data()  # receipt data list
    data['year'] = data['created_date'].dt.year
    data['month'] = data['created_date'].dt.month
    data['quarter'] = data['created_date'].dt.quarter

    # Total revenue by year
    revenue_yearly = data.groupby('year')['total_amount'].sum().reset_index()

    # Total revenue by month
    revenue_monthly = data.groupby(['year', 'month'])['total_amount'].sum().reset_index()

    # Total revenue by quarter
    revenue_quarterly = data.groupby(['year', 'quarter'])['total_amount'].sum().reset_index()

    # Average revenue
    avg_revenue_monthly = data.groupby(['year', 'month'])['total_amount'].sum().groupby('year').mean().reset_index()
    avg_revenue_monthly.columns = ['year', 'avg_revenue_monthly']

    avg_revenue_quarterly = data.groupby(['year', 'quarter'])['total_amount'].sum().groupby('year').mean().reset_index()
    avg_revenue_quarterly.columns = ['year', 'avg_revenue_quarterly']

    return {
        'revenue_yearly': revenue_yearly.astype('int32'),
        'revenue_monthly': revenue_monthly.astype('int32'),
        'revenue_quarterly': revenue_quarterly.astype('int32'),
        'avg_revenue_monthly': avg_revenue_monthly.astype('int32'),
        'avg_revenue_quarterly': avg_revenue_quarterly.astype('int32'),
    }


def calculate_discount_statistics():
    discounts_data = db.session.query(Receipt.id,
                                      Receipt.created_date,
                                      func.sum(coalesce(ReceiptDetail.discount, 0).label("total_discount"))) \
        .join(ReceiptDetail).group_by(Receipt.id).all()

    discounts_data = pd.DataFrame(discounts_data, columns=['id', 'created_date', 'total_discount'])
    discounts_data['created_date'] = pd.to_datetime((discounts_data['created_date']))

    discounts_data['year'] = discounts_data['created_date'].dt.year
    discount_yearly = discounts_data.groupby('year')['total_discount'].sum().reset_index()

    return {
        'discount_data': discounts_data,
        'discount_yearly': discount_yearly
    }


def format_amount(value, tick_number):
    return f'{int(value):,}'


def visualize_revenue_statistics(statistics):
    plt.figure(figsize=(8, 5))
    bars = plt.bar(statistics['revenue_yearly']['year'], statistics['revenue_yearly']['total_amount'].astype('int32'),
                   color='r', alpha=0.7)
    plt.title('Total Revenue by Year')
    plt.xlabel('Year')
    plt.ylabel('Total Revenue')
    plt.grid(axis='y')
    plt.xticks(statistics['revenue_yearly']['year'])

    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_amount))

    for bar in bars:
        y_value = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, y_value, f'{int(y_value):,}đ', ha='center', va='bottom')

    image_path = os.path.join('static', 'images', 'statistics', 'revenue_chart.png')
    plt.savefig(image_path)
    plt.close()

    return image_path


def get_total_receive_and_delivery():
    received_amount = db.session.query(
        Goods_Received_Note_Detail.product_id,
        Product.name.label("product_name"),
        func.sum(coalesce(Goods_Received_Note_Detail.quantity, 0)).label('total_quantity_ordered'),
        func.sum(coalesce(Goods_Received_Note_Detail.received_quantity, 0)).label('total_quantity_received'),
        literal_column("0").label("total_quantity_sold"),
        literal_column("0").label("total_quantity_delivered")
    ).join(Goods_Received_Note, Goods_Received_Note_Detail.goods_received_note_code == Goods_Received_Note.code) \
        .outerjoin(Product, Product.id == Goods_Received_Note_Detail.product_id) \
        .group_by(Goods_Received_Note_Detail.product_id, Product.name)

    delivery_amount = db.session.query(
        Goods_Delivery_Note_Detail.product_id,
        Product.name.label("product_name"),
        literal_column("0").label("total_quantity_ordered"),
        literal_column("0").label("total_quantity_received"),
        func.sum(coalesce(Goods_Delivery_Note_Detail.quantity, 0)).label('total_quantity_sold'),
        func.sum(coalesce(Goods_Delivery_Note_Detail.delivered_quantity, 0)).label('total_quantity_delivered')
    ).join(Goods_Delivery_Note, Goods_Delivery_Note_Detail.goods_delivery_note_code == Goods_Delivery_Note.code) \
        .outerjoin(Product, Product.id == Goods_Delivery_Note_Detail.product_id) \
        .group_by(Goods_Delivery_Note_Detail.product_id, Product.name)

    total_amount = received_amount.union_all(delivery_amount).subquery()

    results = db.session.query(total_amount.c.goods_received_note_detail_product_id,
                               total_amount.c.product_name,
                               func.sum(total_amount.c.total_quantity_ordered).label("total_quantity_ordered"),
                               func.sum(total_amount.c.total_quantity_received).label("total_quantity_received"),
                               func.sum(total_amount.c.total_quantity_sold).label("total_quantity_sold"),
                               func.sum(total_amount.c.total_quantity_delivered).label("total_quantity_delivered")
                               ).group_by(total_amount.c.goods_received_note_detail_product_id,
                                          total_amount.c.product_name).all()

    return results


def update_promotion(promotion_id=None, description=None, end_date=None):
    promotion = Promotion.query.filter(Promotion.id == promotion_id).first()

    if promotion:
        if description:
            promotion.description = description

        if end_date:
            promotion.end_date = end_date

        db.session.commit()
        return {'success': True, 'msg': 'Thay đổi thông tin chương trình khuyến mãi thành công'}

    else:
        db.session.rollback()
        return {'success': False, 'msg': 'Không tìm thấy mã chương trình khuyến mãi'}


def apply_promotion_for_all(promotion_id, discount_type, discount_value):
    products = Product.query.all()
    try:
        for product in products:
            promotion_detail = PromotionDetail(
                product_id=product.id,
                promotion_id=promotion_id,
                discount_type=DiscountType[discount_type],
                discount_value=discount_value
            )
            db.session.add(promotion_detail)
        db.session.commit()
        return {'success': True}

    except Exception as e:
        return {'success': False, 'msg': f'Lỗi xảy ra {str(e)}'}


def apply_promotion_to_product(promotion_id, product_id, discount_value, discount_type):
    try:
        new_promotion_detail = PromotionDetail(product_id=product_id,
                                               promotion_id=promotion_id,
                                               discount_value=discount_value,
                                               discount_type=DiscountType[discount_type])

        db.session.add(new_promotion_detail)
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error utils: {e}")
        return False


def calculate_revenue_before_promotion(promotion_id):
    promotion = Promotion.query.filter(Promotion.id == promotion_id).first()

    if not promotion:
        return {"error": "Không tìm thấy chương trình khuyến mãi"}

    product_on_promotion = db.session.query(PromotionDetail.product_id) \
        .filter(PromotionDetail.promotion_id == promotion_id).subquery()

    promotion_duration = (promotion.end_date - promotion.start_date).days

    start_date_before = (promotion.start_date - timedelta(days=promotion_duration))  # trừ ngày trả về ngày bắt đầu tính

    total_revenue_before_promotion = db.session.query(
        func.sum((ReceiptDetail.unit_price * ReceiptDetail.quantity)).label(
            'total_revenue')) \
                                         .join(Receipt, Receipt.id == ReceiptDetail.receipt_id) \
                                         .filter(ReceiptDetail.product_id.in_(product_on_promotion),
                                                 Receipt.created_date >= start_date_before,
                                                 Receipt.created_date < promotion.start_date).scalar() or 0

    return total_revenue_before_promotion


def calculate_promotion_revenue(promotion_id):
    promotion = Promotion.query.filter(Promotion.id == promotion_id).first()

    if not promotion:
        return {"error": "Không tìm thấy chương trình khuyến mãi"}

    product_on_promotion = db.session.query(PromotionDetail.product_id) \
        .filter(PromotionDetail.promotion_id == promotion_id).subquery()

    total_revenue = db.session.query(
        func.sum((ReceiptDetail.unit_price * ReceiptDetail.quantity) - coalesce(ReceiptDetail.discount, 0)).label(
            'total_revenue')) \
                        .join(Receipt, Receipt.id == ReceiptDetail.receipt_id) \
                        .filter(ReceiptDetail.product_id.in_(product_on_promotion),
                                Receipt.created_date >= Promotion.start_date,
                                Receipt.created_date <= Promotion.end_date).scalar() or 0

    return total_revenue


def calculate_receipt_before_promotion(promotion_id):
    promotion = Promotion.query.filter(Promotion.id == promotion_id).first()


def load_all_brands():
    return Brand.query.all()


def load_product_brand(brand_id):
    return Product.query.order_by(Product.category_id).filter(Product.brand_id == brand_id).all()
