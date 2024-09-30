from flask import Flask, flash
from flask import render_template, request, redirect, session, jsonify, url_for
from Flask_App import app, login, utils, db
import math
import cloudinary.uploader
from flask_login import login_user, logout_user, login_required, current_user
from Flask_App.models import Receipt_Report, DiscountType, Receipt, ReceiptDetail
from Suggest import recommendSimilarProducts, recommend_products_by_user_receipt

@app.route('/')
def home():

    page = request.args.get('page', 1)

    cate_id = request.args.get('category_id')

    kw = request.args.get('kw')

    products = utils.load_products(cate_id = cate_id, kw = kw, page=int(page))

    all_products = utils.load_all_products()

    cate_name = utils.get_cate_by_id(cate_id)

    counter = utils.count_product(cate_id=cate_id, kw = kw)

    prev_page = url_for('home', page=int(page) - 1) if int(page) > 1 else None
    next_page = url_for('home', page=int(page) + 1)

    recommend_id = None
    if current_user.is_authenticated:
        recommend_id = recommend_products_by_user_receipt(current_user.id)

    return render_template('index.html',
                           scroll='something',
                           products=products,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']),
                           prev_page=prev_page,
                           next_page=next_page,
                           cate_name=cate_name,
                           recommend_id=recommend_id,
                           all_products=all_products
                           )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = utils.get_product_by_id(product_id)

    products = utils.load_all_products()

    comments = utils.get_comments(product_id=product_id,
                                  page=int(request.args.get('page', 1)))

    suggest_id = recommendSimilarProducts(product_id, NUMBER = 5)

    suggest_id = sorted(suggest_id)


    return render_template('product_detail.html',
                           comments=comments,
                           product = product,
                           pages = math.ceil(utils.count_comment(product_id)/app.config['COMMENT_SIZE']),
                           products=products,
                           suggest_id=suggest_id,
                           discountType=DiscountType
                           )


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                utils.add_user(name=name, username=username,
                               password=password, email=email,
                               avatar = avatar_path)
                return redirect("/user-login")
            else:
                err_msg = "Mật khẩu không khớp"

        except Exception as e:
            err_msg = "Hệ thống đang có lỗi " + str(e)


    return render_template('register.html', err_msg = err_msg)


@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ""
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next', 'home')
            return redirect(url_for(next))

        else:
            err_msg = 'Username hoặc password không chính xác'

    return render_template('login.html', err_msg = err_msg)


@app.route('/admin-login', methods=['post'])
def signin_admin():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login_admin(username=username,
                                 password=password)
        if user:
            login_user(user=user)
            return redirect('/admin')

        else:
            err_msg = 'Username hoặc password không chính xác'

        return redirect('/admin')


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect('/user-login')


@app.route('/api/comment', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    product_id = data.get('product_id')

    try:
        c = utils.add_comment(content=content, product_id=product_id)
    except:
        return {'status': 404, 'err_msg': 'Chương trình đang bị lỗi !!!'}

    return {'status': 201, 'comment': {
        'id': c.id,
        'content': c.content,
        'created_date': c.created_date,
        'user': {
            'username': current_user.username,
            'avatar': current_user.avatar
        }
    }}


@app.context_processor
def common_response():
    return {
        'categories': utils.load_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/products')    
def product_list():
    
    cate_id = request.args.get("category_id")

    kw = request.args.get("keyword")
    
    products = utils.load_products(cate_id=cate_id, kw=kw)
    
    return render_template('products.html',
                           products=products)


@app.route('/cart')
def cart():
    return render_template('cart.html',
                           stats = utils.count_cart(session.get('cart')),
                            payments = utils.load_payment()
                           )


@app.route('/user-receipt/<int:user_id>')
def user_receipt(user_id):

    receipt_id = request.args.get('receipt_id')

    asc = request.args.get('asc', 'True')

    status_id = request.args.get('status_id')

    user_receipt = utils.get_user_receipt(user_id=user_id, receipt_id=receipt_id, asc=asc, status_id=status_id)

    receipt_status = utils.load_receipt_status()

    need_confirm = utils.get_need_confirm_receipt(user_id)

    report_types = utils.load_report_types()

    status_colors = {
        1: 'btn-warning',
        2: 'btn-success',
        3: 'btn-info',
        4: 'btn-danger',
        5: 'btn-secondary',
        6: 'btn-primary'
    }

    if need_confirm:
        flash('Bạn có một đơn hàng cần xác nhận!', 'warning')

    return render_template('user_receipt.html',
                           user_receipt=user_receipt,
                           receipt_status=receipt_status,
                           report_types=report_types,
                           status_colors=status_colors)


@app.route('/confirm-receipt/<int:receipt_id>')
def confirm_receipt(receipt_id):
    try:

        confirmReceipt = Receipt.query.filter(Receipt.id.__eq__(receipt_id)).first()

        if confirmReceipt:

            confirmReceipt.status_id = 2

            db.session.commit()

            flash('Xác nhận đơn hàng thành công!', 'success')

        else:
            flash('Không tìm thấy hóa đơn!', 'danger')

    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')

    return redirect(f'/user-receipt/{current_user.id}')




@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.get_json()
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')
    image = data.get('image')
    promotion = data.get('promotion')



    cart = session.get('cart')
    if not cart:
        cart = {}



    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1,
            'image': image,
            'promotion': promotion
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route("/api/update-cart", methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')

    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route("/api/delete-cart/<product_id>", methods = ['delete'])
def delete_cart(product_id):
    cart = session.get('cart')

    if cart and product_id in cart:
        del cart[product_id]

        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/pay', methods=['post'])
def pay():
    data = request.json
    payment_id = data.get('payment_id')
    delivery_address = data.get('delivery_address')
    customer_name = data.get('customer_name')
    try:
        utils.add_receipt(session.get('cart'), payment_id, delivery_address, customer_name)
        del session['cart']
    except Exception as e:
        print(e)
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/api/delete-detail/<int:receipt_id>/<int:product_id>/<int:quantity>', methods=['DELETE'])
def delete_receipt_detail(receipt_id, product_id, quantity):
    try:
        # Tìm chi tiết hóa đơn cần xóa
        receipt_detail = ReceiptDetail.query.filter_by(receipt_id=receipt_id, product_id=product_id, quantity=quantity).first()

        if receipt_detail:
            # Xóa chi tiết hóa đơn khỏi cơ sở dữ liệu
            db.session.delete(receipt_detail)
            db.session.commit()

            # Trả về thông báo thành công
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Không tìm thấy chi tiết hóa đơn"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/delete-receipt/<int:receipt_id>', methods=['DELETE'])
def delete_receipt(receipt_id):
    try:
        receipt = Receipt.query.filter(Receipt.id==receipt_id).first()

        if receipt:

            receipt_details = ReceiptDetail.query.filter(ReceiptDetail.receipt_id==receipt_id).all()

            for detail in receipt_details:
                db.session.delete(detail)

            db.session.delete(receipt)

            db.session.commit()

            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Không tìm thấy chi tiết hóa đơn"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e) }), 500



@app.route('/api/update-receipt-details/<int:receipt_id>', methods=['PUT'] )
def update_receipt_details(receipt_id):
    try:
        data = request.json
        receipt_details = data.get('receipt_details', [])
        status_id = data.get('status_id')
        
        receipt = Receipt.query.filter(Receipt.id.__eq__(receipt_id)).first()
        receipt.status_id=status_id
        
        for detail in receipt_details:
            product_id = detail['product_id']
            quantity = detail['quantity']
            
            receipt_detail = ReceiptDetail.query.filter(ReceiptDetail.receipt_id==receipt_id, ReceiptDetail.product_id==product_id).first()
            if receipt_detail:
                receipt_detail.quantity = quantity
            else:
                return jsonify({"success": False, "message": "Không tìm thấy chi tiết hóa đơn"}), 404
            
        db.session.commit()
        
        return jsonify({"success": True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500



# EXAMPLE FOR RSUBMIT & REQUEST FORM IN PYTHON
@app.route('/update-user-privileged', methods=['POST'])
def update_user_privileged():
    user_id = request.form.get('user_id')

    super_user = request.form.get('super_user')

    if super_user:
        flash('Bạn không thể chỉnh sửa quyền của người dùng này !', 'danger')

        return redirect('/admin/user_privileged/')

    user_role = utils.get_user_role_permission(user_id)

    user_role = user_role.User_Role

    if user_role:
        user_role.view_user = 'view_user' in request.form
        user_role.view_customer = 'view_customer' in request.form
        user_role.view_receipt = 'view_receipt' in request.form
        user_role.view_stats = 'view_stats' in request.form
        user_role.update_receipt = 'update_receipt' in request.form
        user_role.view_product = 'view_product' in request.form
        user_role.update_product = 'update_product' in request.form
        user_role.order_product = 'order_product' in request.form
        user_role.receive_product = 'receive_product' in request.form
        user_role.login_admin = 'login_admin' in request.form
        user_role.privileged = 'privileged' in request.form

        db.session.commit()

    flash('Đã lưu thay đổi !', 'warning')

    return redirect('/admin/user_privileged/')


class Reicept_Report:
    pass


@app.route('/post-report/<int:receipt_id>', methods=['POST'])
def post_report(receipt_id):
    report_type = request.form.get('report_type')

    description = request.form.get('description')

    new_report = Receipt_Report(
        user_report = current_user.id,
        receipt_report = receipt_id,
        report_type = report_type,
        description = description
    )

    receipt_reported = Receipt.query.filter(Receipt.id==receipt_id).first()
    receipt_reported.status_id = 3

    db.session.add(new_report)
    db.session.commit()

    flash("Đã gửi phản hồi", "warning")

    return redirect(f'/user-receipt/{current_user.id}')



@app.route("/user-receipt-detail/<int:receipt_id>")
def user_receipt_detail(receipt_id):
    receipt = utils.get_receipt_by_id_2(receipt_id)

    receipt_detail, total_price = utils.load_receipt_detail(receipt_id)

    status_colors = {
        1: 'btn-warning',
        2: 'btn-success',
        3: 'btn-info',
        4: 'btn-danger',
        5: 'btn-secondary',
        6: 'btn-primary'
    }


    return render_template('user_receipt_detail.html',
                           receipt = receipt,
                           receipt_detail = receipt_detail,
                           total_price = total_price,
                           status_colors = status_colors)


@app.route("/account-setting")
def account_setting():
    return render_template("account_setting.html")



@app.route("/update-account/<int:user_id>", methods=['POST'])
def saves_change_account(user_id):
    try:
        data = request.json
        fullname = data.get('fullname')
        username = data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        address = data.get('user_address')

        utils.changes_user_info(user_id = user_id,
                                fullname=fullname,
                                username=username,
                                email=email,
                                phone_number=phone_number,
                                address=address
                                )
        return jsonify({'code': 200}),


    except:
        return jsonify({'code': 404})


if __name__ == "__main__":
    from Flask_App.admin import *
    app.run(debug=True)