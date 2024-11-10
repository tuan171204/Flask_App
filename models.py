from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, MetaData, Table, update, Enum
from Flask_App import db, app
from datetime import datetime
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from flask_login import UserMixin
from flask_migrate import migrate


class Category(db.Model):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('category.id'), nullable=True)
    child = Column(Boolean, nullable=True, default=0)
    children = relationship('Category', backref='parent', remote_side=[id], lazy=True)
    products = relationship('Product', backref='category', lazy=False)

    def __str__(self):
        return self.name


class Product(db.Model):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, index=True)
    description = Column(String(255))
    price = Column(Float, default=0)
    image = Column(String(100))
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())
    rating = Column(Float, default=0, nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('brand.id'), nullable=False)
    import_price = Column(Float, nullable=False)
    warranty = Column(Integer, ForeignKey('warranty.id'), nullable=True)

    promotion= relationship('PromotionDetail', backref='product', lazy=True)
    receipt_details = relationship('ReceiptDetail', backref='product', lazy=True)
    goods_received_note_detail = relationship('Goods_Received_Note_Detail', backref='product', lazy=True)
    comments = relationship('Comment', backref='product', lazy=True)
    distribution = relationship('Distribution', backref='product', lazy=True)
    goods_delivery_note_detail = relationship('Goods_Delivery_Note_Detail', backref='product', lazy=True)
    warranty_detail = relationship('WarrantyDetail', backref='product', lazy=True)

    def __str__(self):
        return self.name


class Brand(db.Model):
    __tablename__ = 'brand'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    products = relationship('Product', backref='brand', lazy=False)


class User_Role(db.Model):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)

    view_user = Column(Boolean, default=False)
    view_customer = Column(Boolean, default=False)
    view_receipt = Column(Boolean, default=False)
    view_stats = Column(Boolean, default=False)
    update_receipt = Column(Boolean, default=False)
    view_product = Column(Boolean, default=False)
    update_product = Column(Boolean, default=False)
    order_product = Column(Boolean, default=False)
    receive_product = Column(Boolean, default=False)
    delivery_product = Column(Boolean, default=False)
    privileged = Column(Boolean, default=False)
    login_admin = Column(Boolean, default=False)
    super_user = Column(Boolean, default=False)

    user_privileged_relation = relationship('Privileged', backref='permission', lazy=True)


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50), unique=True)
    phone_number = Column(String(11), nullable=True)
    address = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    privileged = relationship('Privileged', backref='user', lazy=True)
    goods_recevie = relationship('Goods_Received_Note', backref='user', lazy=True)
    goods_delivery = relationship('Goods_Delivery_Note', backref='user', lazy=True,
                                  foreign_keys='Goods_Delivery_Note.user_created')
    goods_delivery_man = relationship('Goods_Delivery_Note', backref='user_delivery', lazy=True,
                                      foreign_keys='Goods_Delivery_Note.delivery_man')
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)
    report = relationship('Receipt_Report', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Privileged(db.Model):
    __tablename__ = 'privileged'

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    user_role = Column(Integer, ForeignKey(User_Role.id), primary_key=True)


# Hoa don
class Receipt(db.Model):
    __tablename__ = 'receipt'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now(), index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=False, index=True)
    status_id = Column(Integer, ForeignKey('receipt_status.id'), default=6)
    details = relationship('ReceiptDetail', backref='receipt', lazy=True)
    report = relationship('Receipt_Report', backref='receipt', lazy=True)
    exported = Column(Boolean, default=False)
    delivery_address = Column(String(255), nullable=False)
    receiver_name = Column(String(255), nullable=False)
    promotion_id = Column(Integer, ForeignKey('promotion.id'), nullable=True)
    delivery_note = relationship('Goods_Delivery_Note', backref='receipt', lazy=True)


class ReceiptDetail(db.Model):
    __tablename__ = 'receipt_detail'

    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False, primary_key=True, index=True)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)
    discount = Column(Float, default=0, nullable=True)
    discount_info = Column(String(255), nullable=True)
    on_warranty = Column(Boolean, default=False)


class Comment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.now(), index=True)

    def __str__(self):
        return self.content


class Provider(db.Model):
    __tablename__ = 'provider'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    goods_received_note = relationship('Goods_Received_Note', backref='provider', lazy=True)
    distribution = relationship('Distribution', backref='provider', lazy=True)
    # storage_provider = relationship('Storage', backref='provider', lazy=True)


class Distribution(db.Model):
    __tablename__ = 'distribution'

    product_id = Column(Integer, ForeignKey(Product.id), primary_key=True, nullable=False)
    provider_id = Column(Integer, ForeignKey(Provider.id), primary_key=True, nullable=False)
    # Maybe put import & selling price here


class Goods_Received_Note(db.Model):
    __tablename__ = 'goods_received_note'

    code = Column(String(255), primary_key=True)
    order_date = Column(DateTime, nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey(Provider.id), nullable=False, index=True)
    details = relationship("Goods_Received_Note_Detail", backref='goods_Received_Note', lazy=True)
    confirmed = Column(Boolean, default=False, index=True)
    confirm_date = Column(DateTime, default=None, nullable=True, index=True)
    user_confirm = Column(Integer, ForeignKey(User.id), nullable=True)
    delivery_man = Column(String(255), default=None, nullable=True)
    total_price = Column(Float, nullable=False)


class Goods_Received_Note_Detail(db.Model):
    __tablename__ = 'goods_received_note_detail'

    goods_received_note_code = Column(String(255), ForeignKey(Goods_Received_Note.code), primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey(Product.id), primary_key=True, index=True)
    quantity = Column(Integer, default=0)
    received_quantity = Column(Integer, default=0, nullable=True)
    note = Column(String(255), nullable=True)


class Delivery_Reason(db.Model):
    __tablename__ = 'delivery_reason'

    id = Column(Integer, primary_key=True)
    name = Column(String(55), nullable=False)
    deliver_note = relationship('Goods_Delivery_Note', backref='delivery_reason', lazy=True)


class Goods_Delivery_Note(db.Model):
    __tablename__ = 'goods_delivery_note'

    code = Column(String(255), primary_key=True)
    created_date = Column(DateTime, default=datetime.now(), nullable=False, index=True)
    reason = Column(Integer, ForeignKey(Delivery_Reason.id), nullable=False, index=True)
    user_created = Column(Integer, ForeignKey(User.id), nullable=False)
    delivery_address = Column(String(255), nullable=False)
    total_price = Column(Float, nullable=False)
    confirmed = Column(Boolean, nullable=False)
    confirm_date = Column(DateTime, nullable=True)
    details = relationship('Goods_Delivery_Note_Detail', backref='g_deli_details', lazy=True)
    delivery_man = Column(Integer, ForeignKey(User.id), nullable=False, index=True)
    for_receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=True, index=True)


class Goods_Delivery_Note_Detail(db.Model):
    __tablename__ = 'goods_delivery_note_detail'

    goods_delivery_note_code = Column(String(255), ForeignKey(Goods_Delivery_Note.code), primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey(Product.id), primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    delivered_quantity = Column(Integer, nullable=True, default=0)
    note = Column(String(255), nullable=True)


class Payment(db.Model):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    logo = Column(String(55), nullable=True)
    receipt_payment = relationship("Receipt", backref="payment", lazy=True)


class Receipt_Status(db.Model):
    __tablename__ = 'receipt_status'

    id = Column(Integer, primary_key=True)
    status_name = Column(String(50))
    status = relationship('Receipt', backref='receipt_status')


class Report_Type(db.Model):
    __tablename__ = 'report_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = relationship('Receipt_Report', backref='type', lazy=True)


class Receipt_Report(db.Model):
    __tablename__ = 'receipt_report'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_report = Column(Integer, ForeignKey(User.id), nullable=False, index=True)
    receipt_report = Column(Integer, ForeignKey(Receipt.id), nullable=False, index=True)
    report_type = Column(Integer, ForeignKey(Report_Type.id), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    created_date = Column(DateTime, default=datetime.now())


class TimeUnitEnum(PyEnum):
    YEAR = "năm"
    MONTH = "tháng"
    WEEK = "tuần"


class Warranty(db.Model):
    __tablename__ = 'warranty'

    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=True, autoincrement=True)
    product = relationship('Product', backref='warranty_product', lazy=True)
    warranty_detail = relationship('WarrantyDetail', backref='warranty_product', lazy=True)


class WarrantyDetail(db.Model):
    __tablename__ = 'warranty_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    warranty_id = Column(Integer, ForeignKey(Warranty.id), nullable=False)
    warranty_period = Column(Integer, nullable=False)
    time_unit = Column(Enum(TimeUnitEnum), default=TimeUnitEnum.MONTH, nullable=False)


class DiscountType(PyEnum):
    PERCENTAGE = 1
    GET_FREE = 2
    FIXED_AMOUNT = 3
    PRICE = 4


class ApplyObject(PyEnum):
    Product = 1
    Receipt = 2


class Promotion(db.Model):
    __tablename__ = 'promotion'

    id = Column(String(255), primary_key=True)
    description = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=False, default=datetime.now())
    end_date = Column(DateTime, nullable=True)
    apply_for = Column(Enum(ApplyObject), default=ApplyObject.Product, nullable=False)

    receipts = relationship('Receipt', backref='promotion', lazy=True)
    detail = relationship('PromotionDetail', backref='promotion', lazy=True)


class PromotionDetail(db.Model):
    __tablename__ = 'promotion_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    promotion_id = Column(String(255), ForeignKey(Promotion.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    discount_type = Column(Enum(DiscountType), nullable=False)
    discount_value = Column(Float, nullable=True)


class District(db.Model):
    __tablename__ = 'district'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    ward = relationship('Ward', backref='district', lazy=True)


class Ward(db.Model):
    __tablename__ = 'ward'

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey(District.id), nullable=False)
    name = Column(String(255))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
