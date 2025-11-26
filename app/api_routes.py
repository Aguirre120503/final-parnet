
from flask import Blueprint, jsonify
from .models import Producto

api_bp = Blueprint("api", __name__)


@api_bp.route("/productos/<int:producto_id>", methods=["GET"])
def producto_detalle(producto_id):
    p = Producto.query.get_or_404(producto_id)
    return jsonify({
        "id": p.id,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "precio": float(p.precio),
        "existencia": p.existencia,
        "estatus": p.estatus,
        "tipo_producto": p.tipo_producto,
        "imagen_url": p.imagen_url,
    })
