from functools import wraps

from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash

from app import db
from app.models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['GET'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('circuitos.index'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash('Usuario y contraseña son requeridos.', 'danger')
        return redirect(url_for('auth.login'))

    usuario = db.session.execute(
        db.select(Usuario).filter_by(username=username)
    ).scalar_one_or_none()

    if usuario is None or not check_password_hash(usuario.password_hash, password):
        flash('Usuario o contraseña incorrectos.', 'danger')
        return redirect(url_for('auth.login'))

    session.clear()
    session['usuario_id'] = usuario.id
    session['rol'] = usuario.rol

    return redirect(url_for('circuitos.index'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
