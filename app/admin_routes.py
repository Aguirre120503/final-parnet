
from flask import Blueprint, render_template, request, redirect, url_for, send_file
from flask_login import login_required
from .auth import admin_required
from .models import Producto, Sugerencia, SolicitudServicio
from .db_singleton import get_db
from .utils.reports import export_sugerencias_excel, export_sugerencias_pdf, reporte_productos_pdf
from .utils.dashboard import datos_servicios, datos_productos

db = get_db()

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    data_servicios = datos_servicios()
    data_productos = datos_productos()
    return render_template("admin/dashboard.html",
                           data_servicios=data_servicios,
                           data_productos=data_productos)


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
    precio = request.form.get("precio", 0)
    existencia = request.form.get("existencia", 0)
    estatus = request.form.get("estatus", "existencia")
    tipo_producto = request.form.get("tipo_producto")

    producto = Producto(
        nombre=nombre,
        precio=precio,
        existencia=existencia,
        estatus=estatus,
        tipo_producto=tipo_producto,
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
        producto.precio = request.form.get("precio", 0)
        producto.existencia = request.form.get("existencia", 0)
        producto.estatus = request.form.get("estatus", "existencia")
        producto.tipo_producto = request.form.get("tipo_producto")
        db.session.commit()

        return redirect(url_for("admin.productos_list"))

    return render_template("admin/producto_editar.html", producto=producto)