from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()  # Flask-Mail instance

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'yuytr jhf'  # Replace with your secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' # or your actual DB URI

    # Email configuration for Gmail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'redemptioncustomercare1@gmail.com'         # Replace with your Gmail
    app.config['MAIL_PASSWORD'] = 'gufo zvxi fnvn dnyq'       # Use a Gmail app password!

    db.init_app(app)
    mail.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app



