
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
    productos = Producto.query.all()
    path = os.path.join(BASE_DIR, "productos_reporte.pdf")
    c = canvas.Canvas(path, pagesize=letter)
    y = 750
    for p in productos:
        linea = f"{p.nombre} | {p.estatus} | existencia: {p.existencia}"
        c.drawString(50, y, linea)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return path
