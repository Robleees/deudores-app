import os
from flask import Flask, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-cambiar-en-produccion')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'deudores.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.circuitos import circuitos_bp
    from app.routes.casas import casas_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(circuitos_bp)
    app.register_blueprint(casas_bp)

    @app.route('/')
    def index():
        if 'usuario_id' in session:
            return redirect(url_for('circuitos.index'))
        return redirect(url_for('auth.login'))

    with app.app_context():
        from app import models
        db.create_all()

    return app
