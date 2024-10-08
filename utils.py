import math
import string
import random
from datetime import datetime
from PIL import Image
from flask import flash
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import aliased
from Flask_App import app, db, ALLOWED_EXTENSIONS
from Flask_App.models import Category, Product, User, Receipt, ReceiptDetail, User_Role, Comment, Payment, \
    Provider, Distribution, Receipt_Status, Privileged, Report_Type, Receipt_Report, Delivery_Reason, \
    Goods_Received_Note, Goods_Received_Note_Detail, Goods_Delivery_Note, Goods_Delivery_Note_Detail, Promotion, \
    Warranty, Brand, PromotionDetail, District, Ward
import hashlib
from flask_login import current_user
from sqlalchemy import func, and_, or_, desc, Integer
from sqlalchemy.sql import extract
import os


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_categories_client():
    return Category.query.all()


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


def count_user(user_id=None, active=None):
    if user_id:
        return 1

    if active:
        if active == 'True':
            return User.query.filter(User.active == True).count()
        else:
            return User.query.filter(User.active == False).count()

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
        .join(PromotionDetail, PromotionDetail.product_id == Product.id) \
        .join(Promotion, Promotion.id == PromotionDetail.promotion_id) \
        .filter(Product.id == product_id).first()

    return product


def get_cate_by_id(cate_id):
    return Category.query.get(cate_id)


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
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


def get_user_by_id(user_id):
    return User.query.get(user_id)


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

    if cart:
        for c in cart.values():
            id = int(c['id'])
            product = get_product_detail_info(id)

            if product.discount_type.value == 2 and c['quantity'] > 1 and c['quantity'] % 2 == 0:
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
            else:
                d = ReceiptDetail(receipt=receipt,
                                  product_id=int(c['id']),
                                  quantity=c['quantity'],
                                  unit_price=c['price'], )
            db.session.add(d)

        db.session.commit()


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
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id)) \
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
    receipt_details = db.session.query(
        ReceiptDetail.receipt_id,
        ReceiptDetail.product_id,
        ReceiptDetail.quantity,
        ReceiptDetail.unit_price,
        ReceiptDetail.discount,
        ReceiptDetail.discount_info,
        Product.name.label('product_name'),
        Product.image.label('product_image')
    ).join(Product, Product.id == ReceiptDetail.product_id)

    receipt_details = receipt_details.filter(ReceiptDetail.receipt_id.__eq__(receipt_id))

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


def load_user(user_id=None, asc='False', active=None, page=1):
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
    return generate_code("DP04")


def generate_receive():
    return generate_code("RP04")


def create_receive_note(code, products_data, **kwargs, ):
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