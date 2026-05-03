from flask import Blueprint, render_template, session

from app import db
from app.models import Casa, Circuito, Usuario
from app.routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def _get_usuario_actual():
    return db.session.get(Usuario, session['usuario_id'])


@dashboard_bp.route('/')
@login_required
def index():
    usuario = _get_usuario_actual()

    circuitos = db.session.execute(
        db.select(Circuito).order_by(Circuito.nombre)
    ).scalars().all()
    casas_activas = db.session.execute(
        db.select(Casa).filter_by(activa=True)
    ).scalars().all()

    saldos = {casa.id: casa.saldo_actual() for casa in casas_activas}

    total_adeudado = sum(s for s in saldos.values() if s > 0)
    total_casas = len(casas_activas)
    total_morosas = sum(1 for s in saldos.values() if s > 0)

    circuitos_con_saldo = [
        {
            'circuito': c,
            'saldo': sum(
                saldos[casa.id]
                for casa in casas_activas
                if casa.circuito_id == c.id and saldos[casa.id] > 0
            ),
        }
        for c in circuitos
    ]

    top_morosas = sorted(
        [casa for casa in casas_activas if saldos[casa.id] > 0],
        key=lambda c: saldos[c.id],
        reverse=True,
    )[:5]

    return render_template(
        'dashboard/index.html',
        usuario=usuario,
        total_adeudado=total_adeudado,
        total_casas=total_casas,
        total_morosas=total_morosas,
        circuitos_con_saldo=circuitos_con_saldo,
        top_morosas=top_morosas,
        saldos=saldos,
    )
