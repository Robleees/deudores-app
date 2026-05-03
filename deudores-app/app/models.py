from datetime import datetime, timezone
from app import db


class Circuito(db.Model):
    __tablename__ = 'circuitos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    usuarios = db.relationship('Usuario', backref='circuito', lazy='dynamic')
    casas = db.relationship('Casa', backref='circuito', lazy='dynamic')

    def __repr__(self):
        return f'<Circuito {self.nombre}>'


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    ROL_GLOBAL = 'admin_global'
    ROL_LOCAL = 'admin_local'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default=ROL_LOCAL)
    circuito_id = db.Column(db.Integer, db.ForeignKey('circuitos.id'), nullable=True)

    transacciones = db.relationship('Transaccion', backref='usuario', lazy='dynamic')

    @property
    def es_global(self):
        return self.rol == self.ROL_GLOBAL

    def __repr__(self):
        return f'<Usuario {self.username} ({self.rol})>'


class Casa(db.Model):
    __tablename__ = 'casas'

    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(255), nullable=False)
    nombre_familia = db.Column(db.String(150), nullable=False)
    num_personas = db.Column(db.Integer, default=1)
    circuito_id = db.Column(db.Integer, db.ForeignKey('circuitos.id'), nullable=False)
    activa = db.Column(db.Boolean, default=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    transacciones = db.relationship('Transaccion', backref='casa', lazy='dynamic')

    def saldo_actual(self):
        cargos = db.session.query(
            db.func.coalesce(db.func.sum(Transaccion.monto), 0)
        ).filter_by(casa_id=self.id, tipo='cargo').scalar()

        abonos = db.session.query(
            db.func.coalesce(db.func.sum(Transaccion.monto), 0)
        ).filter_by(casa_id=self.id, tipo='abono').scalar()

        return float(cargos) - float(abonos)

    def __repr__(self):
        return f'<Casa {self.nombre_familia} - {self.direccion}>'


class Transaccion(db.Model):
    __tablename__ = 'transacciones'

    TIPO_CARGO = 'cargo'
    TIPO_ABONO = 'abono'

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey('casas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Transaccion {self.tipo} ${self.monto} casa_id={self.casa_id}>'
