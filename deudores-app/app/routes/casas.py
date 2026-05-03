from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app import db
from app.models import Casa, Circuito, Transaccion, Usuario
from app.routes.auth import login_required

casas_bp = Blueprint('casas', __name__, url_prefix='/casas')


def _get_usuario_actual():
    return db.session.get(Usuario, session['usuario_id'])


def _verificar_acceso_circuito(usuario, circuito_id):
    """Aborta con 403 si el admin_local intenta operar fuera de su circuito."""
    if not usuario.es_global and usuario.circuito_id != circuito_id:
        abort(403)


@casas_bp.route('/<int:casa_id>')
@login_required
def detalle(casa_id):
    usuario = _get_usuario_actual()

    casa = db.session.get(Casa, casa_id)
    if casa is None:
        abort(404)

    _verificar_acceso_circuito(usuario, casa.circuito_id)

    transacciones = (
        db.session.execute(
            db.select(Transaccion)
            .filter_by(casa_id=casa_id)
            .order_by(Transaccion.fecha.desc())
        )
        .scalars()
        .all()
    )

    return render_template(
        'casas/detalle.html',
        casa=casa,
        transacciones=transacciones,
        saldo=casa.saldo_actual(),
        usuario=usuario,
    )


@casas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    usuario = _get_usuario_actual()

    circuito_id = request.args.get('circuito_id', type=int)
    if circuito_id is None:
        flash('Debes especificar un circuito para crear una casa.', 'danger')
        return redirect(url_for('circuitos.index'))

    circuito = db.session.get(Circuito, circuito_id)
    if circuito is None:
        abort(404)

    _verificar_acceso_circuito(usuario, circuito_id)

    if request.method == 'POST':
        nombre_familia = request.form.get('nombre_familia', '').strip()
        direccion = request.form.get('direccion', '').strip()
        num_personas_raw = request.form.get('num_personas', '1').strip()

        errores = []
        if not nombre_familia:
            errores.append('El nombre de la familia es requerido.')
        if not direccion:
            errores.append('La dirección es requerida.')

        try:
            num_personas = int(num_personas_raw)
            if num_personas < 1:
                raise ValueError
        except ValueError:
            errores.append('El número de personas debe ser un entero positivo.')
            num_personas = 1

        if errores:
            for msg in errores:
                flash(msg, 'danger')
            return render_template(
                'casas/nueva.html',
                circuito=circuito,
                usuario=usuario,
                form=request.form,
            )

        casa = Casa(
            nombre_familia=nombre_familia,
            direccion=direccion,
            num_personas=num_personas,
            circuito_id=circuito_id,
        )
        db.session.add(casa)
        db.session.commit()

        flash(f'Casa "{nombre_familia}" registrada correctamente.', 'success')
        return redirect(url_for('casas.detalle', casa_id=casa.id))

    return render_template('casas/nueva.html', circuito=circuito, usuario=usuario, form={})


@casas_bp.route('/<int:casa_id>/transaccion', methods=['POST'])
@login_required
def registrar_transaccion(casa_id):
    usuario = _get_usuario_actual()

    casa = db.session.get(Casa, casa_id)
    if casa is None:
        abort(404)

    _verificar_acceso_circuito(usuario, casa.circuito_id)

    tipo = request.form.get('tipo', '').strip()
    monto_raw = request.form.get('monto', '').strip()
    descripcion = request.form.get('descripcion', '').strip() or None

    if tipo not in (Transaccion.TIPO_CARGO, Transaccion.TIPO_ABONO):
        flash('El tipo de transacción debe ser "cargo" o "abono".', 'danger')
        return redirect(url_for('casas.detalle', casa_id=casa_id))

    try:
        monto = Decimal(monto_raw)
        if monto <= 0:
            raise InvalidOperation
    except InvalidOperation:
        flash('El monto debe ser un número positivo.', 'danger')
        return redirect(url_for('casas.detalle', casa_id=casa_id))

    transaccion = Transaccion(
        casa_id=casa_id,
        usuario_id=usuario.id,
        tipo=tipo,
        monto=monto,
        descripcion=descripcion,
    )
    db.session.add(transaccion)
    db.session.commit()

    tipo_label = 'Cargo' if tipo == Transaccion.TIPO_CARGO else 'Abono'
    flash(f'{tipo_label} de ${monto:,.2f} registrado correctamente.', 'success')
    return redirect(url_for('casas.detalle', casa_id=casa_id))
