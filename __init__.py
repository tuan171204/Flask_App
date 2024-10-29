import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, manage_session=False, logger=True, async_mode='gevent')

app.secret_key = 'ajwdnkjabwhdkbalwdajwd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tuan:123456tuan@localhost/labsaledb2?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 8
app.config['COMMENT_SIZE'] = 20
app.config['VIEW_SIZE'] = 10

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app=app)
migrate = Migrate(app, db)

cloudinary.config(
    cloud_name='dr4hg7vdv',
    api_key='219231189323661',
    api_secret='13au1HyrP1GXpZhf3d5fM09OPEs',
)

login = LoginManager(app=app)
