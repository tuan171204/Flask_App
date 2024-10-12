import math
import os
from itertools import product

from num2words import num2words
import random

from werkzeug.utils import secure_filename

from Flask_App import app, db, UPLOAD_FOLDER
from flask_admin import Admin
from Flask_App.models import Category, Product, User_Role, Goods_Received_Note, User, Receipt, ReceiptDetail, \
    Goods_Delivery_Note
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose, AdminIndexView
from flask import redirect, flash, url_for
import utils
from flask import request
from datetime import datetime


class ManageModelView(ModelView):
    def check_permission(self, permission_name):
        if not current_user.is_authenticated:
            return False

        user_permission = utils.get_user_permission(current_user.id)
        return getattr(user_permission.User_Role, permission_name, False)

    def is_accessible(self):
        return current_user.is_authenticated


class UserView(ManageModelView):
    status_colors = {
        1: 'btn-warning',
        2: 'btn-success',
        3: 'btn-info',
        4: 'btn-danger',
        5: 'btn-secondary',
        6: 'btn-primary'
    }

    @expose('/')
    def index(self):
        info = request.args.get('info')

        active = request.args.get('active')

        asc = request.args.get('asc')

        page = request.args.get('page', 1)

        users = utils.load_user(active=active,
                                page=int(page),
                                asc=asc,
                                info=info)

        counter = utils.count_user(active=active, info=info)

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        next_page = url_for('user_admin.index',
                            page=int(page) + 1,
                            active=request.args.get('active'),
                            asc=request.args.get('asc')) if int(page) < pages else None

        prev_page = url_for('user_admin.index',
                            page=int(page) - 1,
                            active=request.args.get('active'),
                            asc=request.args.get('asc')) if int(page) > 1 else None

        return self.render('admin/user.html',
                           page=int(page),
                           users=users,
                           pages=pages,
                           prev_page=prev_page,
                           next_page=next_page,
                           size=app.config['VIEW_SIZE'])

    @expose('user-detail/<int:user_id>')
    def user_detail(self, user_id):
        user = utils.get_user_detail_admin(user_id)

        user_receipts = utils.get_user_receipt(user_id)

        return self.render('admin/user.html',
                           user=user,
                           user_receipts=user_receipts,
                           user_detail=True,
                           status_colors=self.status_colors)

    def is_accessible(self):
        return self.check_permission('view_user')


class ProductView(ManageModelView):
    @expose("/")
    def index(self):

        providers = utils.load_provider()

        kw = request.args.get('kw')

        active = request.args.get('active')

        provider_id = request.args.get('provider_id')

        import_price_asc = request.args.get('import_price_asc')

        price_asc = request.args.get('price_asc')

        from_import_price, to_import_price = request.args.get('from_import_price'), \
            request.args.get('to_import_price')

        from_price, to_price = request.args.get('from_price'), \
            request.args.get('to_price')

        page = request.args.get('page', 1)

        category = utils.load_categories_client()

        brands = utils.load_brands()

        products, counter = utils.load_manage_product(kw=kw,
                                                      active=active,
                                                      provider_id=provider_id,
                                                      price_asc=price_asc,
                                                      import_price_asc=import_price_asc,
                                                      from_import_price=from_import_price,
                                                      to_import_price=to_import_price,
                                                      from_price=from_price,
                                                      to_price=to_price,
                                                      page=int(page))

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        next_page = url_for('product.index',
                            page=int(page) + 1,
                            kw=request.args.get('kw'),
                            active=request.args.get('active'),
                            provider_id=request.args.get('provider_id'),
                            price_asc=request.args.get('price_asc'),
                            import_price_asc=request.args.get('import_price_asc'),
                            from_import_price=request.args.get('from_import_price'),
                            to_import_price=request.args.get('to_import_price'),
                            from_price=request.args.get('from_price'),
                            to_price=request.args.get('to_price')
                            ) if int(page) < pages else None

        prev_page = url_for('product.index',
                            page=int(page) - 1,
                            kw=request.args.get('kw'),
                            active=request.args.get('active'),
                            provider_id=request.args.get('provider_id'),
                            price_asc=request.args.get('price_asc'),
                            import_price_asc=request.args.get('import_price_asc'),
                            from_import_price=request.args.get('from_import_price'),
                            to_import_price=request.args.get('to_import_price'),
                            from_price=request.args.get('from_price'),
                            to_price=request.args.get('to_price')
                            ) if int(page) > 1 else None

        return self.render('admin/product.html',
                           products=products,
                           providers=providers,
                           next_page=next_page,
                           prev_page=prev_page,
                           pages=pages,
                           size=app.config['VIEW_SIZE'],
                           page=int(page),
                           categories=category,
                           brands=brands
                           )

    @expose("create-product", methods=['POST'])
    def create_product(self):
        file = request.files['product_image']
        image_path = ''

        if file.filename == '':
            file.filename = 'iphone7.jpg'

        if file and utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # Resize ảnh trước khi lưu
            resized_image = utils.resize_image(file)
            resized_image.save(filepath)

            image_path = f'images/{filename}'

        product_name = request.form.get('product_name')
        category_id = request.form.get('category_id')
        provider_id = request.form.get('provider_id')
        brand_id = request.form.get('brand_id')
        description = request.form.get('description')
        price = request.form.get('price')
        import_price = request.form.get('import_price')

        result = utils.add_product(product_name=product_name,
                                   category_id=category_id,
                                   provider_id=provider_id,
                                   brand_id=brand_id,
                                   description=description,
                                   import_price=float(import_price),
                                   price=float(price),
                                   image=image_path)

        if result:
            flash("Tạo thêm sản phẩm thành công", "warning")
        return redirect('/admin/product/')

    @expose('deactive-product/<int:product_id>')
    def deactive_product(self, product_id):
        product = Product.query.filter(Product.id == product_id).first()
        product.active = False

        db.session.commit()
        flash("Đã tạm ẩn sản phẩm", "info")
        return redirect('/admin/product')

    @expose('active-product/<int:product_id>')
    def active_product(self, product_id):
        product = Product.query.filter(Product.id == product_id).first()
        product.active = True

        db.session.commit()
        flash("Đã đổi trạng thái sản phẩm", "info")
        return redirect('/admin/product')

    @expose('product-update/<int:product_id>')
    def product_update(self, product_id):
        product = utils.get_product_detail_info_admin(product_id)

        return self.render("admin/product.html",
                           product=product)

    @expose('product-promotion')
    def product_promotion(self):

        kw = request.args.get('kw')

        expired = request.args.get('expired')

        promotion = utils.get_promotion(kw=kw, expired=expired)

        current_time = datetime.now()

        if not promotion:
            flash("Không tìm thấy chương trình khuyến mãi nào !", "danger")
            return self.render("admin/product.html",
                               promotion=promotion,
                               current_time=current_time)

        return self.render("admin/product.html",
                           promotion=promotion,
                           current_time=current_time)

    @expose('promotion-detail/<int:promotion_id>')
    def promotion_detail(self, promotion_id):
        promotion = utils.get_promotion(kw=str(promotion_id))

        product_promotion = utils.get_product_with_promotion(promotion_id)

        promotion_detail = utils.get_promotion_detail(promotion_id)

        return self.render('admin/product.html',
                           promotion_detail=True,
                           promotion=promotion,
                           product_promotion=product_promotion)

    def is_accessible(self):
        return self.check_permission('view_product')


class CategoryView(ManageModelView):
    @expose("/")
    def index(self):
        kw = request.args.get('kw')

        page = request.args.get('page', 1)

        categories, counter = utils.load_categories(kw, page=int(page))

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        next_page = url_for('category.index',
                            page=int(page) + 1) if int(page) < pages else None

        prev_page = url_for('category.index',
                            page=int(page) - 1) if int(page) > 1 else None

        return self.render('admin/category.html',
                           categories=categories,
                           pages=pages,
                           next_page=next_page,
                           prev_page=prev_page
                           )

    @expose("category-detail/<int:category_id>")
    def category_detail(self, category_id):
        page = request.args.get('page', 1)

        products = utils.load_products_admin(cate_id=category_id, page=int(page))

        counter = utils.count_product(cate_id=category_id)

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        next_page = url_for('category.category_detail',
                            page=int(page) + 1,
                            category_id=category_id) if int(page) < pages else None

        prev_page = url_for('category.category_detail',
                            page=int(page) - 1,
                            category_id=category_id) if int(page) > 1 else None

        return self.render('admin/category.html',
                           page=int(page),
                           products=products,
                           counter=counter,
                           pages=pages,
                           next_page=next_page,
                           prev_page=prev_page,
                           step=app.config['VIEW_SIZE'],
                           category_id=category_id
                           )

    @expose('delete-category/<int:category_id>')
    def delete_category(self, category_id):
        category = Category.query.filter(Category.id == category_id).first()

        products = Product(Product.category_id == category_id).all()
        for product in products:
            product.category_id = 0

        db.session.commit()

        db.session.delete(category)
        db.session.commit()

        flash('Đã xóa bỏ danh mục sản phẩm', 'warning')

        return redirect('/admin/category/')

    @expose('change-category/<int:category_id>', methods=['POST'])
    def change_id(self, category_id):
        category = Category.query.filter(Category.id == category_id).first()
        category.id = request.form.get('category_id')
        db.session.commit()

        flash('Thay đổi mã danh mục thành công', 'warning')

        return redirect('/admin/category/')

    @expose('create-category', methods=['POST'])
    def create_category(self):
        category_id = request.form.get('category_id')
        category_name = request.form.get('category_name')
        utils.create_category(cate_id=category_id,
                              cate_name=category_name)

        flash("Tạo danh mục sản phẩm mới thành công ", "warning")

        return redirect('/admin/category/')

    def is_accessible(self):
        return self.check_permission('view_product')


class DeliveryNoteView(ManageModelView):
    @expose('/')
    def index(self):
        delivery_code = request.args.get('delivery_note_code')

        confirmed = request.args.get('confirmed')

        asc = request.args.get('asc', 'True')

        reason = request.args.get('delivery_reason')

        page = request.args.get('page', 1)

        delivery_man_id = request.args.get('delivery_man_id')

        delivery_reason = utils.load_delivery_reason()

        counter = utils.count_delivery_note(confirmed=confirmed,
                                            delivery_code=delivery_code,
                                            reason=reason,
                                            delivery_man_id=delivery_man_id)

        delivery_notes = utils.load_delivery_note(delivery_code=delivery_code,
                                                  confirmed=confirmed,
                                                  asc=asc,
                                                  reason=reason,
                                                  delivery_man_id=delivery_man_id,
                                                  page=int(page))

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        prev_page = url_for('goods_delivery.index',
                            page=int(page) - 1,
                            confirmed=request.args.get('confirmed'),
                            asc=request.args.get('asc'),
                            delivery_note=request.args.get('delivery_note_code'),
                            reason=request.args.get('delivery_reason'),
                            delivery_man_id=request.args.get('delivery_man_id')
                            ) if int(page) > 1 else None

        next_page = url_for('goods_delivery.index',
                            page=int(page) + 1,
                            confirmed=request.args.get('confirmed'),
                            asc=request.args.get('asc'),
                            delivery_note=request.args.get('delivery_note_code'),
                            reason=request.args.get('delivery_reason'),
                            delivery_man_id=request.args.get('delivery_man_id')
                            ) if int(page) < pages else None

        return self.render('admin/delivery_product.html',
                           delivery_notes=delivery_notes,
                           delivery_reason=delivery_reason,
                           prev_page=prev_page,
                           next_page=next_page,
                           pages=pages)

    @expose("view-delivery-note-by-id/<int:receipt_id>")
    def view_delivery_note_by_id(self, receipt_id):
        delivery_note = utils.get_delivery_note(receipt_id=receipt_id)
        delivery_code = delivery_note.code
        return self.view_delivery_note(delivery_code=delivery_code, receipt_id=receipt_id)

    @expose("/view-delivery-note/<delivery_code>")
    @expose("/view-delivery-note/<delivery_code>/<int:receipt_id>")
    def view_delivery_note(self, delivery_code, receipt_id=None):
        receipt = utils.get_receipt_by_id(receipt_id)

        delivery_note = utils.get_delivery_note(delivery_code)

        delivery_details, total_price, total_price2 = utils.load_delivery_note_details(delivery_code)

        total_in_words = num2words(total_price, lang='vi').capitalize() + " đồng "

        now = datetime.now()

        return self.render('admin/delivery_form.html',
                           receipt=receipt,
                           delivery_details=delivery_details,
                           total_price=total_price,
                           total_price2=total_price2,
                           total_in_words=total_in_words,
                           now=now,
                           delivery_code=delivery_code,
                           delivery_note=delivery_note)

    @expose("/update-delivery-note/<delivery_code>", methods=['POST'])
    @expose("/update-delivery-note/<delivery_code>/<int:receipt_id>", methods=['POST'])
    def update_delivery_note(self, receipt_id=None, delivery_code=None):
        reason = request.form.get('delivery_reason')

        if not reason:
            reason = 1

        delivery_man_id = 8

        delivery_address = request.form.get('delivery_address')

        receipt_details, total_price = utils.load_receipt_detail(receipt_id)

        products_data = []

        for detail in receipt_details:
            product_id = request.form.get(f'product_id_{detail.product_id}')
            delivered_quantity = request.form.get(f'quantity_{detail.product_id}')
            base_quantity = request.form.get(f'base_quantity_{detail.product_id}')

            if product_id and delivered_quantity and base_quantity:
                products_data.append({'product_id': product_id,
                                      'delivered_quantity': delivered_quantity,
                                      'base_quantity': base_quantity})

        utils.update_delivery_note(delivery_code=delivery_code,
                                   delivery_man_id=delivery_man_id,
                                   delivery_reason=reason,
                                   delivery_address=delivery_address,
                                   total_price=total_price,
                                   products_data=products_data,
                                   receipt_id=receipt_id)

        flash("Cập nhật phiếu xuất kho thành công ", "info")

        return redirect('/admin/goods_delivery')

    @expose('/confirm-delivery-note/<delivery_code>/<int:receipt_id>', methods=['POST'])
    def confirm_delivery_note(self, delivery_code, receipt_id):
        reason = request.form.get('delivery_reason')

        if not reason:
            reason = 1

        delivery_man_id = 8

        delivery_address = request.form.get('delivery_address')

        receipt_details, total_price = utils.load_receipt_detail(receipt_id)

        products_data = []

        for detail in receipt_details:
            product_id = request.form.get(f'product_id_{detail.product_id}')
            delivered_quantity = request.form.get(f'quantity_{detail.product_id}')
            base_quantity = request.form.get(f'base_quantity_{detail.product_id}')

            if product_id and delivered_quantity and base_quantity:
                products_data.append({'product_id': product_id,
                                      'delivered_quantity': delivered_quantity,
                                      'base_quantity': base_quantity})

        utils.confirm_delivery_note(delivery_code=delivery_code,
                                    delivery_man_id=delivery_man_id,
                                    delivery_reason=reason,
                                    delivery_address=delivery_address,
                                    total_price=total_price,
                                    products_data=products_data,
                                    receipt_id=receipt_id)

        utils.confirm_receipt(receipt_id)

        flash("Xác nhận phiếu xuất kho thành công ", "warning")

        return redirect('/admin/goods_delivery')

    def is_accessible(self):
        return self.check_permission('delivery_product')


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndex(AdminIndexView):
    def __init__(self):
        super(MyAdminIndex, self).__init__(name='Home', menu_icon_type='fa', menu_icon_value='fa-solid fa-home')

    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=utils.category_stats())


class StatsView(ManageModelView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year', datetime.now())

        return self.render('admin/stats.html',
                           month_stats=utils.product_months_stats(year=year),
                           stats=utils.product_stats(kw=kw,
                                                     from_date=from_date, to_date=to_date))

    def is_accessible(self):
        return self.check_permission('view_stats')


class OrderProductView(ManageModelView):
    @expose('/')
    def index(self):

        providers = utils.load_provider()

        provider_id = request.args.get('provider_id')

        distributions = utils.load_distribution(provider_id)

        products = utils.load_all_products()

        products = products.order_by(Product.id)

        return self.render('admin/product_order.html',
                           providers=providers,
                           distributions=distributions,
                           products=products)

    @expose('/create-order/', methods=['POST'])
    def create_order(self):

        code = utils.generate_receive()

        provider_id = request.form.get('provider_id')

        products_data = []
        counter = 0

        total = 0

        while (True):
            product_id = request.form.get(f'product_id_{counter}')
            quantity = request.form.get(f'quantity_{counter}')
            note = request.form.get(f'note_{counter}')

            product = utils.get_product_by_id(product_id)

            if product and quantity:
                products_data.append({'product': product, 'quantity': quantity, 'note': note})
                total += float(product.import_price) * int(quantity)
                counter += 1

            else:
                break

        created_date = request.form.get('order_date')

        if not created_date:
            created_date = datetime.now()

        utils.create_receive_note(code=code,
                                  order_date=created_date,
                                  provider_id=provider_id,
                                  total_price=total,
                                  products_data=products_data,
                                  )

        flash("Đặt hàng thành công", "warning")

        return self.render('admin/product_order.html')

    def is_accessible(self):
        return self.check_permission('order_product')


class ReceiveNoteView(ManageModelView):
    @expose('/')
    def index(self):

        received_note_code = request.args.get('received_note_code')

        confirmed = request.args.get('confirmed')

        asc = request.args.get('asc', 'True')

        page = request.args.get('page', 1)

        goods_received_note = utils.load_goods_received_note(received_note_code, confirmed, asc, page=int(page))

        counter = utils.count_receive_note(confirmed=confirmed, received_note_code=received_note_code)

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        prev_page = url_for('goods_receive.index',
                            page=int(page) - 1,
                            confirmed=request.args.get('confirmed'),
                            asc=request.args.get('asc')
                            ) if int(page) > 1 else None
        next_page = url_for('goods_receive.index',
                            page=int(page) + 1,
                            confirmed=request.args.get('confirmed'),
                            asc=request.args.get('asc')
                            ) if int(page) < pages else None

        return self.render('admin/receive_product.html',
                           goods_received_note=goods_received_note,
                           next_page=next_page,
                           prev_page=prev_page,
                           pages=pages
                           )

    def is_accessible(self):
        return self.check_permission('receive_product')

    @expose('/create-receive-form/<goods_received_code>')
    def create_receive_form(self, goods_received_code):

        goods_received_note = utils.get_goods_received_note(goods_received_code)

        goods_received_note_detail = utils.get_goods_received_note_detail(goods_received_code)

        total_in_words = num2words(goods_received_note[0].total_price, lang='vi').capitalize() + " đồng "

        now = datetime.now()

        return self.render('admin/receive_form.html',
                           g_note=goods_received_note,
                           total_price=goods_received_note.Goods_Received_Note.total_price,
                           g_detail=goods_received_note_detail,
                           total_in_words=total_in_words,
                           now=now)

    @expose('/update-receive-form/<goods_received_code>', methods=['POST'])
    def update_received_note(self, goods_received_code):

        g_details = utils.get_goods_received_note_detail(goods_received_code)

        for g_detail in g_details:
            product_id = request.form.get(f'product_id_{g_detail[0].product_id}')
            quantity = request.form.get(f'quantity_{g_detail[0].product_id}')

            if product_id and quantity:
                utils.update_received_note_detail(goods_received_code, product_id, quantity)

        delivery_man = request.form.get('delivery_man')

        if delivery_man:
            utils.update_g_note_delivery_man(delivery_man, goods_received_code)

        flash(f'Cập nhật phiếu nhập {goods_received_code} thành công', 'warning')

        return redirect(f'/admin/goods_receive')

    @expose('/confirm-receive-form/<goods_received_code>', methods=['POST'])
    def confirm_received_note(self, goods_received_code):
        utils.complete_received_note(goods_received_code)

        flash(f"Đã xác nhận phiếu nhập kho {goods_received_code}", "warning")

        return redirect('/admin/goods_receive/')


class ReceiptView(ManageModelView):
    status_colors = {
        1: 'btn-warning',
        2: 'btn-success',
        3: 'btn-info',
        4: 'btn-danger',
        5: 'btn-secondary',
        6: 'btn-primary'
    }

    @expose('/')
    def index(self):

        receipt_id = request.args.get('receipt_id')

        asc = request.args.get('asc', 'True')

        status_id = request.args.get('status_id')

        page = request.args.get('page', 1)

        receipt_status = utils.load_receipt_status()

        receipts = utils.load_receipt(receipt_id, status_id, asc, page=int(page))

        counter = utils.count_receipt(status_id)

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        prev_page = url_for('receipt.index',
                            page=int(page) - 1,
                            status_id=request.args.get('status_id'),
                            asc=request.args.get('asc')
                            ) if int(page) > 1 else None

        next_page = url_for('receipt.index',
                            page=int(page) + 1,
                            status_id=request.args.get('status_id'),
                            asc=request.args.get('asc')
                            ) if int(page) < pages else None

        receipts_report = utils.load_receipt_report()

        report_types = utils.load_report_types()

        return self.render('admin/receipt.html',
                           receipts=receipts,
                           next_page=next_page,
                           prev_page=prev_page,
                           pages=pages,
                           receipt_status=receipt_status,
                           status_colors=self.status_colors,
                           receipts_report=receipts_report,
                           report_types=report_types)

    @expose('/view-detail/<int:receipt_id>')
    @expose('/view-detail/<int:receipt_id>/<next_url>/<int:user_id>')
    def receipt_detail_view(self, receipt_id, next_url=None, user_id=None):

        receipt_details, total_price, base_total_price = utils.load_receipt_detail(receipt_id)

        receipt_status = utils.load_receipt_status()

        receipts = utils.load_receipt(receipt_id)

        if next_url and user_id:
            url = url_for('user_admin.user_detail',
                          user_id=user_id)
        else:
            url = None

        return self.render('admin/receipt.html',
                           receipt_id=receipt_id,
                           receipt_details=receipt_details,
                           receipt_status=receipt_status,
                           receipts=receipts,
                           total_price=total_price,
                           status_colors=self.status_colors,
                           next_url=url)

    @expose('/receipt-update/<int:receipt_id>')
    def receipt_detail_update(self, receipt_id):

        user_permission = utils.get_user_permission(current_user.id)

        if user_permission.User_Role.update_receipt:

            product_id = request.args.get('product_id')

            product_name = request.args.get('product_name')

            receipt_details, total_price, base_total_price = utils.load_receipt_detail(receipt_id,
                                                                                       product_id=product_id,
                                                                                       product_name=product_name)

            receipts = utils.load_receipt(receipt_id)

            receipt_status = utils.load_receipt_status()

            return self.render('admin/receipt_update.html',
                               receipt_id=receipt_id,
                               receipt_details=receipt_details,
                               receipt_status=receipt_status,
                               receipts=receipts,
                               total_price=total_price,
                               product_id=product_id,
                               status_colors=self.status_colors)

        else:
            return self.render('admin/receipt_update.html',
                               err_msg='Bạn phải được cấp quyền mới được sử dụng chức năng này')

    @expose('/view-delivery-note/<int:receipt_id>')
    def view_delivery_note(self, receipt_id):
        receipt = utils.get_receipt_by_id(receipt_id)

        receipt_details, total_price = utils.load_receipt_detail(receipt_id)

        total_in_words = num2words(total_price, lang='vi').capitalize() + " đồng "

        now = datetime.now()

        delivery_code = utils.generate_delivery()

        return self.render('admin/delivery_form.html',
                           receipt=receipt,
                           receipt_details=receipt_details,
                           total_price=total_price,
                           total_in_words=total_in_words,
                           now=now,
                           delivery_code=delivery_code,
                           delivery_note=None)

    @expose('create-delivery-note/<int:receipt_id>/<delivery_code>', methods=['POST'])
    def create_delivery_note(self, receipt_id=None, delivery_code=None):

        created_date = datetime.now()

        reason = request.form.get('delivery_reason')

        if not reason:
            reason = 1

        delivery_man_id = 8

        delivery_address = request.form.get('delivery_address')

        receipt_details, total_price = utils.load_receipt_detail(receipt_id)

        products_data = []

        for detail in receipt_details:
            product_id = request.form.get(f'product_id_{detail.product_id}')
            delivered_quantity = request.form.get(f'quantity_{detail.product_id}')
            base_quantity = request.form.get(f'base_quantity_{detail.product_id}')
            note = request.form.get(f'note_{detail.product_id}')

            if product_id and delivered_quantity and base_quantity:
                products_data.append({'product_id': product_id,
                                      'delivered_quantity': delivered_quantity,
                                      'base_quantity': base_quantity,
                                      'note': note})

        utils.create_delivery_note(delivery_code=delivery_code,
                                   created_date=created_date,
                                   delivery_man_id=delivery_man_id,
                                   delivery_reason=reason,
                                   delivery_address=delivery_address,
                                   total_price=total_price,
                                   products_data=products_data,
                                   receipt_id=receipt_id)

        flash("Tạo phiếu xuất kho thành công ", "success")

        return redirect('/admin/receipt')

    @expose('create-confirm-delivery-note/<int:receipt_id>/<delivery_code>', methods=['POST'])
    def create_confirm_delivery_note(self, receipt_id=None, delivery_code=None):
        created_date = datetime.now()

        reason = request.form.get('delivery_reason')

        if not reason:
            reason = 1

        delivery_man_id = 8

        delivery_address = request.form.get('delivery_address')

        receipt_details, total_price = utils.load_receipt_detail(receipt_id)

        products_data = []

        for detail in receipt_details:
            product_id = request.form.get(f'product_id_{detail.product_id}')
            delivered_quantity = request.form.get(f'quantity_{detail.product_id}')
            base_quantity = request.form.get(f'base_quantity_{detail.product_id}')
            note = request.form.get(f'note_{detail.product_id}')

            if product_id and delivered_quantity and base_quantity:
                products_data.append({'product_id': product_id,
                                      'delivered_quantity': delivered_quantity,
                                      'base_quantity': base_quantity,
                                      'note': note})

        utils.create_delivery_note(delivery_code=delivery_code,
                                   created_date=created_date,
                                   delivery_man_id=delivery_man_id,
                                   delivery_reason=reason,
                                   delivery_address=delivery_address,
                                   total_price=total_price,
                                   products_data=products_data,
                                   receipt_id=receipt_id,
                                   confirmed=True)

        utils.confirm_receipt(receipt_id)

        flash("Tạo và xác nhận phiếu xuất kho thành công ", "success")

        return redirect('/admin/receipt')

    @expose('/confirm-report/<int:receipt_id>')
    def receipt_report_confirm(self, receipt_id):
        utils.complete_receipt(receipt_id)

        flash("Đã đánh dấu hoàn thành đơn hàng", "success")

        return redirect('/admin/receipt')

    def is_accessible(self):
        return self.check_permission('view_receipt')


class UserRoleView(ManageModelView):
    @expose('/')
    def index(self):
        user_id = request.args.get('user_id')

        asc = request.args.get('asc', 'False')

        page = request.args.get('page', 1)

        active = request.args.get('active')

        users = utils.load_user(user_id, asc, active, int(page))

        counter = utils.count_user(user_id, active)

        users_role = utils.load_user_role()

        pages = math.ceil(counter / app.config['VIEW_SIZE'])

        next_page = url_for('user_privileged.index',
                            page=int(page) + 1,
                            active=request.args.get('active'),
                            asc=request.args.get('asc')) if int(page) < pages else None

        prev_page = url_for('user_privileged.index',
                            page=int(page) - 1,
                            active=request.args.get('active'),
                            asc=request.args.get('asc')) if int(page) > 1 else None

        return self.render('admin/privileged.html',
                           users=users,
                           users_role=users_role,
                           next_page=next_page,
                           prev_page=prev_page,
                           pages=pages)

    @expose('/update-privileged/<int:user_id>')
    def update_privileged(self, user_id):
        user_privileged = utils.get_user_by_id(user_id)

        user_role_permissions = utils.get_user_role_permission(user_id)

        user_role_permission = user_role_permissions.User_Role

        user_role_privileged = user_role_permissions.user_privileged

        return self.render('admin/privileged.html',
                           user_privileged=user_privileged,
                           user_role_permission=user_role_permission,
                           user_role_privileged=user_role_privileged)

    def is_accessible(self):
        if not current_user.is_authenticated:
            return False

        user_permission = utils.get_user_permission(current_user.id)
        return getattr(user_permission, 'user_privileged', False)


admin = Admin(app=app,
              name="ANNNPTT Website",
              template_mode="bootstrap4",
              index_view=MyAdminIndex(),
              category_icon_classes={
                  'fa': 'fa-solid fa-house'
              })

admin.add_view(UserView(User, db.session,
                        name='Người dùng',
                        endpoint='user_admin',
                        menu_icon_type='fa',
                        menu_icon_value='fa-solid fa-user'))

admin.add_view(ProductView(Product, db.session,
                           name='Sản phẩm',
                           endpoint='product',
                           menu_icon_type='fa',
                           menu_icon_value='fa-solid fa-laptop'))

admin.add_view(CategoryView(Category, db.session,
                            name='Danh mục sản phẩm',
                            endpoint='category',
                            menu_icon_type='fa',
                            menu_icon_value='fa-solid fa-list'))

admin.add_view(ReceiptView(Receipt, db.session,
                           name='Hóa đơn',
                           endpoint='receipt',
                           menu_icon_type='fa',
                           menu_icon_value='fa-solid fa-receipt'
                           ))

admin.add_view(DeliveryNoteView(Goods_Delivery_Note, db.session,
                                name='Xuất kho',
                                endpoint='goods_delivery',
                                menu_icon_type='fa',
                                menu_icon_value='fa-solid fa-clipboard-list'
                                ))

admin.add_view(ReceiveNoteView(Goods_Received_Note, db.session,
                               name='Nhập kho',
                               endpoint='goods_receive',
                               menu_icon_type='fa',
                               menu_icon_value='fa-solid fa-clipboard-check'
                               ))

admin.add_view(OrderProductView(Goods_Received_Note, db.session,
                                name='Đặt hàng hóa',
                                endpoint='order_product',
                                menu_icon_type='fa',
                                menu_icon_value='fa-solid fa-truck'))

admin.add_view(StatsView(Receipt, db.session,
                         name='Thống kê',
                         endpoint='product_stats',
                         menu_icon_type='fa',
                         menu_icon_value='fa-solid fa-chart-simple'
                         ))

admin.add_view(UserRoleView(User_Role, db.session,
                            name='Phân quyền',
                            endpoint='user_privileged',
                            menu_icon_type='fa',
                            menu_icon_value='fa-solid fa-people-roof'
                            ))

admin.add_view(LogoutView(name='Đăng xuất',
                          menu_icon_type='fa',
                          menu_icon_value='fa-solid fa-power-off'
                          ))
