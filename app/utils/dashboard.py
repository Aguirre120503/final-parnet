
from ..models import SolicitudServicio, Producto
from ..db_singleton import get_db

db = get_db()


def datos_servicios():
    rows = db.session.query(
        SolicitudServicio.tipo_servicio,
        db.func.count(SolicitudServicio.id)
    ).group_by(SolicitudServicio.tipo_servicio).all()
    labels = [r[0] or "Sin tipo" for r in rows]
    values = [r[1] for r in rows]
    return {"labels": labels, "values": values}


def datos_productos():
    rows = db.session.query(
        Producto.tipo_producto,
        db.func.count(Producto.id)
    ).group_by(Producto.tipo_producto).all()
    labels = [r[0] or "Sin tipo" for r in rows]
    values = [r[1] for r in rows]
    return {"labels": labels, "values": values}
