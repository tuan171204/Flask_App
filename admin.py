from num2words import num2words
import random
from Flask_App import app,db
from flask_admin import Admin
from Flask_App.models import Category, Product, User_Role, Goods_Received_Note, User, Receipt, ReceiptDetail, \
    Goods_Delivery_Note
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose, AdminIndexView
from flask import redirect, flash
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
    create_modal = True
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ['id', 'name', 'username', 'password', "joined_date", "active"]
    form_columns = ['id','name', 'username', 'password', "joined_date", "active"]
    can_view_details = True
    can_export = True
    column_searchable_list = ['name', 'id']
    column_filters = ['name', 'id']
    column_exclude_list = ['active']
    column_sortable_list = ['id', 'name']

    def is_accessible(self):
        return self.check_permission('view_user')


class CustomerView(ManageModelView):
    create_modal = True
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ['name', 'username', 'password', "joined_date", "active"]
    form_columns = ['name', 'username', 'password', "joined_date", "active"]
    can_view_details = True
    can_export = True
    column_searchable_list = ['name', 'id']
    column_filters = ['name', 'id']
    column_exclude_list = ['active']
    column_sortable_list = ['id', 'name']

    def is_accessible(self):
        return self.check_permission('view_customer')


class ProductView(ManageModelView):
    create_modal = True
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ['id', 'name', 'price', 'image', 'active', 'description', 'category_id', 'brand_id']
    form_columns = ['id','name', 'price', 'image', 'active', 'description', 'category_id', 'brand_id']
    can_view_details = True
    can_export = True
    column_searchable_list = ['name', 'category_id']
    column_filters = ['name', 'price', 'category_id']
    column_exclude_list = ['image', 'active']
    column_sortable_list = ['id', 'name', 'price']

    def is_accessible(self):
        return self.check_permission('view_product')


class CategoryView(ManageModelView):
    create_modal = True
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ['id', 'name']
    form_columns = ['id','name']
    can_view_details = True
    can_export = True
    column_searchable_list = ['name']
    column_filters = ['name']
    column_sortable_list = ['id']

    def is_accessible(self):
        return self.check_permission('view_product')



class DeliveryNoteView(ManageModelView):
   @expose('/')
   def index(self):
       delivery_code = request.args.get('delivery_note_code')

       confirmed = request.args.get('confirmed')

       asc = request.args.get('asc', 'True')

       reason = request.args.get('delivery_reason')

       delivery_man_id = request.args.get('delivery_man_id')

       delivery_reason = utils.load_delivery_reason()

       delivery_notes = utils.load_delivery_note(delivery_code=delivery_code,
                                                 confirmed=confirmed,
                                                 asc=asc,
                                                 reason=reason,
                                                 delivery_man_id=delivery_man_id)

       return self.render('admin/delivery_product.html',
                          delivery_notes=delivery_notes,
                          delivery_reason=delivery_reason)


   @expose("view-delivery-note-by-id/<int:receipt_id>")
   def view_delivery_note_by_id(self, receipt_id):
       delivery_note = utils.get_delivery_note(receipt_id=receipt_id)
       delivery_code = delivery_note.code
       return self.view_delivery_note(delivery_code=delivery_code, receipt_id=receipt_id)

   @expose("/view-delivery-note/<delivery_code>")
   @expose("/view-delivery-note/<delivery_code>/<int:receipt_id>")
   def view_delivery_note(self, delivery_code, receipt_id = None):
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
                           month_stats = utils.product_months_stats(year=year),
                           stats = utils.product_stats(kw=kw,
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

        while(True):
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
                                  products_data = products_data,
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

        goods_received_note = utils.load_goods_received_note(received_note_code, confirmed, asc)

        return self.render('admin/receive_product.html',
                           goods_received_note=goods_received_note)


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
                           g_detail=goods_received_note_detail,
                           total_in_words = total_in_words,
                           now = now)

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

        flash('Cập nhật phiếu nhập thành công', 'warning')

        return redirect(f'/admin/goods_receive/create-receive-form/{goods_received_code}')


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

        receipt_status = utils.load_receipt_status()

        receipts = utils.load_receipt(receipt_id, status_id, asc)

        receipts_report = utils.load_receipt_report()

        report_types = utils.load_report_types()

        return self.render('admin/receipt.html',
                            receipts = receipts,
                           receipt_status=receipt_status,
                           status_colors=self.status_colors,
                           receipts_report=receipts_report,
                           report_types=report_types)

    @expose('/view-detail/<int:receipt_id>')
    def receipt_detail_view(self, receipt_id):

        receipt_details, total_price = utils.load_receipt_detail(receipt_id)

        receipt_status = utils.load_receipt_status()

        receipts = utils.load_receipt(receipt_id)



        return self.render('admin/receipt.html',
                           receipt_id=receipt_id,
                           receipt_details=receipt_details,
                           receipt_status=receipt_status,
                           receipts=receipts,
                           total_price=total_price,
                           status_colors=self.status_colors)

    @expose('/receipt-update/<int:receipt_id>')
    def receipt_detail_update(self, receipt_id):

        user_permission = utils.get_user_permission(current_user.id)

        if user_permission.User_Role.update_receipt:

            product_id = request.args.get('product_id')

            product_name = request.args.get('product_name')

            receipt_details, total_price = utils.load_receipt_detail(receipt_id, product_id, product_name)

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
                               err_msg = 'Bạn phải được cấp quyền mới được sử dụng chức năng này')


    @expose('/view-delivery-note/<int:receipt_id>')
    def view_delivery_note(self, receipt_id):
        receipt = utils.get_receipt_by_id(receipt_id)

        receipt_details, total_price = utils.load_receipt_detail(receipt_id)

        total_in_words = num2words(total_price, lang='vi').capitalize() + " đồng "

        now = datetime.now()

        delivery_code = utils.generate_delivery()

        return self.render('admin/delivery_form.html',
                           receipt= receipt,
                           receipt_details= receipt_details,
                           total_price=total_price,
                           total_in_words=total_in_words,
                           now=now,
                           delivery_code=delivery_code,
                           delivery_note=None)


    @expose('create-delivery-note/<int:receipt_id>/<delivery_code>', methods=['POST'])
    def create_delivery_note(self, receipt_id=None, delivery_code=None):

        created_date=datetime.now()

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
            note =  request.form.get(f'note_{detail.product_id}')

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

        users = utils.load_user(user_id, asc)

        users_role = utils.load_user_role()



        return self.render('admin/privileged.html',
                           users = users,
                           users_role=users_role)


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





admin = Admin(app=app, name = "ANNNPTT Website", template_mode="bootstrap4", index_view=MyAdminIndex())
admin.add_view(UserView(User, db.session, name='Người dùng', endpoint='user_admin'))
admin.add_view(ProductView(Product, db.session))
admin.add_view(CategoryView(Category, db.session))
admin.add_view(CustomerView(User, db.session, name='Khách hàng', endpoint='customer_admin'))
admin.add_view(ReceiptView(Receipt, db.session, name='Hóa đơn', endpoint='receipt'))
# admin.add_view(ReceiptDetailView(ReceiptDetail, db.session, name='Receipt Detail', endpoint='receipt_detail'))
admin.add_view(DeliveryNoteView(Goods_Delivery_Note, db.session, name='Xuất kho', endpoint='goods_delivery'))
admin.add_view(ReceiveNoteView(Goods_Received_Note, db.session, name='Nhập kho', endpoint='goods_receive'))
admin.add_view(OrderProductView(Goods_Received_Note, db.session, name='Đặt hàng hóa', endpoint='order_product'))
admin.add_view(StatsView(Receipt, db.session, name='Thống kê', endpoint='product_stats'))
admin.add_view(UserRoleView(User_Role, db.session, name='Phân quyền', endpoint='user_privileged'))
admin.add_view(LogoutView(name='Đăng xuất'))



