from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ініціалізація розширень
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Налаштування Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'
    login_manager.login_message_category = 'info'
    
    # Контекстний процесор для CSRF токена
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    # Реєстрація blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.books import books_bp
    from app.routes.authors import authors_bp
    from app.routes.genres import genres_bp
    from app.routes.users import users_bp
    from app.routes.reviews import reviews_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(authors_bp)
    app.register_blueprint(genres_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)
    
    return app
