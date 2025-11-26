
from datetime import datetime
from flask_login import UserMixin
from .db_singleton import get_db

db = get_db()


class Rol(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    rol = db.relationship("Rol")

    def is_admin(self):
        return self.rol and self.rol.nombre == "admin"


class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    productos = db.relationship("Producto", backref="categoria", lazy=True)


class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    existencia = db.Column(db.Integer, nullable=False, default=0)
    estatus = db.Column(db.String(20), nullable=False, default="existencia")
    imagen_url = db.Column(db.String(255))
    tipo_producto = db.Column(db.String(100))
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)


class Sugerencia(db.Model):
    __tablename__ = "sugerencias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(120))
    mensaje = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)


class SolicitudServicio(db.Model):
    __tablename__ = "solicitudes_servicio"
    id = db.Column(db.Integer, primary_key=True)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    area = db.Column(db.String(100), nullable=False)
    tipo_servicio = db.Column(db.String(100))
    detalle = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)


class Noticia(db.Model):
    __tablename__ = "noticias"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    publicado_en = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)


class Visita(db.Model):
    __tablename__ = "visitas"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    contador = db.Column(db.Integer, nullable=False, default=0)
