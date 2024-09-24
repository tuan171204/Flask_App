import string
import random
from datetime import datetime

from sqlalchemy.orm import aliased

from Flask_App import app, db
from Flask_App.models import Category, Product, User, Receipt, ReceiptDetail, User_Role, Comment, Payment, \
    Provider, Distribution, Receipt_Status, Privileged, Report_Type, Receipt_Report, Delivery_Reason, \
    Goods_Received_Note, Goods_Received_Note_Detail, Goods_Delivery_Note
import hashlib
from flask_login import current_user
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.sql import extract
import os


def load_categories():
    return Category.query.all()

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

def load_all_products():
    products = Product.query.filter(Product.active.__eq__(True))
    products = products.order_by(Product.category_id)
    return products

def count_product(cate_id=None, kw=None):
    if cate_id:
        return Product.query.filter(and_(Product.active.__eq__(True),Product.category_id.__eq__(cate_id))).count()

    if kw:
        return Product.query.filter(Product.name.contains(kw)).count()

    return Product.query.filter(Product.active.__eq__(True)).count()


def get_product_by_id(product_id):
    return Product.query.get(product_id)


def get_cate_by_id(cate_id):
    return Category.query.get(cate_id)


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                avatar = kwargs.get('avatar'))

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


def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }
    
def load_payment():
    payments = Payment.query.all()
    
    return payments

def add_receipt(cart, payment_id):
    if cart:
        receipt = Receipt(user=current_user, payment_id=payment_id)
        db.session.add(receipt)

        for c in cart.values():
            d = ReceiptDetail(receipt=receipt,
                              product_id=int(c['id']),
                              quantity=c['quantity'],
                              unit_price=c['price'],)
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

    return db.session.query(Category.id, Category.name, func.count(Product.id))\
          .join(Product, Category.id.__eq__(Product.category_id), isouter=True)\
          .group_by(Category.id, Category.name).all()
#
# with app.app_context():
#     print(category_stats())


def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Product.id, Product.name, func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price))\
        .join(ReceiptDetail, ReceiptDetail.product_id.__eq__(Product.id), isouter=True)\
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id))\
        .group_by(Product.id, Product.name)\
        .order_by(Product.id)
        #.order_by( func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price))

    if kw:
        p = p.filter(Product.name.contains(kw))
        print(p)

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()

def product_months_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
                            .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id))\
                            .filter(extract('year', Receipt.created_date) == year)\
                            .group_by(extract('month', Receipt.created_date))\
                            .order_by(extract('month', Receipt.created_date)).all()


def add_comment(content, product_id):
    c = Comment(content=content, product_id=product_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(product_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size

    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).slice(start, start + page_size).all()


def count_comment(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()


def load_provider():
    
    return Provider.query.all()


def get_provider_by_id(provider_id):
    provider = Provider.query.filter(Provider.id==provider_id).first()

    return provider


def load_distribution(product_id):
    if product_id:
        return  Distribution.query.filter(Distribution.product_id.__eq__(product_id)).all()


def load_receipt(receipt_id=None, status_id=None, asc='True'):


        receipts = db.session.query(
            Receipt.id,
            Receipt.status_id.label('status_id'),
            Receipt.created_date,
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

        return receipts.all()


def load_receipt_detail(receipt_id, product_id=None, product_name=None):

    receipt_details = db.session.query(
        ReceiptDetail.receipt_id,
        ReceiptDetail.product_id,
        ReceiptDetail.quantity,
        ReceiptDetail.unit_price,
        Product.name.label('product_name'),
    ).join(Product, Product.id == ReceiptDetail.product_id)


    receipt_details = receipt_details.filter(ReceiptDetail.receipt_id.__eq__(receipt_id))

    total_price = sum(detail.quantity * detail.unit_price for detail in receipt_details)

    if product_id:
        receipt_details = receipt_details.filter(ReceiptDetail.product_id.__eq__(product_id))

    if product_name:
        receipt_details = receipt_details.filter(Product.name.contains(product_name))

    return receipt_details.all(), total_price


def load_receipt_status():
    return Receipt_Status.query.all()


def get_user_receipt(user_id, receipt_id=None, status_id=None, asc=True):

    user_receipt = db.session.query(
        Receipt.id,
        Receipt.created_date,
        Receipt.status_id,
        Payment.name.label('payment_name'),
        Receipt_Status.status_name.label('status_name')
    ).join(Payment, Receipt.payment_id==Payment.id)\
     .join(Receipt_Status, Receipt.status_id==Receipt_Status.id)

    user_receipt = user_receipt.filter(Receipt.user_id==user_id)

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
    need_confirm_receipt =  Receipt.query.filter(Receipt.user_id.__eq__(user_id),
                                                 Receipt.status_id == 5).first()

    if need_confirm_receipt:
        return True

    return False

def complete_receipt(receipt_id):
    receipt = Receipt.query.filter(Receipt.id==(receipt_id)).first()
    receipt.status_id=2

    db.session.commit()


def get_user_permission(user_id):
    user_permission = db.session.query(
                User.id,
                User_Role.privileged.label('user_privileged'),
                Privileged,
                User_Role
                ).join(Privileged, Privileged.user_id==User.id)\
                 .join(User_Role, User_Role.id==Privileged.user_role)\
                 .filter(User.id==user_id).first()

    return user_permission


def get_user_role_permission(user_id):
    user_role_permission = db.session.query(User_Role.privileged.label('user_privileged'),
                                            User_Role)\
                                     .join(Privileged, Privileged.user_role==User_Role.id)\
                                     .filter(Privileged.user_id==user_id).first()

    return user_role_permission



def load_user(user_id=None, asc='False'):
    users = db.session.query(User)

    if user_id:
        users = users.filter(User.id==user_id)

    if asc == 'True':
        users = users.order_by((User.joined_date))

    else:
        users = users.order_by(desc(User.joined_date))

    return users.all()

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



def load_goods_received_note(received_note_code=None, confirmed=None, asc='False'):

    g_note = db.session.query(Goods_Received_Note,
                            Provider.name.label('provider_name'),
                            Provider.address.label('provider_address'),
                            User.name.label('user_name_confirm'))\
                            .outerjoin(Provider, Provider.id==Goods_Received_Note.provider_id)\
                            .outerjoin(User, User.id==Goods_Received_Note.user_confirm)

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

    return g_note.all()


def get_goods_received_note(received_note_code):
    return db.session.query(Goods_Received_Note,
                            Provider.name.label('provider_name'),
                            Provider.address.label('provider_address'),
                            User.name.label('user_name_confirm')) \
        .outerjoin(Provider, Provider.id == Goods_Received_Note.provider_id) \
        .outerjoin(User, User.id == Goods_Received_Note.user_confirm)\
        .filter(Goods_Received_Note.code==received_note_code).first()


def get_goods_received_note_detail(received_note_code):
    return db.session.query(Goods_Received_Note_Detail,
                                            Product.name.label('product_name'),
                                            Product.import_price.label('product_import_price'))\
        .join(Product, Goods_Received_Note_Detail.product_id==Product.id)\
        .filter(Goods_Received_Note_Detail.goods_received_note_code==received_note_code).all()


def update_received_note_detail(goods_received_code, product_id,quantity):
    g_detail = Goods_Received_Note_Detail.query\
        .filter(and_(Goods_Received_Note_Detail.goods_received_note_code==goods_received_code,\
                    Goods_Received_Note_Detail.product_id==product_id)).first()
    
    g_detail.received_quantity = quantity
    db.session.commit()


def update_g_note_delivery_man(delivery_man, goods_received_code):
    g_note = Goods_Received_Note.query.filter(Goods_Received_Note.code==goods_received_code).first()

    g_note.delivery_man = delivery_man

    db.session.commit()


def complete_received_note(goods_received_code):
    g_note = Goods_Received_Note.query.filter(Goods_Received_Note.code==goods_received_code).first()

    g_note.confirmed = True
    g_note.confirm_date = datetime.now()
    g_note.user_confirm = current_user.id

    db.session.commit()


def load_delivery_reason():
    reason = Delivery_Reason.query.all()

    return reason

def load_delivery_note(delivery_code=None, confirmed=None, asc='False', reason=None, delivery_man_id=None):
    user_created_alias = aliased(User)
    delivery_man_alias = aliased(User)

    delivery_notes = db.session.query(Goods_Delivery_Note,
                                      Delivery_Reason.name.label('delivery_reason'),
                                      User.name.label('user_created'),
                                      User.name.label('delivery_man'))\
                                .join(Delivery_Reason, Delivery_Reason.id==Goods_Delivery_Note.reason)\
                                .join(user_created_alias, user_created_alias.id==Goods_Delivery_Note.user_created)\
                                .join(delivery_man_alias, delivery_man_alias.id==Goods_Delivery_Note.delivery_man)

    filters = []

    if delivery_code:
        filters.append(Goods_Delivery_Note.code.contains(delivery_code))

    if confirmed is not None:
        filters.append(Goods_Delivery_Note.confirmed == (confirmed == 'True'))

    if reason:
        filters.append(Goods_Delivery_Note.reason == reason)

    if delivery_man_id:
        filters.append(Goods_Delivery_Note.delivery_man.contains(delivery_man_id))

    if filters:
        delivery_notes = delivery_notes.filter(*filters)

    # Sắp xếp theo asc
    if asc == 'False':
        delivery_notes = delivery_notes.order_by(Goods_Delivery_Note.created_date)
    else:
        delivery_notes = delivery_notes.order_by(desc(Goods_Delivery_Note.created_date))

    return delivery_notes.all()

