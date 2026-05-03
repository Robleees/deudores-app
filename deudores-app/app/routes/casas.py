from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app import db
from app.models import Casa, Circuito, Transaccion, Usuario
from app.routes.auth import login_required

casas_bp = Blueprint('casas', __name__, url_prefix='/casas')


def _get_usuario_actual():
    return db.session.get(Usuario, session['usuario_id'])


@casas_bp.route('/buscar')
@login_required
def buscar():
    usuario = _get_usuario_actual()
    q = request.args.get('q', '').strip() or None

    if q is None:
        return render_template('casas/buscar.html', resultados=[], q=None, usuario=usuario)

    patron = f'%{q}%'
    consulta = db.select(Casa).filter(
        Casa.activa == True,
        db.or_(
            Casa.nombre_familia.ilike(patron),
            Casa.direccion.ilike(patron),
        )
    )

    resultados = db.session.execute(consulta.order_by(Casa.nombre_familia)).scalars().all()
    return render_template('casas/buscar.html', resultados=resultados, q=q, usuario=usuario)


@casas_bp.route('/<int:casa_id>')
@login_required
def detalle(casa_id):
    usuario = _get_usuario_actual()

    casa = db.session.get(Casa, casa_id)
    if casa is None:
        abort(404)

    page = request.args.get('page', 1, type=int)

    paginacion = db.paginate(
        db.select(Transaccion)
        .filter_by(casa_id=casa_id)
        .order_by(Transaccion.fecha.desc()),
        page=page,
        per_page=10,
        error_out=False,
    )

    return render_template(
        'casas/detalle.html',
        casa=casa,
        paginacion=paginacion,
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


@casas_bp.route('/<int:casa_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(casa_id):
    usuario = _get_usuario_actual()

    casa = db.session.get(Casa, casa_id)
    if casa is None:
        abort(404)

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
            num_personas = casa.num_personas

        if errores:
            for msg in errores:
                flash(msg, 'danger')
            return render_template('casas/editar.html', casa=casa, usuario=usuario)

        casa.nombre_familia = nombre_familia
        casa.direccion = direccion
        casa.num_personas = num_personas
        db.session.commit()

        flash(f'Casa "{nombre_familia}" actualizada correctamente.', 'success')
        return redirect(url_for('casas.detalle', casa_id=casa_id))

    return render_template('casas/editar.html', casa=casa, usuario=usuario)


@casas_bp.route('/<int:casa_id>/desactivar', methods=['POST'])
@login_required
def desactivar(casa_id):
    usuario = _get_usuario_actual()

    if not usuario.es_global:
        flash('Solo los administradores globales pueden desactivar casas.', 'danger')
        return redirect(url_for('casas.detalle', casa_id=casa_id))

    casa = db.session.get(Casa, casa_id)
    if casa is None:
        abort(404)

    circuito_id = casa.circuito_id
    nombre = casa.nombre_familia
    casa.activa = False
    db.session.commit()

    flash(f'Casa "{nombre}" desactivada correctamente.', 'success')
    return redirect(url_for('circuitos.detalle', circuito_id=circuito_id))


@casas_bp.route('/<int:casa_id>/transaccion', methods=['POST'])
@login_required
def registrar_transaccion(casa_id):
    usuario = _get_usuario_actual()

    casa = db.session.get(Casa, casa_id)
    if casa is None:
        abort(404)

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
