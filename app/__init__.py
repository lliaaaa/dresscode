from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .models import db, User
from config import Config

migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # --- Create tables ---
    with app.app_context():
        db.create_all()

        if not User.query.first():
            admin = User(email="admin@site.com", role="admin")
            admin.set_password("12345")
            guard = User(email="guard@site.com", role="guard")
            guard.set_password("12345")
            db.session.add_all([admin, guard])
            db.session.commit()

    from .auth import bp as auth_bp
    from .routes import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'main.login'

    return app
