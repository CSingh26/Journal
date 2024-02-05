from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Root%40123@localhost:3306/Journal'
app.config['SECRET_KEY'] = 'app@123'
app.config['SECURITY_PASSWORD_SALT'] = '2f1133c632c91094cb59ec8d11f7a0ee40cf065ea452d712'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'singh.chaiitanya@gmail.com'  
app.config['MAIL_PASSWORD'] = 'qsny iluw xfpe vtti' 

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail=Mail(app)

from app import routes