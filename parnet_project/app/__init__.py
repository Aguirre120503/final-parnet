
from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db_singleton import get_db
from .models import Usuario, Rol

db = get_db()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        # Crear roles básicos
        if not Rol.query.filter_by(nombre="admin").first():
            admin_role = Rol(nombre="admin")
            client_role = Rol(nombre="cliente")
            db.session.add_all([admin_role, client_role])
            db.session.commit()

    # Registrar blueprints
    from .public_routes import public_bp
    from .admin_routes import admin_bp
    from .api_routes import api_bp
    from .auth import auth_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
