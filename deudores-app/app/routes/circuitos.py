from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app import db
from app.models import Circuito, Usuario
from app.routes.auth import login_required

circuitos_bp = Blueprint('circuitos', __name__, url_prefix='/circuitos')


def _get_usuario_actual():
    return db.session.get(Usuario, session['usuario_id'])


@circuitos_bp.route('/')
@login_required
def index():
    usuario = _get_usuario_actual()

    if usuario.es_global:
        circuitos = db.session.execute(db.select(Circuito).order_by(Circuito.nombre)).scalars().all()
    else:
        circuito = db.session.get(Circuito, usuario.circuito_id)
        circuitos = [circuito] if circuito else []

    return render_template('circuitos/index.html', circuitos=circuitos, usuario=usuario)


@circuitos_bp.route('/<int:circuito_id>')
@login_required
def detalle(circuito_id):
    usuario = _get_usuario_actual()

    if not usuario.es_global and usuario.circuito_id != circuito_id:
        abort(403)

    circuito = db.session.get(Circuito, circuito_id)
    if circuito is None:
        abort(404)

    casas = circuito.casas.filter_by(activa=True).all()
    saldo_total = sum(casa.saldo_actual() for casa in casas)

    return render_template(
        'circuitos/detalle.html',
        circuito=circuito,
        casas=casas,
        saldo_total=saldo_total,
        usuario=usuario,
    )


@circuitos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    usuario = _get_usuario_actual()

    if not usuario.es_global:
        flash('Solo los administradores globales pueden crear circuitos.', 'danger')
        return redirect(url_for('circuitos.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not nombre:
            flash('El nombre del circuito es requerido.', 'danger')
            return render_template('circuitos/nuevo.html', usuario=usuario)

        existe = db.session.execute(
            db.select(Circuito).filter_by(nombre=nombre)
        ).scalar_one_or_none()

        if existe:
            flash(f'Ya existe un circuito con el nombre "{nombre}".', 'danger')
            return render_template('circuitos/nuevo.html', usuario=usuario)

        circuito = Circuito(nombre=nombre, descripcion=descripcion or None)
        db.session.add(circuito)
        db.session.commit()

        flash(f'Circuito "{nombre}" creado correctamente.', 'success')
        return redirect(url_for('circuitos.detalle', circuito_id=circuito.id))

    return render_template('circuitos/nuevo.html', usuario=usuario)
