from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    
    # Đăng ký Blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.user.routes import user_bp
    from app.admin.routes import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    with app.app_context():
        db.create_all()
        
    return app