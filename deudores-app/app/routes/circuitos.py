from flask import Blueprint

circuitos_bp = Blueprint('circuitos', __name__, url_prefix='/circuitos')


@circuitos_bp.route('/ping')
def ping():
    return 'OK'
