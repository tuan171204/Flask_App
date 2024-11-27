window.addEventListener('load', function () {
    document.getElementById('loading-overlay').style.display = 'none';
});

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function (event) {
        if (!link.classList.contains('disable-loading')) {
            showLoading();
        }
    })
})




function addToCart(id, name, price, image, promotion) {
    event.preventDefault()
    // promise
    fetch('/api/add-cart', {
        method: 'POST',
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
    })
        .then(response => response.json())
        .then(data => {
            let counter = document.getElementsByClassName('cart-counter')
            for (let i = 0; i < counter.length; i++) {
                counter[i].innerText = data.total_quantity
            }
            console.log(data)

            alert("Thêm sản phẩm vào giỏ hàng thành công ! ")
        })
        .catch(function (err) {
            console.error("Lỗi :", err)
        })
}


function pay() {
    event.preventDefault();
    const fullNameInput = document.querySelector('input[name="fullname"]');
    const phoneNumInput = document.querySelector('input[name="phone_number"]')
    const payment = document.getElementById('payment')
    const district = document.querySelector("select[name='district']").value
    const ward = document.querySelector("select[name='ward']").value
    const address_detail = document.getElementById('delivery_address').value
    const delivery_address = `${address_detail}, ${ward}, ${district}, TP Hồ Chí Minh`
    console.log(delivery_address)

    if (!fullNameInput.value) {
        alert('Vui lòng nhập họ tên người nhận!');
        return;
    } else if (!phoneNumInput.value) {
        alert('Vui lòng nhập số điện thoại người nhận!');
        return
    } else if (!phoneNumInput.value.match(/^0[0-9]{9}$/)) {
        alert('Số điện thoại không hợp lệ!');
        return;
    } else if (!district || !ward || !address_detail) {
        alert('Vui lòng nhập đầy đủ địa chỉ');
        return;
    }

    if (confirm('Bạn chắc chắn muốn thanh toán không ?') == true) {
        fetch('/api/pay', {
            method: 'post',
            body: JSON.stringify({
                'customer_name': fullNameInput.value,
                'payment_id': payment.value,
                'delivery_address': delivery_address
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.code == 200) {
                location.reload();
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
        let base_amount = document.getElementById('base-amount')
        amount.innerHTML = new Intl.NumberFormat().format(data.total_amount) + "đ"
        base_amount.innerHTML = `<s>${new Intl.NumberFormat().format(data.base_total_amount)}đ </s>`
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


filterSearching = () => {
    const input = document.querySelector(".search-input")
    const filter = input.value.toUpperCase();
    const div = document.querySelector(".dropdown-content")
    const a = div.querySelectorAll(".dropdown-content-detail a");
    const displayElement = div.querySelectorAll(".dropdown-content-detail");
    for (let i = 0; i < a.length; i++) {
        txtValue = a[i].textContent || a[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            displayElement[i].style.display = "";
        } else {
            displayElement[i].style.display = "none";
        }
    }
}

window.addEventListener("load", function () {
    const middleElement = document.querySelector("#something")
    if (middleElement) {
        middleElement.scrollIntoView({
            behavior: "smooth",
            block: "start"
        })
    }
})

function getWard() {
    const district_input = document.querySelector('select[name="district"]')
    const selectedOption = district_input.options[district_input.selectedIndex];
    const districtId = selectedOption.getAttribute('data-district-id');
    console.log(districtId)

    if (districtId) {

        fetch(`/api/get_ward/${districtId}`)
            .then(response => response.json())
            .then(data => {

                const wardSelect = document.querySelector('select[name="ward"]');

                wardSelect.innerHTML = '<option value="">Phường</option>';

                data.forEach(ward => {
                    const option = document.createElement('option');
                    option.value = ward.name;
                    option.textContent = ward.name;
                    wardSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }
}

showSuggest = () => {
    document.querySelector(".dropdown-content").classList.toggle("show");
}


loadBrandProduct = async (brand_id) => {
    try {
        showLoading()
        const response = await fetch(`/brand-product-data?brand_id=${brand_id}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        })

        const data = await response.json()

        document.querySelector(".product-selling-place").innerHTML = ''

        if (data.success) {
            if (data.products.length >= 1) {
                data.products.forEach((p) => {
                    const productHTML = `
                            <div class="col-md-3 col-s-12 mb-4" style="padding: 5px;">
                                <div class="card hover-overlay h-100 container-overlay " style="padding: 10px;border-radius: 15px;">
                                    <a href="/product/${p.id}" style="height:250px;">
                                        <img class="card-img-top"
                                             src="/static/${p.image}"
                                             alt="Product"
                                             style="height:fit-content;">
                                    </a>
                                   <div class="card-body" style="bottom: 10px; position: relative;">
                                    <h4 class="card-title text-center">${p.name}</h4>
                                    <h5 class="text-danger font-weight-bold text-center product-price-card">${p.price.toLocaleString('vi-VN')}đ</h5>
                                  </div>
                                  <div class="overlay">
                                            <div class="overlay-content">
                                                <a href="/product/${p.id}"
                                                   class="btn mt-1 form-control text-left">
                                                Xem chi tiết
                                                </a>
                                            </div>
                                        </div>
                                </div>
                            </div>
                    `

                    document.querySelector(".product-selling-place").innerHTML += productHTML
                })
            } else {
                document.querySelector(".product-selling-place").innerHTML = `<h2 class="text-center alert alert-secondary col-12">Chưa có sản phẩm nào</h2>`
            }

            document.querySelector(".pagination-place ul").style.display = 'none'

            hideLoading()
        } else {
            console.error("Có lỗi xảy ra: ", data.error)
            hideLoading()
        }
    } catch (error) {
        console.error("Lỗi kết nối API: ", error)
        hideLoading()
    }
}







