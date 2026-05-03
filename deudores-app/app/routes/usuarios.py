from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from app import db
from app.models import Circuito, Usuario
from app.routes.auth import login_required

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


def _get_usuario_actual():
    return db.session.get(Usuario, session['usuario_id'])


def _solo_admin_global(usuario):
    if not usuario.es_global:
        flash('Solo los administradores globales pueden gestionar usuarios.', 'danger')
        return False
    return True


def _get_circuitos():
    return db.session.execute(db.select(Circuito).order_by(Circuito.nombre)).scalars().all()


@usuarios_bp.route('/')
@login_required
def index():
    usuario = _get_usuario_actual()
    if not _solo_admin_global(usuario):
        return redirect(url_for('dashboard.index'))

    usuarios = db.session.execute(
        db.select(Usuario).order_by(Usuario.nombre)
    ).scalars().all()

    return render_template('usuarios/index.html', usuarios=usuarios, usuario=usuario)


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    usuario = _get_usuario_actual()
    if not _solo_admin_global(usuario):
        return redirect(url_for('dashboard.index'))

    circuitos = _get_circuitos()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        rol = request.form.get('rol', '').strip()
        circuito_id = request.form.get('circuito_id', '').strip() or None

        errores = []
        if not nombre:
            errores.append('El nombre es requerido.')
        if not username:
            errores.append('El nombre de usuario es requerido.')
        if not password:
            errores.append('La contraseña es requerida.')
        if rol not in (Usuario.ROL_GLOBAL, Usuario.ROL_NORMAL):
            errores.append('El rol seleccionado no es válido.')
        if not errores:
            duplicado = db.session.execute(
                db.select(Usuario).filter_by(username=username)
            ).scalar_one_or_none()
            if duplicado:
                errores.append(f'El nombre de usuario "{username}" ya está en uso.')

        if errores:
            for msg in errores:
                flash(msg, 'danger')
            return render_template(
                'usuarios/nuevo.html',
                circuitos=circuitos,
                usuario=usuario,
                form=request.form,
            )

        nuevo_usuario = Usuario(
            nombre=nombre,
            username=username,
            password_hash=generate_password_hash(password),
            rol=rol,
            circuito_id=int(circuito_id) if circuito_id else None,
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash(f'Usuario "{username}" creado correctamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template(
        'usuarios/nuevo.html',
        circuitos=circuitos,
        usuario=usuario,
        form={},
    )


@usuarios_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(usuario_id):
    usuario = _get_usuario_actual()
    if not _solo_admin_global(usuario):
        return redirect(url_for('dashboard.index'))

    objetivo = db.session.get(Usuario, usuario_id)
    if objetivo is None:
        abort(404)

    circuitos = _get_circuitos()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        rol = request.form.get('rol', '').strip()
        circuito_id = request.form.get('circuito_id', '').strip() or None

        errores = []
        if not nombre:
            errores.append('El nombre es requerido.')
        if rol not in (Usuario.ROL_GLOBAL, Usuario.ROL_NORMAL):
            errores.append('El rol seleccionado no es válido.')
        if errores:
            for msg in errores:
                flash(msg, 'danger')
            return render_template(
                'usuarios/editar.html',
                objetivo=objetivo,
                circuitos=circuitos,
                usuario=usuario,
                form=request.form,
            )

        objetivo.nombre = nombre
        objetivo.rol = rol
        objetivo.circuito_id = int(circuito_id) if circuito_id else None
        db.session.commit()

        flash(f'Usuario "{objetivo.username}" actualizado correctamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template(
        'usuarios/editar.html',
        objetivo=objetivo,
        circuitos=circuitos,
        usuario=usuario,
        form={},
    )
