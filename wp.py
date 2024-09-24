from flask_login import current_user

from Flask_App.models import Distribution, User, User_Role, Privileged, Product, Goods_Received_Note, Provider
from Flask_App import app, db, utils

import requests




with app.app_context():
    pass