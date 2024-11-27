import json
import string
import random
from Flask_App.tests.conftest import client
from Flask_App import app
from unittest.mock import Mock
import math
import pytest
from flask import session, flash


def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits  # Bao gồm chữ cái (hoa + thường) và số
    return ''.join(random.choices(characters, k=length))


def test_intro_route(client):
    response = client.get('/')
    assert response.status_code == 200


def test_user_register_get(client):
    response = client.get('/register')
    assert response.status_code == 200


def test_user_register_post(client):
    response = client.post('/register', data={
        'name': 'Test user',
        'username': generate_random_string(),
        'password': 'password',
        'confirm': 'password',
        'email': 'testuser@example.com'
    })

    assert response.status_code == 302  # redirect
    assert response.location.endswith('/user-login')


def test_user_signin_get(client):
    response = client.get('/user-login')
    assert response.status_code == 200


def test_add_comment_unauthorized(client):
    response = client.post('/api/comment', json={
        'content': 'Great product!',
        'product_id': 123
    })
    assert response.status_code == 401  # unauthorized


def test_add_comment_authorized(client, mocker):
    with client.session_transaction() as session:
        session['_user_id'] = 1

    mocker.patch('Flask_App.utils.add_comment', return_value=Mock(
        id=1, content='Great product!', created_date='2024-11-22'
    ))

    response = client.post('/api/comment', json={
        'content': 'Great product!',
        'product_id': 123
    })

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['status'] == 201
    assert json_data['comment']['content'] == 'Great product!'
    assert json_data['comment']['id'] == 1


def mock_get_address():
    mock_district = Mock(name='District 1', id=1)
    mock_ward = Mock(name='Ward 1', id=1)
    return [mock_district], [mock_ward]


def mock_count_cart(cart):
    return len(cart) if cart else 0


def mock_load_payment():
    return [
        Mock(name='Credit Card', id=1),
        Mock(name='PayPal', id=2)
    ]


def test_cart(client, mocker):
    mocker.patch('Flask_App.utils.get_address', side_effect=mock_get_address)
    mocker.patch('Flask_App.utils.count_cart', side_effect=mock_count_cart)
    mocker.patch('Flask_App.utils.load_payment', side_effect=mock_load_payment)

    with client.session_transaction() as sess:
        sess['cart'] = {
            '1': {
                'id': '1',
                'name': 'Product 1',
                'price': 100000.0,
                'quantity': 2,
                'image': 'image1.jpg',
                'promotion': 'giảm giá 10 %'
            },
            '2': {
                'id': '2',
                'name': 'Product 2',
                'price': 200000.0,
                'quantity': 1,
                'image': 'image2.jpg',
                'promotion': None
            },
            '3': {
                'id': '3',
                'name': 'Product 3',
                'price': 300000.0,
                'quantity': 2,
                'image': 'image3.jpg',
                'promotion': 'Mua 1 tặng 1'
            }
        }

    response = client.get('/cart')

    assert response.status_code == 200


def test_delete_receipt_detail_success(client, mocker):
    with app.app_context():
        mock_receipt_detail = Mock()
        mocker.patch(
            'Flask_App.models.ReceiptDetail.query.filter_by',
            return_value=Mock(first=Mock(return_value=mock_receipt_detail))
        )

        mock_delete = mocker.patch('Flask_App.db.session.delete')
        mock_commit = mocker.patch('Flask_App.db.session.commit')

        response = client.delete('/api/delete-detail/2/17/2')

        assert response.status_code == 200

        response_data = json.loads(response.data)
        assert response_data["success"] is True

        mock_delete.assert_called_once_with(mock_receipt_detail)
        mock_commit.assert_called_once()


def test_delete_receipt_detail_not_found(client, mocker):
    with app.app_context():
        mocker.patch(
            'Flask_App.models.ReceiptDetail.query.filter_by',
            return_value=Mock(first=Mock(return_value=None))
        )
        response = client.delete('/api/delete-detail/1/101/2')

        assert response.status_code == 404

        response_data = json.loads(response.data)
        assert response_data["success"] is False
        assert response_data["message"] == "Không tìm thấy chi tiết hóa đơn"


def test_delete_receipt_detail_exception(client, mocker):
    with app.app_context():
        mocker.patch(
            'Flask_App.models.ReceiptDetail.query.filter_by',
            side_effect=Exception("Test Exception")
        )

        mock_rollback = mocker.patch('Flask_App.db.session.rollback')

        response = client.delete('/api/delete-detail/2/17/2')

        assert response.status_code == 500

        response_data = json.loads(response.data)
        assert response_data["success"] is False
        assert "Test Exception" in response_data["message"]

        mock_rollback.assert_called_once()


def test_post_report_success(client, mocker):
    with app.app_context():
        mock_current_user = Mock()
        mock_current_user.id = 1
        mocker.patch('Flask_App.index.current_user', mock_current_user)

        mock_receipt = Mock(
            id=2,
            user_id=7,
            status_id=None
        )
        mocker.patch(
            'Flask_App.models.Receipt.query.filter',
            return_value=Mock(first=Mock(return_value=mock_receipt))
        )

        mock_receipt_reported = Mock(
            user_report=1,
            receipt_report=2,
            report_type=1,
            description='Giá không đúng như quảng cáo'
        )
        mock_add = mocker.patch('Flask_App.db.session.add', return_value=mock_receipt_reported)
        mock_commit = mocker.patch('Flask_App.db.session.commit')

        response = client.post(
            '/post-report/2',
            data={
                'report_type': 1,
                'description': 'Giá không đúng như quảng cáo'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

        assert mock_receipt.status_id == 3

        mock_add.assert_called_once()
        added_report = mock_add.call_args[0][0]
        assert added_report.user_report == 1
        assert added_report.receipt_report == 1
        assert added_report.report_type == 1
        assert added_report.description == 'Giá không đúng như quảng cáo'

        mock_commit.assert_called_once()

        assert 'Đã gửi phản hồi' in response.data

        assert f'/user-receipt/{mock_current_user.id}' in response.request.path