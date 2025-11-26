
import random
from flask import session


def generar_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    resultado = a + b
    session["captcha_result"] = resultado
    return {
        "texto": f"{a} + {b} = ?",
        "id": "simple"
    }


def validar_captcha(respuesta):
    try:
        valor = int(respuesta)
    except (TypeError, ValueError):
        return False
    return session.get("captcha_result") == valor
