
from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os

from .auth import admin_required
from .models import Producto, Sugerencia, SolicitudServicio, Usuario, Rol, Contacto
from .db_singleton import get_db
from .utils.reports import export_sugerencias_excel, export_sugerencias_pdf, reporte_productos_pdf
from .utils.dashboard import datos_servicios, datos_productos

db = get_db()
admin_bp = Blueprint("admin",  __name__, url_prefix="/admin")

# Carpeta donde se guardarán las imágenes de productos
UPLOAD_FOLDER = os.path.join("app", "static", "img", "productos")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    data_servicios = datos_servicios()
    data_productos = datos_productos()
    return render_template(
        "admin/dashboard.html",
        data_servicios=data_servicios,
        data_productos=data_productos
    )


@admin_bp.route("/productos")
@login_required
@admin_required
def productos_list():
    productos = Producto.query.all()
    return render_template("admin/productos_crud.html", productos=productos)


@admin_bp.route("/productos/nuevo", methods=["POST"])
@login_required
@admin_required
def productos_nuevo():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio", type=float, default=0)
    existencia = request.form.get("existencia", type=int, default=0)
    estatus = request.form.get("estatus", "existencia")
    tipo_producto = request.form.get("tipo_producto")
    ficha_tecnica = request.form.get("ficha_tecnica") 

    # archivo de imagen
    imagen_file = request.files.get("imagen")
    imagen_url = None

    if imagen_file and imagen_file.filename:
        filename = secure_filename(imagen_file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        imagen_file.save(save_path)
        # ruta relativa dentro de /static
        imagen_url = f"img/productos/{filename}"

    producto = Producto(
        nombre=nombre,
        precio=precio,
        existencia=existencia,
        estatus=estatus,
        tipo_producto=tipo_producto,
        imagen_url=imagen_url
    )
    db.session.add(producto)
    db.session.commit()
    return redirect(url_for("admin.productos_list"))


@admin_bp.route("/productos/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def productos_eliminar(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("admin.productos_list"))


@admin_bp.route("/sugerencias")
@login_required
@admin_required
def sugerencias_list():
    page = request.args.get("page", 1, type=int)
    pag = Sugerencia.query.order_by(Sugerencia.creado_en.desc()).paginate(page=page, per_page=10)
    # 🔴 AQUÍ ESTABA EL ERROR, ANTES USABAS url_for
    return render_template("admin/sugerencias_list.html", pag=pag)


@admin_bp.route("/sugerencias/export/excel")
@login_required
@admin_required
def sugerencias_export_excel():
    path = export_sugerencias_excel()
    return send_file(path, as_attachment=True)


@admin_bp.route("/sugerencias/export/pdf")
@login_required
@admin_required
def sugerencias_export_pdf():
    path = export_sugerencias_pdf()
    return send_file(path, as_attachment=True)


@admin_bp.route("/productos/reporte/pdf")
@login_required
@admin_required
def productos_reporte_pdf():
    path = reporte_productos_pdf()
    return send_file(path, as_attachment=True)


@admin_bp.route("/productos/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def productos_editar(id):
    producto = Producto.query.get_or_404(id)

    if request.method == "POST":
        producto.nombre = request.form.get("nombre")
        producto.precio = request.form.get("precio", type=float, default=0)
        producto.existencia = request.form.get("existencia", type=int, default=0)
        producto.estatus = request.form.get("estatus", "existencia")
        producto.tipo_producto = request.form.get("tipo_producto")

        # si el admin sube una nueva imagen, la actualizamos
        imagen_file = request.files.get("imagen")
        if imagen_file and imagen_file.filename:
            filename = secure_filename(imagen_file.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            imagen_file.save(save_path)
            producto.imagen_url = f"img/productos/{filename}"

        db.session.commit()
        return redirect(url_for("admin.productos_list"))

    return render_template("admin/producto_editar.html", producto=producto)


# ==============================
#  NUEVO ADMINISTRADOR
# ==============================
@admin_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def usuarios_nuevo():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # VALIDAR username único
        if Usuario.query.filter_by(username=username).first():
            flash("Ese nombre de usuario ya existe", "danger")
            return redirect(url_for("admin.usuarios_nuevo"))

        # VALIDAR email único
        if Usuario.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado", "danger")
            return redirect(url_for("admin.usuarios_nuevo"))

        # Buscar o crear rol admin
        rol_admin = Rol.query.filter_by(nombre="admin").first()
        if not rol_admin:
            rol_admin = Rol(nombre="admin")
            db.session.add(rol_admin)
            db.session.commit()

        nuevo = Usuario(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            rol_id=rol_admin.id,
            is_admin="true"
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("Administrador agregado correctamente", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/usuario_nuevo.html")


@admin_bp.route("/contacto")
@login_required
@admin_required
def contacto_list():
    page = request.args.get("page", 1, type=int)
    pag = Contacto.query.order_by(Contacto.creado_en.desc()).paginate(page=page, per_page=10)
    return render_template("admin/contacto_list.html", pag=pag)


@admin_bp.route("/contacto/<int:id>/toggle", methods=["POST"])
@login_required
@admin_required
def contacto_toggle(id):
    contacto = Contacto.query.get_or_404(id)

    # alternar entre pendiente y leído
    if contacto.estado == "leído":
        contacto.estado = "pendiente"
    else:
        contacto.estado = "leído"

    db.session.commit()
    return redirect(url_for("admin.contacto_list"))

@admin_bp.route("/noticias")
@login_required
@admin_required
def noticias_list():
    noticias = Noticia.query.order_by(Noticia.creado_en.desc()).all()
    return render_template("admin/noticias_list.html", noticias=noticias)

@admin_bp.route("/noticias/nueva", methods=["POST"])
@login_required
@admin_required
def noticias_nueva():
    titulo = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    imagen = request.files.get("imagen")

    imagen_url = None
    if imagen and imagen.filename:
        filename = secure_filename(imagen.filename)
        save_path = os.path.join("app", "static", "img", "noticias", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        imagen.save(save_path)
        imagen_url = f"img/noticias/{filename}"

    noticia = Noticia(
        titulo=titulo,
        descripcion=descripcion,
        imagen_url=imagen_url
    )

    db.session.add(noticia)
    db.session.commit()

    return redirect(url_for("admin.noticias_list"))