from flask import Blueprint

casas_bp = Blueprint('casas', __name__, url_prefix='/casas')


@casas_bp.route('/ping')
def ping():
    return 'OK'
