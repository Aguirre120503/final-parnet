
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

from ..models import Sugerencia, Producto
from ..db_singleton import get_db

db = get_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def export_sugerencias_excel():
    sugerencias = Sugerencia.query.all()
    data = [{
        "Nombre": s.nombre,
        "Email": s.email,
        "Mensaje": s.mensaje,
        "Fecha": s.creado_en,
    } for s in sugerencias]
    df = pd.DataFrame(data)
    path = os.path.join(BASE_DIR, "sugerencias.xlsx")
    df.to_excel(path, index=False)
    return path


def export_sugerencias_pdf():
    sugerencias = Sugerencia.query.all()
    path = os.path.join(BASE_DIR, "sugerencias.pdf")
    c = canvas.Canvas(path, pagesize=letter)
    y = 750
    for s in sugerencias:
        linea = f"{s.creado_en} - {s.nombre or ''} - {s.email or ''}: {s.mensaje[:80]}"
        c.drawString(50, y, linea)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return path


def reporte_productos_pdf():
    """
    Genera un PDF con el listado de TODOS los productos
    que hay en la base de datos, incluyendo su estatus
    (En existencia o Agotado).
    """
    productos = Producto.query.order_by(Producto.nombre.asc()).all()

    path = os.path.join(BASE_DIR, "productos_listado.pdf")
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Listado de productos")

    c.setFont("Helvetica", 10)
    c.drawString(
        50,
        height - 70,
        f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    # Línea separadora
    c.line(50, height - 80, width - 50, height - 80)

    # Encabezados de columnas
    y = height - 110
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50,  y, "Nombre")
    c.drawString(220, y, "Tipo")
    c.drawString(360, y, "Precio")
    c.drawString(430, y, "Exist.")
    c.drawString(480, y, "Estatus")

    y -= 15
    c.line(50, y, width - 50, y)
    y -= 15

    c.setFont("Helvetica", 9)

    for p in productos:
        estatus_legible = "Agotado" if p.estatus == "agotado" else "En existencia"

        c.drawString(50,  y, (p.nombre or "")[:25])
        c.drawString(220, y, (p.tipo_producto or "N/A")[:20])

        if p.precio is not None:
            c.drawString(360, y, f"${p.precio:,.2f}")
        else:
            c.drawString(360, y, "N/A")

        c.drawString(430, y, str(p.existencia or 0))
        c.drawString(480, y, estatus_legible)

        y -= 15
        if y < 60:
            c.showPage()
            y = height - 80
            c.setFont("Helvetica", 9)

    c.showPage()
    c.save()
    return path


def export_ficha_producto_pdf(producto):
    """
    Genera un PDF con la ficha técnica de UN producto
    y regresa la ruta del archivo generado.
    Usa también el campo producto.ficha_tecnica.
    """

    # Guardamos el PDF junto a este archivo (como los otros reportes)
    filename = f"ficha_producto_{producto.id}.pdf"
    path = os.path.join(BASE_DIR, filename)

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Ficha técnica de producto")

    c.setFont("Helvetica", 10)
    c.drawString(
        50,
        height - 70,
        f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    # Línea separadora
    c.line(50, height - 80, width - 50, height - 80)

    # Datos básicos del producto
    y = height - 120

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Nombre:")
    c.setFont("Helvetica", 12)
    c.drawString(150, y, producto.nombre or "")

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Tipo:")
    c.setFont("Helvetica", 12)
    c.drawString(150, y, producto.tipo_producto or "N/A")

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Precio:")
    c.setFont("Helvetica", 12)
    if producto.precio is not None:
        c.drawString(150, y, f"${producto.precio:,.2f}")
    else:
        c.drawString(150, y, "N/A")

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Existencia:")
    c.setFont("Helvetica", 12)
    if producto.existencia is not None:
        c.drawString(150, y, str(producto.existencia))
    else:
        c.drawString(150, y, "N/A")

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Estatus:")
    c.setFont("Helvetica", 12)
    c.drawString(150, y, producto.estatus or "N/A")

    # Título de sección para ficha técnica
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Ficha técnica:")

    y -= 20
    c.setFont("Helvetica", 10)

    # Texto de ficha_tecnica (llenado manual en el admin)
    texto = getattr(producto, "ficha_tecnica", None) or "Información técnica no capturada."
    for linea in texto.splitlines():
        # Cortamos la línea si es demasiado larga (simple)
        c.drawString(60, y, linea[:100])
        y -= 14

        # Si ya no hay espacio al final de la página, salto de página
        if y < 60:
            c.showPage()
            y = height - 80
            c.setFont("Helvetica", 10)

    # Nota final opcional
    y -= 30
    if y > 40:
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(
            50,
            y,
            "Para mayor información, contactar a PARNET Ingeniería S.A. de C.V."
        )

    c.showPage()
    c.save()

    return path