from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Casa, Circuito, Usuario


def seed():
    app = create_app()

    with app.app_context():
        _seed_usuario_admin()
        norte = _seed_circuitos()
        _seed_casas(norte)
        db.session.commit()
        print("Seed completado.")


def _seed_usuario_admin():
    existe = db.session.execute(
        db.select(Usuario).filter_by(username='admin')
    ).scalar_one_or_none()

    if existe:
        print("Usuario 'admin' ya existe, se omite.")
        return

    admin = Usuario(
        nombre='Administrador',
        username='admin',
        password_hash=generate_password_hash('admin123'),
        rol=Usuario.ROL_GLOBAL,
        circuito_id=None,
    )
    db.session.add(admin)
    print("Usuario 'admin' creado.")


def _seed_circuitos():
    norte = _get_or_create_circuito('Circuito Norte', 'Zona norte de la ciudad')
    _get_or_create_circuito('Circuito Sur', 'Zona sur de la ciudad')
    return norte


def _get_or_create_circuito(nombre, descripcion):
    circuito = db.session.execute(
        db.select(Circuito).filter_by(nombre=nombre)
    ).scalar_one_or_none()

    if circuito:
        print(f"Circuito '{nombre}' ya existe, se omite.")
        return circuito

    circuito = Circuito(nombre=nombre, descripcion=descripcion)
    db.session.add(circuito)
    db.session.flush()  # obtener id antes del commit final
    print(f"Circuito '{nombre}' creado.")
    return circuito


def _seed_casas(circuito_norte):
    casas_data = [
        {
            'nombre_familia': 'Familia García',
            'direccion': 'Calle Hidalgo 14, Col. Centro',
            'num_personas': 4,
        },
        {
            'nombre_familia': 'Familia Mendoza',
            'direccion': 'Av. Juárez 87, Col. Norte',
            'num_personas': 3,
        },
    ]

    for datos in casas_data:
        existe = db.session.execute(
            db.select(Casa).filter_by(
                nombre_familia=datos['nombre_familia'],
                circuito_id=circuito_norte.id,
            )
        ).scalar_one_or_none()

        if existe:
            print(f"Casa '{datos['nombre_familia']}' ya existe, se omite.")
            continue

        casa = Casa(circuito_id=circuito_norte.id, **datos)
        db.session.add(casa)
        print(f"Casa '{datos['nombre_familia']}' creada.")


if __name__ == '__main__':
    seed()
