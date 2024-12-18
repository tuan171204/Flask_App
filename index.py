from flask import render_template, request, redirect, session, jsonify, url_for, flash
from sympy.codegen.fnodes import product_
from Flask_App import app, login, utils, db, socketio
import cloudinary.uploader
from flask_login import login_user, logout_user, login_required, current_user
from Flask_App.models import Receipt_Report, DiscountType, Receipt, ReceiptDetail, Ward
from flask_socketio import join_room, leave_room, send
import random
from string import ascii_uppercase
import logging
from Flask_App.chat_rooms import rooms


@app.route('/')
def intro():
    return render_template('intro.html')


@app.route('/product')
def home():
    page = request.args.get('page', 1)

    cate_id = request.args.get('category_id')

    kw = request.args.get('kw')

    products = utils.load_products(cate_id=cate_id, kw=kw, page=int(page))

    all_products = utils.load_all_products()

    cate_name = utils.get_cate_by_id(cate_id)

    counter = utils.count_product(cate_id=cate_id, kw=kw)

    brands = utils.load_all_brands()

    prev_page = url_for('home', page=int(page) - 1) if int(page) > 1 else None
    next_page = url_for('home', page=int(page) + 1)

    return render_template('index.html',
                           scroll='something',
                           products=products,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']),
                           prev_page=prev_page,
                           next_page=next_page,
                           cate_name=cate_name,
                           all_products=all_products,
                           brands=brands
                           )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = utils.get_product_detail_info(product_id)

    products = utils.load_all_products()

    comments = utils.get_comments(product_id=product_id,
                                  page=int(request.args.get('page', 1)))
    #
    # suggest_id = recommendSimilarProducts(product_id, NUMBER=8)
    #
    # suggest_id = sorted(suggest_id)

    return render_template('product_detail.html',
                           comments=comments,
                           product=product,
                           pages=math.ceil(utils.count_comment(product_id) / app.config['COMMENT_SIZE']),
                           products=products,
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
                               avatar=avatar_path)
                return redirect("/user-login")
            else:
                err_msg = "Mật khẩu không khớp"

        except Exception as e:
            err_msg = "Hệ thống đang có lỗi " + str(e)

    return render_template('register.html', err_msg=err_msg)


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

    return render_template('login.html', err_msg=err_msg)


@app.route('/admin-login', methods=['post'])
def signin_admin():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login_admin(username=username,
                                       password=password)
        if user:
            login_user(user=user)
            flash("Đăng nhập thành công ", "success")
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
    except Exception as e:
        return {'status': 404, 'err_msg': f'Lỗi {e}'}

    return {
        'status': 201,
        'comment': {
            'id': c.id,
            'content': c.content,
            'created_date': c.created_date,
            'user': {
                'username': current_user.username,
                'avatar': current_user.avatar
            }
        }
    }, 201


@app.context_processor
def common_response():
    return {
        'categories': utils.load_categories_client(),
        'cart_stats': utils.count_cart(session.get('cart')),
        'all_products': utils.load_all_products()
    }


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/cart')
def cart():
    district, ward = utils.get_address()
    return render_template('cart.html',
                           stats=utils.count_cart(session.get('cart')),
                           payments=utils.load_payment(),
                           district=district,
                           ward=ward
                           )


@app.route('/api/get_ward/<int:district_id>')
def get_ward(district_id):
    wards = Ward.query.filter(Ward.district_id == district_id).all()
    ward_list = [{'id': w.id, 'name': w.name} for w in wards]
    return jsonify(ward_list)


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
        flash('Bạn có đơn hàng cần xác nhận!', 'warning')

    return render_template('user_receipt.html',
                           user_receipt=user_receipt,
                           receipt_status=receipt_status,
                           report_types=report_types,
                           status_colors=status_colors)


@app.route('/confirm-receipt/<int:receipt_id>', methods=['POST'])
def confirm_receipt(receipt_id):
    try:
        rating = request.form.get('rating')

        confirmReceipt = Receipt.query.filter(Receipt.id.__eq__(receipt_id)).first()

        if confirmReceipt:

            confirmReceipt.status_id = 2
            confirmReceipt.rating_service = rating

            db.session.commit()

            flash('Xác nhận đơn hàng thành công!', 'success')

        else:
            flash('Không tìm thấy hóa đơn!', 'danger')

    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')

    return redirect(f'/user-receipt/{current_user.id}')


@app.route('/api/add-cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        id = str(data.get('id'))
        name = data.get('name')
        price = float(data.get('price'))
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

    except Exception as e:
        print(f"Lỗi server index: {str(e)}")


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


@app.route("/api/delete-cart/<product_id>", methods=['delete'])
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
    momo_code = data.get('momo_code', '')
    try:
        utils.add_receipt(session.get('cart'), payment_id, delivery_address, customer_name, momo_code)
        del session['cart']
    except Exception as e:
        print(f'Lỗi index {e}')
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/api/delete-detail/<int:receipt_id>/<int:product_id>/<int:quantity>', methods=['DELETE'])
def delete_receipt_detail(receipt_id, product_id, quantity):
    try:
        receipt_detail = ReceiptDetail.query.filter_by(receipt_id=receipt_id, product_id=product_id,
                                                       quantity=quantity).first()

        if receipt_detail:
            db.session.delete(receipt_detail)
            db.session.commit()

            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Không tìm thấy chi tiết hóa đơn"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/delete-receipt/<int:receipt_id>', methods=['DELETE'])
def delete_receipt(receipt_id):
    try:
        receipt = Receipt.query.filter(Receipt.id == receipt_id).first()

        if receipt:

            receipt_details = ReceiptDetail.query.filter(ReceiptDetail.receipt_id == receipt_id).all()

            for detail in receipt_details:
                db.session.delete(detail)

            db.session.delete(receipt)

            db.session.commit()

            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Không tìm thấy chi tiết hóa đơn"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/update-receipt-details/<int:receipt_id>', methods=['PUT'])
def update_receipt_details(receipt_id):
    try:
        data = request.json
        receipt_details = data.get('receipt_details', [])
        status_id = data.get('status_id')

        receipt = Receipt.query.filter(Receipt.id.__eq__(receipt_id)).first()
        receipt.status_id = status_id

        for detail in receipt_details:
            product_id = detail['product_id']
            quantity = detail['quantity']

            receipt_detail = ReceiptDetail.query.filter(ReceiptDetail.receipt_id == receipt_id,
                                                        ReceiptDetail.product_id == product_id).first()
            if receipt_detail:
                receipt_detail.quantity = quantity
            else:
                return jsonify({"success": False, "message": "Không tìm thấy chi tiết hóa đơn"}), 404

        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# EXAMPLE FOR SUBMIT & REQUEST FORM IN PYTHON
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


@app.route('/post-report/<int:receipt_id>', methods=['POST'])
def post_report(receipt_id):
    report_type = request.form.get('report_type')

    description = request.form.get('description')

    new_report = Receipt_Report(
        user_report=current_user.id,
        receipt_report=receipt_id,
        report_type=report_type,
        description=description
    )

    receipt_reported = Receipt.query.filter(Receipt.id == receipt_id).first()
    receipt_reported.status_id = 3

    db.session.add(new_report)
    db.session.commit()

    flash("Đã gửi phản hồi", "warning")

    return redirect(f'/user-receipt/{current_user.id}')


@app.route("/user-receipt-detail/<int:receipt_id>")
def user_receipt_detail(receipt_id):
    receipt = utils.get_receipt_by_id_2(receipt_id)

    receipt_detail, total_price, base_total_price = utils.load_receipt_detail_admin(receipt_id)

    status_colors = {
        1: 'btn-warning',
        2: 'btn-success',
        3: 'btn-info',
        4: 'btn-danger',
        5: 'btn-secondary',
        6: 'btn-primary'
    }

    return render_template('user_receipt_detail.html',
                           receipt_id=receipt_id,
                           receipt=receipt,
                           receipt_detail=receipt_detail,
                           total_price=total_price,
                           status_colors=status_colors,
                           base_total_price=base_total_price)


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

        utils.changes_user_info(user_id=user_id,
                                fullname=fullname,
                                username=username,
                                email=email,
                                phone_number=phone_number,
                                address=address
                                )
        return jsonify({'code': 200}),

    except Exception as e:
        return jsonify({'code': 404})


@app.route('/api/check_category_id/<int:category_id>', methods=['GET'])
def check_category_id(category_id):
    if utils.check_category_id(category_id):
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})


@app.route('/api/check_change_category_id/<int:base_id>/<int:category_id>', methods=['GET'])
def check_change_category_id(base_id, category_id):
    if utils.check_change_category_id(base_id, category_id):
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})


@app.route('/api/load_product/<int:provider_id>')
def load_product(provider_id):
    products = utils.get_product_by_provider(provider_id)

    product_list = [{'id': p.id, 'name': p.name} for p in products]

    return jsonify(product_list)


@app.route('/api/change_status_product/', methods=['PUT'])
def deactive_product():
    try:
        data = request.json
        func = data.get('func')
        products_id = data.get('products_id', [])

        if func == 'active':
            for id in products_id:
                if id:
                    product = Product.query.filter(Product.id == id).first()
                    product.active = True
                else:
                    pass

        elif func == 'deactive':
            for id in products_id:
                if id:
                    product = Product.query.filter(Product.id == id).first()
                    product.active = False
                else:
                    pass

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 404

    db.session.commit()
    return jsonify({"success": True, "message": "Đã lưu thay đổi"}), 200


@app.route('/api/delete_warranty/<int:warranty_id>', methods=['DELETE'])
def delete_warranty(warranty_id):
    warranty = Warranty.query.get(warranty_id)

    if not warranty:
        return jsonify({"error": "Không tìm thấy chương trình bảo hành"}), 404

    try:
        utils.delete_warranty(warranty_id)

        return jsonify({"success": True, "message": "Xoá chương trình bảo hành thành công"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/delete_apply_warranty/', methods=['DELETE'])
def delete_apply_warranty():
    data = request.get_json()
    warranty_id = data.get('warranty_id')
    product_id = data.get('product_id')
    warranty = Warranty.query.get(warranty_id)

    if not warranty:
        return jsonify({"error": "Không tìm thấy bảo hành và sản phẩm áp dụng"}), 404

    try:
        utils.delete_warranty_detail(warranty_id, product_id)

        return jsonify({"success": True, "message": "Xóa bỏ bảo hành thành công"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/apply_warranty', methods=['PUT'])
def apply_warranty():
    try:
        data = request.get_json()
        warranty_id = data.get('warranty_id')
        products = data.get('products', [])

        if not products:
            return jsonify({"success": False, "message": "Không có sản phẩm nào được chọn"}), 400

        for product in products:
            product_id = product.get('product_id')
            warranty_period = product.get('warranty_period')
            time_unit = product.get('time_unit')

            if not product_id or not warranty_period or not time_unit:
                continue

            utils.apply_warranty(
                product_id=product_id,
                warranty_id=warranty_id,
                warranty_period=warranty_period,
                time_unit=time_unit
            )

        return jsonify({"success": True, "message": "Áp dụng bảo hành thành công"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Đã có lỗi khi áp dụng bảo hành"}), 500


@app.route('/api/update_warranty', methods=['PUT'])
def update_warranty():
    try:
        data = request.get_json()
        description = data.get('description')
        warranty_id = data.get('warranty_id')

        warranty = Warranty.query.filter(Warranty.id == warranty_id).first()
        warranty.description = description

        db.session.commit()

        return jsonify({"success": True, "message": "Thay đổi thông tin bảo hành thành công"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Đã có lỗi khi cập nhật"}), 500


@app.route('/api/change_warranty_detail', methods=['PUT'])
def change_warranty_detail():
    data = request.get_json()
    warranty_id = data.get('warranty_id')
    product_id = data.get('product_id')
    period = data.get('period')
    time_unit = data.get('time_unit')
    if time_unit == 'TimeUnitEnum.MONTH':
        time_unit = 'MONTH'

    if time_unit == 'TimeUnitEnum.YEAR':
        time_unit = 'YEAR'

    if time_unit == 'TimeUnitEnum.WEEK':
        time_unit = 'WEEK'

    try:
        utils.update_warranty_detail(warranty_id=warranty_id,
                                     product_id=product_id,
                                     period=period,
                                     time_unit=time_unit)

        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/support-chat-room', methods=['GET'])
def support_chat_room():
    session.clear()

    room = f'ROOM{random.randint(100, 999)}'
    name = "Khách"

    if room not in rooms:
        rooms[room] = {"members": 0, "messages": []}

    session["room"] = room  # store room_code in user session
    session["name"] = name  # store user_name in user session

    return redirect(url_for("room"))


@app.route("/room")
def room():
    room = session.get("room")
    name = session.get("name")

    if room is None or name is None:
        return redirect(url_for("support_chat_room"))

    return render_template("chat_room.html",
                           code=room,
                           name=name,
                           messages=rooms[room]["messages"],
                           join=True)


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }

    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


# DATA BUSINESS ANALYST

@app.route('/revenue-data')
def revenue_data():
    statistics = utils.calculate_revenue_statistics()
    revenue_yearly = statistics['revenue_yearly']
    years_labels = revenue_yearly.apply(lambda row: f"Năm {row['year']}", axis=1)

    revenue_monthly = statistics['revenue_monthly']
    revenue_monthly = revenue_monthly[revenue_monthly['year'] == datetime.now().year]
    months_labels = revenue_monthly.apply(lambda row: f"Tháng {row['month']}", axis=1)

    revenue_quarterly = statistics['revenue_quarterly']
    revenue_quarterly = revenue_quarterly[revenue_quarterly['year'] == datetime.now().year]
    quarters_labels = revenue_quarterly.apply(lambda row: f'Quý {row['quarter']}', axis=1)

    avg_revenue_monthly = statistics['avg_revenue_monthly']
    avg_revenue_monthly = avg_revenue_monthly[avg_revenue_monthly['year'] == datetime.now().year]
    avg_revenue_months_labels = avg_revenue_monthly.apply(lambda row: f'Năm {row['year']}', axis=1)

    avg_revenue_quarterly = statistics['avg_revenue_quarterly']
    avg_revenue_quarterly = avg_revenue_quarterly[avg_revenue_quarterly['year'] == datetime.now().year]
    avg_revenue_quarters_labels = avg_revenue_quarterly.apply(lambda row: f'Năm {row['year']}', axis=1)

    data = {
        'years': years_labels.tolist(),
        'revenue_yearly': revenue_yearly['total_amount'].tolist(),

        'months': months_labels.tolist(),
        'revenue_monthly': revenue_monthly['total_amount'].tolist(),

        'quarters': quarters_labels.tolist(),
        'revenue_quarterly': revenue_quarterly['total_amount'].tolist(),

        'avg_months': avg_revenue_months_labels.tolist(),
        'avg_revenue_monthly': avg_revenue_monthly['avg_revenue_monthly'].tolist(),

        'avg_quarters': avg_revenue_quarters_labels.tolist(),
        'avg_revenue_quarterly': avg_revenue_quarterly['avg_revenue_quarterly'].tolist(),
    }

    return jsonify(data)


@app.route('/revenue-data-by-year', methods=['POST'])
def revenue_data_by_year():
    data = request.get_json()
    year = data.get('year')
    time_unit = data.get('time_unit')

    statistics = utils.calculate_revenue_statistics()

    if time_unit == 'month':
        revenue_monthly = statistics['revenue_monthly']
        revenue_monthly = revenue_monthly[revenue_monthly['year'] == int(year)]

        months_labels = revenue_monthly.apply(lambda row: f"Tháng {row['month']}", axis=1)

        return jsonify({
            'months': months_labels.tolist(),
            'revenue_monthly': revenue_monthly['total_amount'].tolist()
        })

    if time_unit == 'quarter':
        revenue_quarterly = statistics['revenue_quarterly']
        revenue_quarterly = revenue_quarterly[revenue_quarterly['year'] == int(year)]

        quarters_labels = revenue_quarterly.apply(lambda row: f'Quý {row['quarter']}', axis=1)

        return jsonify({
            'quarters': quarters_labels.tolist(),
            'revenue_quarterly': revenue_quarterly['total_amount'].tolist()
        })

    if time_unit == 'avg_month':
        avg_revenue_monthly = statistics['avg_revenue_monthly']
        avg_revenue_monthly = avg_revenue_monthly[avg_revenue_monthly['year'] == int(year)]

        avg_months_labels = avg_revenue_monthly.apply(lambda row: f'Năm {row['year']}', axis=1)

        return jsonify({
            'avg_months': avg_months_labels.tolist(),
            'avg_revenue_monthly': avg_revenue_monthly['avg_revenue_monthly'].tolist()
        })

    if time_unit == 'avg_quarter':
        avg_revenue_quarterly = statistics['avg_revenue_quarterly']
        avg_revenue_quarterly = avg_revenue_quarterly[avg_revenue_quarterly['year'] == int(year)]

        avg_quarters_labels = avg_revenue_quarterly.apply(lambda row: f'Năm {row['year']}', axis=1)

        return jsonify({
            'avg_quarters': avg_quarters_labels.tolist(),
            'avg_revenue_quarterly': avg_revenue_quarterly['avg_revenue_quarterly'].tolist()
        })


@app.route('/api/apply-promotion', methods=['POST'])
def apply_promotion():
    data = request.get_json()
    promotion_id = data.get('promotion_id')
    products = data.get('products', [])

    try:
        for product in products:
            product_id = product['product_id']
            discount_value = product['discount_value']
            discount_type = product['discount_type']

            success = utils.apply_promotion_to_product(promotion_id=str(promotion_id),
                                                       product_id=product_id,
                                                       discount_value=discount_value,
                                                       discount_type=discount_type)
            if not success:
                raise Exception("Có lỗi khi thêm khuyến mãi vào sản phẩm")

        db.session.commit()
        return jsonify({"success": True, "msg": "Áp dụng khuyến mãi thành công"}), 200

    except Exception as e:
        print(f'Error index: {e}')
        return jsonify({"success": False, "msg": f"{str(e)}"}), 500


@app.route('/brand-product-data', methods=["GET"])
def brand_product_data():
    brand_id = request.args.get('brand_id')

    if brand_id is None:
        return jsonify({"success": False, "message": "Không tìm thấy mã khuyến mãi"}), 400

    products = utils.load_product_brand(brand_id)

    products_data = [{
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "image": product.image
    } for product in products]

    return jsonify({"success": True, "products": products_data})


@app.route("/api/delete-product-provider", methods=["PUT"])
def delete_product_provider():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        provider_id = data.get('provider_id')

        utils.delete_product_provider(product_id)

        return jsonify({"success": True, "message": 'Tạm ngưng sản phẩm cung cấp thành công'})

    except Exception as e:
        print("Lỗi server: ", str(e))
        return jsonify({"success": False, "message": f'Lỗi server: {str(e)}'})


@app.route("/api/active-product-provider", methods=["PUT"])
def active_product_provider():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        provider_id = data.get('provider_id')

        utils.active_product_provider(product_id, provider_id)

        return jsonify({"success": True, "message": 'Tiếp tục bán sản phẩm cung cấp thành công'})

    except Exception as e:
        print("Lỗi server: ", str(e))
        return jsonify({"success": False, "message": f'Lỗi server: {str(e)}'})


@app.route("/api/deactive_provider", methods=['PUT'])
def deactive_provider():
    try:
        data = request.get_json()
        provider_id = data.get('provider_id')

        result = utils.deactive_provider(provider_id)

        if result:
            return jsonify({"success": True, "message": result['message']})

        else:
            return jsonify({"success": False, "message": result['message']})

    except Exception as e:
        print(f"Lỗi server: {e}")

        return jsonify({"success": False, "message": f"Lỗi server: {e}"})


@app.route("/api/check-duplicate-provider-name", methods=["POST"])
def check_duplicate_provider_name():
    data = request.get_json()
    new_provider_name = data.get('provider_name')

    provider = Provider.query.filter(Provider.name == new_provider_name).first()

    if provider:
        return {"duplicate": True}

    else:
        return {"duplicate": False}


if __name__ == "__main__":
    from Flask_App.admin import *

    socketio.run(app, debug=True)
