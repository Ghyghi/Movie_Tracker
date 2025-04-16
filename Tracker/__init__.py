# __init__.py
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
secret_key = os.getenv('SECRET_KEY')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
s = URLSafeTimedSerializer(secret_key)

def create_app():
    app = Flask(__name__)
    app.config.from_object('Tracker.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    from Tracker.models import User
    from .routes import register_routes

    @login_manager.user_loader
    def load_user(username):
        return User.query.get(username)
    
    with app.app_context():
        db.create_all()

    register_routes(app)
    
    return app
