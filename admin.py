import json
import math
import os
from num2words import num2words
import random
from werkzeug.utils import secure_filename
from Flask_App import app, db, UPLOAD_FOLDER
from Flask_App.chat_rooms import rooms
from flask_admin import Admin
from Flask_App.models import Category, Product, User_Role, Goods_Received_Note, User, Receipt, ReceiptDetail, \
    Goods_Delivery_Note, Warranty, TimeUnitEnum, DiscountType, Promotion, PromotionDetail, Provider
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user, login_user
from flask_admin import BaseView, expose, AdminIndexView
from flask import redirect, flash, url_for, session, jsonify
import utils
from flask import request
from datetime import datetime


def check_permission(permission_name):
    if not current_user.is_authenticated:
        return False

    user_permission = utils.get_user_permission(current_user.id)
    return getattr(user_permission.User_Role, permission_name, False)


class ManageModelView(ModelView):

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
    @expose('user-detail/<int:user_id>/<url>/<int:receipt_id>')
    def user_detail(self, user_id, url=None, receipt_id=None):
        user = utils.get_user_detail_admin(user_id)

        user_receipts = utils.get_user_receipt(user_id)

        if url == 'receipt':
            back_url = url_for('receipt.receipt_detail_view',
                               receipt_id=receipt_id)
        elif url == 'receipt_update':
            back_url = url_for('receipt.receipt_detail_update',
                               receipt_id=receipt_id)
        else:
            back_url = None

        return self.render('admin/user.html',
                           user=user,
                           user_receipts=user_receipts,
                           user_detail=True,
                           back_url=back_url,
                           status_colors=self.status_colors)

    @expose('update-info/<int:user_id>', methods=['POST'])
    def update_info(self, user_id):
        username = request.form.get('user_username')
        name = request.form.get('user_name')
        email = request.form.get('user_email')
        phone_number = request.form.get('user_phone')
        if phone_number == 'Không có':
            phone_number = None
        address = request.form.get('user_address')
        if address == 'Không có':
            address = None

        result = utils.change_user_info(user_id,
                                        name=name,
                                        username=username,
                                        email=email,
                                        phone_number=str(phone_number),
                                        address=address)

        if result["success"]:
            flash("Cập nhật thông tin thành công.", "success")
        else:
            flash(f"{result['message']}", "danger")

        return redirect(f'/admin/user_admin/user-detail/{user_id}')

    @expose('deactive-user/<int:user_id>')
    def deactive_user(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        user.active = False

        db.session.commit()
        flash("Đã tạm khóa tài khoản", "info")
        return redirect('/admin/user_admin')

    @expose('active-user/<int:user_id>')
    def active_user(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        user.active = True

        db.session.commit()
        flash("Đã thay đổi trạng thái tài khoản", "info")
        return redirect('/admin/user_admin')

    @expose('create-user', methods=['POST'])
    def create_user(self):
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('fullname')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        staff = request.form.get('staff', False)

        if staff:
            utils.add_staff(name=name,
                            username=username,
                            password=password,
                            email=email,
                            phone_number=phone_number,
                            address=address)
        else:
            utils.add_user(name=name,
                           username=username,
                           password=password,
                           email=email,
                           phone_number=phone_number,
                           address=address)

        flash("Thêm người dùng thành công", "success")

        return redirect('/admin/user_admin/')

    def is_accessible(self):
        return check_permission('view_user')


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
        flash("Đã thay đổi trạng thái sản phẩm", "info")
        return redirect('/admin/product')

    @expose('product-update/<int:product_id>')
    @expose('product-update/<int:product_id>/<url>/<int:provider_id>')
    def product_update(self, product_id, url=None, provider_id=None):
        product = utils.get_product_detail_info_admin(product_id)

        category = utils.load_categories_client()

        product_warranty = utils.load_product_warranty(product_id)

        try:
            if url == 'provider':
                back_url = url_for('provider.provider_detail',
                                   provider_id=provider_id)

            else:
                back_url = None

        except Exception as e:
            print("Lỗi: ", str(e))

        return self.render("admin/product.html",
                           product=product,
                           category=category,
                           product_warranty=product_warranty,
                           back_url=back_url)

    @expose('update-product/<int:product_id>', methods=['POST'])
    def update_product(self, product_id):
        up_product_id = request.form.get('product_id')
        product_name = request.form.get('product_name')
        # GET ID
        product_category_id = request.form.get('category_id')
        product_price = request.form.get('product_price').replace(',', '')
        product_import_price = request.form.get('import_price').replace(',', '')

        if int(up_product_id) != int(product_id):
            info = utils.duplicate_product_with_new_id(product_id=product_id,
                                                       up_product_id=up_product_id,
                                                       product_name=product_name,
                                                       category_id=product_category_id,
                                                       price=product_price,
                                                       import_price=product_import_price)

        else:
            info = utils.update_product(product_id=product_id,
                                        up_product_id=up_product_id,
                                        product_name=product_name,
                                        category_id=product_category_id,
                                        price=product_price,
                                        import_price=product_import_price)

        if info:
            flash(str(info), "success")

        return redirect("/admin/product/")

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

    @expose('promotion-detail/<promotion_id>')
    def promotion_detail(self, promotion_id):
        promotion = utils.get_promotion(kw=str(promotion_id))

        product_promotion, product_applied_yet = utils.get_product_with_promotion(promotion_id)

        promotion_discount_type = PromotionDetail.query.filter(PromotionDetail.promotion_id == promotion_id).first()

        revenue_during_promotion, customer_count_before_promotion = utils.calculate_promotion_revenue(promotion_id)

        revenue_before_promotion, customer_count_during_promotion = utils.calculate_revenue_before_promotion(
            promotion_id)

        if promotion_discount_type:
            discount_type = promotion_discount_type.discount_type
            discount_type_list = False
        else:
            discount_type = False
            discount_type_list = DiscountType

        return self.render('admin/product.html',
                           promotion_detail=True,
                           promotion=promotion,
                           product_promotion=product_promotion,
                           product_applied_yet=product_applied_yet,
                           discount_type=discount_type,
                           discount_type_list=discount_type_list,
                           promotion_id=promotion_id,
                           revenue_during_promotion=revenue_during_promotion,
                           revenue_before_promotion=revenue_before_promotion,
                           customer_count_during_promotion=customer_count_during_promotion,
                           customer_count_before_promotion=customer_count_before_promotion)

    @expose('create-promotion', methods=['POST'])
    def create_promotion(self):
        description = request.form.get('description')
        start_date = request.form.get('promotion_start_date')
        end_date = request.form.get('promotion_end_date')
        apply_all = request.form.get('apply_all', False)

        try:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

            new_promotion = Promotion(id=str(f'PROMO{random.randint(100, 999)}'),
                                      description=description,
                                      start_date=start_date_dt,
                                      end_date=end_date_dt)

            db.session.add(new_promotion)
            db.session.commit()

            if apply_all:
                discount_type = request.form.get('discount_type')
                discount_value = request.form.get('discount_value')

                utils.apply_promotion_for_all(new_promotion.id, discount_type, discount_value)

                flash("Thêm chương trình khuyến mãi và áp dụng thành công ", "success")

                return redirect(url_for('product.product_promotion'))

            flash("Thêm chương trình khuyến mãi thành công ", "success")

        except Exception as e:
            flash(f'Error: {str(e)}', "danger")

            return redirect(url_for('product.product_promotion'))

    @expose('promotion-detail-update', methods=['POST'])
    def promotion_detail_update(self):
        promotion_id = request.form.get('promotion_id')
        promotion_description = request.form.get('promotion_description')
        end_date = request.form.get('promotion_end_date', None)

        try:
            if end_date:
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

            else:
                end_date_dt = None

        except Exception as e:
            flash(str(e), "danger")

            return redirect(url_for('product.promotion_detail', promotion_id=promotion_id))

        result = utils.update_promotion(promotion_id=promotion_id,
                                        description=promotion_description,
                                        end_date=end_date_dt)

        if result['success']:
            flash(result['msg'], 'success')

        else:
            flash(result['msg'], 'danger')

        return redirect(url_for('product.promotion_detail', promotion_id=promotion_id))

    @expose('delete-promotion/<promotion_id>')
    def delete_promotion(self, promotion_id):

        result = utils.delete_promotion(promotion_id)

        if result['success']:
            flash(result['message'], 'success')

        else:
            flash(result['message'], 'danger')

        return redirect(url_for('product.product_promotion'))

    def is_accessible(self):
        return check_permission('view_product')


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
        return check_permission('view_product')


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

        receipt_details, total_price, base_price = utils.load_receipt_detail_admin(receipt_id)

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

        receipt_details, total_price, base_price = utils.load_receipt_detail_admin(receipt_id)

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
        return check_permission('delivery_product')


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
        total_revenue = utils.calculate_total_revenue()

        total_check = utils.count_total_check()

        complete_receipt = utils.count_complete_receipt()

        total_customer = utils.count_customer()

        rating_service = float(utils.calculate_rating_service())

        sale_month_stats = utils.product_months_stats(datetime.now().year)

        sale_month_stats_last_year = utils.product_months_stats(datetime.now().year - 1)

        customer_month_stats = utils.customer_months_stats(datetime.now().year)

        profit_month_stats = utils.product_profit_month_stats(datetime.now().year)

        return self.render('admin/index.html',
                           total_revenue=total_revenue,
                           total_check=total_check,
                           complete_receipt=complete_receipt,
                           total_customer=total_customer,
                           sale_month_stats=sale_month_stats,
                           sale_month_stats_ly=sale_month_stats_last_year,
                           customer_month_stats=customer_month_stats,
                           profit_month_stats=profit_month_stats,
                           rating_service=float(rating_service))

    @expose('/forgot-password')
    def forgot_password(self):
        return self.render('admin/restore.html')

    @expose('/forgot-email-valid', methods=['post'])
    def forgot_email_valid(self):
        username = request.form.get('restore_username')
        email = request.form.get('email')

        valid = utils.check_restore_email_validation(username=username,
                                                     email=email)

        code = utils.generate_id()
        if valid:
            session['restore_code'] = code
            session['restore_username'] = username

            subject = 'Khôi phục mật khẩu'
            body = f'''
                    Mã khôi phục mật khẩu của bạn là {code}, vui lòng không chia sẻ mã khôi phục với bất kỳ ai
                '''
            to_email = email
            utils.send_email(subject, body, to_email)

            return self.render('admin/restore.html', restore_code=True)

        return self.render('admin/restore.html', err_msg='username và email không đúng, vui lòng thử lại')

    @expose('/check-restore-code', methods=['post'])
    def check_restore_code(self):
        restore_code = request.form.get('restore_code')

        if restore_code:
            session_code = session.get('restore_code')
            session_username = session.get('restore_username')

            if int(restore_code) == int(session_code):
                user = utils.login_without_pass(username=session_username)
                login_user(user=user)
                flash("Đăng nhập thành công", "success")
                return redirect('/admin')

            else:
                return self.render('admin/restore.html',
                                   err_msg='Mã khôi phục không đúng. vui lòng thử lại',
                                   restore_code=True)


class StatsView(ManageModelView):
    @expose('/')
    def index(self):
        revenue_statistics = utils.calculate_revenue_statistics()

        years = revenue_statistics['revenue_yearly']['year'].tolist()
        months = revenue_statistics['revenue_monthly']['month'].tolist()
        quarters = revenue_statistics['revenue_quarterly']['quarter'].tolist()

        # image_path = utils.visualize_revenue_statistics(revenue_statistics)

        return self.render('admin/stats.html',
                           revenue_stats=revenue_statistics,
                           years=years,
                           months=months,
                           quarters=quarters)

    def is_accessible(self):
        return check_permission('view_stats')


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
        return check_permission('order_product')


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
        return check_permission('receive_product')

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

        parsed_details = []
        for r in receipt_details:
            parsed_detail = {
                "receipt_id": r[0],
                "product_id": r[1],
                "quantity": r[2],
                "unit_price": r[3],
                "discount": r[4],
                "discount_info": r[5],
                "on_warranty": r[6],
                "warranty_details": json.loads(r[7]),
                "product_name": r[8],
                "product_image": r[9],
            }
            parsed_details.append(parsed_detail)

        receipt_status = utils.load_receipt_status()

        receipts = utils.load_receipt(receipt_id)

        if next_url and user_id:
            url = url_for('user_admin.user_detail',
                          user_id=user_id)
        else:
            url = None

        return self.render('admin/receipt.html',
                           receipt_id=receipt_id,
                           receipt_details=parsed_details,
                           receipt_status=receipt_status,
                           receipts=receipts,
                           total_price=total_price,
                           status_colors=self.status_colors,
                           next_url=url)

    @expose('/receipt-update/<int:receipt_id>')
    @expose('/view-detail/<int:receipt_id>/<next_url>/<int:user_id>')
    def receipt_detail_update(self, receipt_id, next_url=None, user_id=None):

        user_permission = utils.get_user_permission(current_user.id)

        if user_permission.User_Role.update_receipt:

            product_id = request.args.get('product_id')

            product_name = request.args.get('product_name')

            receipt_details, total_price, base_total_price = utils.load_receipt_detail_admin(receipt_id,
                                                                                             product_id=product_id,
                                                                                             product_name=product_name)

            receipts = utils.load_receipt(receipt_id)

            receipt_status = utils.load_receipt_status()

            if next_url and user_id:
                url = url_for('user_admin.user_detail',
                              user_id=user_id)
            else:
                url = None

            return self.render('admin/receipt_update.html',
                               receipt_id=receipt_id,
                               receipt_details=receipt_details,
                               receipt_status=receipt_status,
                               receipts=receipts,
                               total_price=total_price,
                               product_id=product_id,
                               status_colors=self.status_colors,
                               next_url=url)

        else:
            return self.render('admin/receipt_update.html',
                               err_msg='Bạn phải được cấp quyền mới được sử dụng chức năng này')

    @expose('/view-delivery-note/<int:receipt_id>')
    def view_delivery_note(self, receipt_id):
        receipt = utils.get_receipt_by_id(receipt_id)

        receipt_details, total_price, base_price = utils.load_receipt_detail_admin(receipt_id)

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

        receipt_details, total_price, base_price = utils.load_receipt_detail_admin(receipt_id)

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

        receipt_details, total_price, base_price = utils.load_receipt_detail_admin(receipt_id)

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
        return check_permission('view_receipt')


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


class WarrantyView(ManageModelView):
    @expose('/')
    def index(self):
        info = request.args.get('info')

        warrantys = utils.load_warranty(info=info)

        return self.render('admin/warranty.html',
                           warrantys=warrantys)

    @expose('/warranty-update/<int:warranty_id>')
    def warranty_update(self, warranty_id):
        warranty_detail = utils.get_warranty_detail(warranty_id)

        products = utils.load_product_applied_warranty_yet(warranty_id)

        time_unit = TimeUnitEnum

        if len(warranty_detail) < 1:
            warranty_detail = utils.get_void_warranty_detail(warranty_id)
            return self.render('admin/warranty.html',
                               warranty_detail=warranty_detail,
                               products=products,
                               time_unit=time_unit,
                               void=True)

        return self.render('admin/warranty.html',
                           warranty_detail=warranty_detail,
                           products=products,
                           time_unit=time_unit)

    @expose('/create-warranty', methods=['POST'])
    def create_warranty(self):
        description = request.form.get('description')
        apply_all = request.form.get('apply_all')
        warranty_period = request.form.get('warranty_period')
        time_unit = request.form.get('time_unit')

        new_warranty = Warranty(description=description)

        db.session.add(new_warranty)
        db.session.commit()

        if apply_all:
            apply_warranty = utils.apply_warranty_for_all(new_warranty.id, warranty_period, time_unit)

            if not apply_warranty['success']:
                print(apply_warranty['msg'])

        flash('Chương trình bảo hành đã được thêm thành công!', 'success')
        return redirect(url_for('warranty.index'))

    def is_accessible(self):
        return check_permission('view_product')


class StorageView(BaseView):
    @expose("/")
    def index(self):
        total_amount = utils.get_total_receive_and_delivery()

        return self.render('admin/storage.html',
                           total_amount=total_amount)

    def is_accessible(self):
        return current_user.is_authenticated


class ProviderView(ManageModelView):
    @expose("/")
    def index(self):
        kw = request.args.get("kw")

        phone_number = request.args.get("phone_number")

        email = request.args.get("email")

        providers = utils.load_provider(kw=kw,
                                        phone_number=phone_number,
                                        email=email)

        return self.render('admin/provider.html',
                           providers=providers)

    @expose("/provider-detail/<int:provider_id>")
    def provider_detail(self, provider_id):
        provider_detail, products_provider = utils.get_provider_detail(provider_id)

        return self.render('admin/provider.html',
                           provider_detail=provider_detail,
                           products_provider=products_provider)

    @expose("/create-provider", methods=['POST'])
    def create_provider(self):
        try:
            provider_name = request.form.get("provider_name")
            address = request.form.get("address")
            phone_number = request.form.get("phone_number")
            email = request.form.get("email")

            result = utils.add_provider(provider_name=provider_name,
                                        address=address,
                                        phone_number=phone_number,
                                        email=email)

            if result['success']:
                flash(result['message'], "success")

            else:
                flash(result['message'], 'danger')

            return redirect(url_for('provider.index'))

        except Exception as e:
            print(f'Lỗi server: {e}')

            flash("Thêm nhà cung cấp không thành công", "danger")

            return redirect(url_for('provider.index'))

    @expose("/update-provider", methods=['POST'])
    def update_provider(self):
        provider_id = request.form.get('provider-id')

        try:
            provider_name = request.form.get('provider-name')
            address = request.form.get('address')
            phone_number = request.form.get('phone-number')
            email = request.form.get('address')

            if phone_number == 'Chưa có':
                phone_number = None

            if email == 'Chưa có':
                email = None

            changes = utils.update_provider(provider_id=provider_id,
                                            provider_name=provider_name,
                                            address=address,
                                            phone_number=phone_number,
                                            email=email)
            if changes:
                flash("Cập nhật thông tin nhà cung cấp thành công", "success")

            else:
                flash("Lỗi utils", "danger")

            return redirect(url_for('provider.provider_detail', provider_id=provider_id))

        except Exception as e:
            print(str(e))
            flash(f"Lỗi: {str(e)}", "danger")
            return redirect(url_for('provider.provider_detail', provider_id=provider_id))

    def is_accessible(self):
        return check_permission('order_product')


class SupportView(BaseView):
    @expose("/")
    def index(self):
        rooms_list = [{"room_code": room, "members": data["members"]} for room, data in rooms.items()]

        return self.render("admin/support.html", rooms=rooms_list)

    @expose('/support-user/<room_code>', methods=['GET'])
    def support_user(self, room_code):
        room = room_code
        name = "Nhân viên"

        session["room"] = room  # store room_code in user session
        session["name"] = name  # store user_name in user session

        room = session.get("room")
        name = session.get("name")

        if room is None or name is None:
            return redirect("/admin/support")

        return self.render("admin/support.html",
                           code=room,
                           name=name,
                           messages=rooms[room]["messages"],
                           join=True)

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app=app,
              name="ANNNPTT WEB",
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

admin.add_view(SupportView(name="Hỗ trợ trực tuyến",
                           endpoint="support",
                           menu_icon_type='fa',
                           menu_icon_value='fa-solid fa-headset'
                           ))

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

admin.add_view(WarrantyView(Warranty, db.session,
                            name='Bảo hành',
                            endpoint='warranty',
                            menu_icon_type='fa',
                            menu_icon_value='fa-solid fa-wrench'
                            ))

admin.add_view(ReceiptView(Receipt, db.session,
                           name='Hóa đơn',
                           endpoint='receipt',
                           menu_icon_type='fa',
                           menu_icon_value='fa-solid fa-receipt'
                           ))

admin.add_view(OrderProductView(Goods_Received_Note, db.session,
                                name='Đặt hàng hóa',
                                endpoint='order_product',
                                menu_icon_type='fa',
                                menu_icon_value='fa-solid fa-truck'))

admin.add_view(ProviderView(Provider, db.session,
                            name="Nhà cung cấp",
                            endpoint='provider',
                            menu_icon_type='fa',
                            menu_icon_value='fa-solid fa-basket-shopping'))

admin.add_view(ReceiveNoteView(Goods_Received_Note, db.session,
                               name='Nhập kho',
                               endpoint='goods_receive',
                               menu_icon_type='fa',
                               menu_icon_value='fa-solid fa-clipboard-check'
                               ))

admin.add_view(DeliveryNoteView(Goods_Delivery_Note, db.session,
                                name='Xuất kho',
                                endpoint='goods_delivery',
                                menu_icon_type='fa',
                                menu_icon_value='fa-solid fa-clipboard-list'
                                ))

admin.add_view(StorageView(name='Kiểm kho',
                           endpoint='storage',
                           menu_icon_type='fa',
                           menu_icon_value='fa-solid fa-shop-lock'
                           ))

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
