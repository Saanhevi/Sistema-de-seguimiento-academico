"""Normalización de las claves con las que se identifica a una persona.

Vive aquí, y no dentro del parser de Excel o del servicio de auth, porque las
dos puntas tienen que coincidir exactamente: si el registro guarda
"1.023.456.789" y la importación busca "1023456789", el emparejamiento no falla
con un error — simplemente no encuentra a nadie, en silencio (RN-r).

Módulo puro: sin SQLAlchemy y sin FastAPI, para que lo pueda importar tanto el
parser (que no toca la base de datos) como los servicios.
"""

import re

# Separadores con los que la gente escribe un documento: "1.023.456.789",
# "1 023 456 789", "12345678-9". Ninguno forma parte del número.
_SEPARADORES_DOCUMENTO = re.compile(r"[\s.\-]")

# "1,02E+09" / "1.02e9": Excel ya truncó los dígitos que faltan, así que el
# número original no se puede reconstruir sin inventárselo (RN-s).
_NOTACION_CIENTIFICA = re.compile(r"^[+-]?\d+([.,]\d+)?[eE][+-]?\d+$")


def normalizar_documento(valor: str | None) -> str | None:
    """Quita espacios, puntos y guiones. Devuelve None si no queda nada."""
    if valor is None:
        return None
    limpio = _SEPARADORES_DOCUMENTO.sub("", str(valor)).strip()
    return limpio or None


def es_notacion_cientifica(valor: str | None) -> bool:
    """True si el texto es un número en notación científica (RN-s)."""
    if valor is None:
        return False
    return bool(_NOTACION_CIENTIFICA.match(str(valor).strip()))


def normalizar_correo(valor: str | None) -> str | None:
    """strip() + minúsculas.

    Usuario.correo es UNIQUE, pero Postgres compara sensible a mayúsculas y el
    docente escribe el correo como se le ocurre (RN-t).
    """
    if valor is None:
        return None
    limpio = str(valor).strip().lower()
    return limpio or None
