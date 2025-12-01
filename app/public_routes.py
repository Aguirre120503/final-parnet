from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from .models import Producto, Noticia, Sugerencia, SolicitudServicio
from .db_singleton import get_db
from .utils.captcha import generar_captcha, validar_captcha
from .utils.reports import export_ficha_producto_pdf

db = get_db()

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    noticias = Noticia.query.filter_by(activo=True).order_by(Noticia.publicado_en.desc()).all()
    return render_template("index.html", noticias=noticias)


@public_bp.route("/productos")
def productos():
    q = request.args.get("q", "")
    query = Producto.query
    if q:
        query = query.filter(Producto.nombre.ilike(f"%{q}%"))
    productos = query.all()
    return render_template("productos.html", productos=productos, q=q)

@public_bp.route("/productos/<int:id>/ficha")
def producto_ficha_pdf(id):
    producto = Producto.query.get_or_404(id)
    path = export_ficha_producto_pdf(producto)
    return send_file(path, as_attachment=True)

@public_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        pass
    return render_template("contacto.html")


# ============================================================
#               S U G E R E N C I A S   (CAPTCHA)
# ============================================================
@public_bp.route("/sugerencias", methods=["GET", "POST"])
def sugerencias():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        mensaje = request.form.get("mensaje")
        captcha_resp = request.form.get("captcha")

        # Validar captcha
        if not validar_captcha(captcha_resp):
            flash("CAPTCHA incorrecto, intenta de nuevo.", "danger")
            return redirect(url_for("public.sugerencias"))

        # Guardar sugerencia
        sug = Sugerencia(nombre=nombre, mensaje=mensaje)
        db.session.add(sug)
        db.session.commit()

        flash("Tu sugerencia ha sido enviada correctamente.", "success")
        return redirect(url_for("public.sugerencias"))

    # GET → generar captcha nuevo
    cap = generar_captcha()
    return render_template(
        "sugerencias.html",
        captcha_texto=cap["texto"],
        captcha_id=cap["id"]
    )


# ============================================================
#               S E R V I C I O S   (CAPTCHA)
# ============================================================
@public_bp.route("/servicios", methods=["GET", "POST"])
def servicios():
    if request.method == "POST":
        nombre = request.form.get("nombre_cliente")
        email = request.form.get("email")
        area = request.form.get("area")
        tipo = request.form.get("tipo_servicio")
        detalle = request.form.get("detalle")
        captcha_resp = request.form.get("captcha")

        if not validar_captcha(captcha_resp):
            flash("❌ El CAPTCHA es incorrecto. Inténtalo de nuevo.", "danger")
            return redirect(url_for("public.servicios"))

        sol = SolicitudServicio(
            nombre_cliente=nombre,
            email=email,
            area=area,
            tipo_servicio=tipo,
            detalle=detalle
        )
        db.session.add(sol)
        db.session.commit()

        flash("✔ Tu solicitud ha sido enviada correctamente. ¡Gracias!", "success")
        return redirect(url_for("public.servicios"))

    cap = generar_captcha()
    return render_template("servicios.html", captcha_texto=cap["texto"], captcha_id=cap["id"])


@public_bp.route("/quienes")
def quienes():
    return render_template("quienes.html")


@public_bp.route("/clientes")
def clientes():
    return render_template("clientes.html")


@public_bp.route("/socios")
def socios():
    return render_template("socios.html")


@public_bp.route("/casos")
def casos():
    return render_template("casos.html")

