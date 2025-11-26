
from flask import Blueprint, render_template, request
from .models import Producto, Noticia, Sugerencia, SolicitudServicio
from .db_singleton import get_db
from .utils.captcha import generar_captcha, validar_captcha

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


@public_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    # Aquí puedes implementar el envío de correo si lo deseas
    if request.method == "POST":
        # procesar datos del formulario
        pass
    return render_template("contacto.html")


@public_bp.route("/sugerencias", methods=["GET", "POST"])
def sugerencias():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        mensaje = request.form.get("mensaje")
        captcha_resp = request.form.get("captcha")

        if not validar_captcha(captcha_resp):
            return "Captcha incorrecto", 400

        sug = Sugerencia(nombre=nombre, email=email, mensaje=mensaje)
        db.session.add(sug)
        db.session.commit()
        return "OK"

    cap = generar_captcha()
    return render_template("sugerencias.html", captcha_texto=cap["texto"], captcha_id=cap["id"])


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
            return "Captcha incorrecto", 400

        sol = SolicitudServicio(
            nombre_cliente=nombre,
            email=email,
            area=area,
            tipo_servicio=tipo,
            detalle=detalle
        )
        db.session.add(sol)
        db.session.commit()
        return "OK"

    cap = generar_captcha()
    return render_template("servicios.html", captcha_texto=cap["texto"], captcha_id=cap["id"])
