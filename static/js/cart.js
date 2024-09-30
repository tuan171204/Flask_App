function addToCart(id, name, price, image, promotion) {
    event.preventDefault()
    // promise

    fetch('/api/add-cart', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'price': price,
            'image': image,
            'promotion': promotion,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function (res) {
        console.info(res)
        return res.json()

    }).then(function (data) {
        console.info(data)
        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < count.length; i++)
            counter[i].innerText = data.total_quantity
    }).catch(function (err) {
        console.error(err)
    })

    alert("Thêm sản phẩm vào giỏ hàng thành công ! ")
}


function pay() {
    event.preventDefault();
    const fullNameInput = document.querySelector('input[name="fullname"]');
    const phoneNumInput = document.querySelector('input[name="phone_number"]')
    const payment = document.getElementById('payment')
    const deli_address = document.getElementById('delivery_address')
    // Kiểm tra xem input đã được điền hay chưa
    if (!fullNameInput.value) {
        alert('Vui lòng nhập họ tên người nhận!');
        return; // Thoát khỏi hàm nếu không điền
    } else if (!phoneNumInput.value) {
        alert('Vui lòng nhập số điện thoại người nhận!');
        return
    } else if (!phoneNumInput.value.match(/^0[0-9]{9}$/)) {
        alert('Số điện thoại không hợp lệ!');
        return;
    }

    if (confirm('Bạn chắc chắn muốn thanh toán không ?') == true) {
        fetch('/api/pay', {
            method: 'post',
            body: JSON.stringify({
                'customer_name': fullNameInput.value,
                'payment_id': payment.value,
                'delivery_address': deli_address.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if (data.code === 200) {
                // Xử lý dữ liệu từ phản hồi, ví dụ:
                console.log(data.distributions, data.providers);
                location.reload(); // Nếu bạn vẫn muốn tải lại trang
            } else {
                console.error('Error:', data);
            }
        }).catch(err => console.error(err));
    }
}

    function updateCart(id, obj) {
        fetch('/api/update-cart', {
            method: 'put',
            body: JSON.stringify({
                'id': id,
                'quantity': parseInt(obj.value)
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            let counter = document.getElementsByClassName('cart-counter')
            for (let i = 0; i < counter.length; i++)
                counter[i].innerText = data.total_quantity

            let amount = document.getElementById('total-amount')
            amount.innerText = new Intl.NumberFormat().format(data.total_amount) + "đ"
        }).catch(err => console.error(err))
    }


    function deleteCart(id) {
        if (confirm("Bạn chắc chắn muốn xóa sản phẩm này chứ ?") == true) {
            fetch('/api/delete-cart/' + id, {
                method: 'delete',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json()).then(data => {
                let counter = document.getElementsByClassName('cart-counter')
                for (let i = 0; i < counter.length; i++)
                    counter[i].innerText = data.total_quantity

                let amount = document.getElementById('total-amount')
                amount.innerText = new Intl.NumberFormat().format(data.total_amount)

                let e = document.getElementById("product" + id)
                e.style.display = "none"
            }).catch(err => console.error(err))
        }
    }


    function add_comment(productId) {
        let content = document.getElementById("commentId")
        if (content !== null) {
            fetch('/api/comment', {
                method: 'post',
                body: JSON.stringify({
                    'product_id': productId,
                    'content': content.value
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json()).then(data => {
                if (data.status == 201) {
                    let c = data.comment

                    let area = document.getElementById("commentArea")

                    area.innerHTML = `<div class="row">
                                    <div class="col-md-1 col-xs-4">
                                        <img src="${c.user.avatar}"
                                             class="img-fluid rounded-circle" alt="avatar">
                                    </div>
                                    <div class="col-md-11 col-xs-8">
                                        <p><em>${moment(c.created_date).locale('vi').fromNow()}</em></p>
                                        <p>${c.created_date}</p>
                                    </div>
                                 </div>` + area.innerHTML
                } else if (data.status == 404) {
                    alert(data.err_msg)
                }
            })
        }
    }


