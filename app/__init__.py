from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.extensions import db

from config import config

migrate = Migrate()
jwt = JWTManager()


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS'))

    from app.api.posts import posts_bp
    from app.api.comments import comments_bp
    from app.auth.routes import auth_bp
    from app.ui_routes import ui 

    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ui)

    return app
