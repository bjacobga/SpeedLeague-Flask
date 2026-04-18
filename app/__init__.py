from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to submit a run.'

    from .auth import auth_bp, load_user_by_id

    @login_manager.user_loader
    def load_user(user_id):
        return load_user_by_id(user_id)

    app.register_blueprint(auth_bp)

    from .routes import main
    app.register_blueprint(main)

    return app
