"""
Prueba de integración end-to-end del módulo de calificaciones.

Recorre el flujo completo contra el backend REAL levantado en Docker, hablando
por HTTP (urllib de la stdlib, sin dependencias extra) y verificando de paso
contra la base de datos:

    Admin  -> crea grado, materia, periodo (Abierto), curso y matrícula.
    Docente-> ve su curso con los anidados (BE-2), crea sección y actividad,
              registra una nota y hace carga masiva (upsert).
    Estudiante -> consulta solo sus propias notas y matrículas (RN-04).

Además comprueba, extremo a extremo, las reglas:
    RN-03: un docente ajeno recibe 403 al crear una sección en un curso ajeno.
    RN-d : con el periodo 'Cerrado' no se pueden registrar notas (400).

Requisitos para correrla:
    - Stack de Docker arriba (backend + db) sembrado con los usuarios de
      app/tests/creacion_usuarios.py.
    - El backend accesible por HTTP. Por defecto http://localhost:8000; se puede
      cambiar con la variable de entorno CALIF_BASE_URL (p. ej. para apuntar al
      contenedor). Si el backend no responde, la prueba se salta.
    - Ejecutar con:  python -m unittest app.tests.test_calificaciones_integracion

La prueba crea sus propios datos y los borra en tearDownClass, así que es
repetible y no deja basura en la base.
"""

import json
import os
import random
import unittest
import urllib.error
import urllib.request

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal

BASE_URL = os.environ.get("CALIF_BASE_URL", "http://localhost:8000").rstrip("/")

# Credenciales sembradas por app/tests/creacion_usuarios.py
ADMIN = ("samuel.herrera@colegio.edu.co", "Admin123!")
DOCENTE = ("carlos.rodriguez@colegio.edu.co", "Docente123!")
OTRO_DOCENTE = ("juan.martinez@colegio.edu.co", "Docente123!")
ESTUDIANTE = ("david.ramirez@colegio.edu.co", "Estudiante123!")


def _peticion(metodo, ruta, cuerpo=None, token=None):
    """Devuelve (status, json|None). No lanza ante 4xx: los códigos se afirman en el test."""
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(f"{BASE_URL}{ruta}", data=datos, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as err:
        cuerpo_error = err.read()
        try:
            return err.code, json.loads(cuerpo_error or "null")
        except json.JSONDecodeError:
            return err.code, None


def _backend_disponible() -> bool:
    # Solo comprueba conectividad: cualquier respuesta HTTP (incluido un 404)
    # significa que el backend está arriba. Falla únicamente si no hay servidor.
    try:
        urllib.request.urlopen(f"{BASE_URL}/docs", timeout=10)
        return True
    except urllib.error.HTTPError:
        return True
    except (urllib.error.URLError, OSError):
        return False


@unittest.skipUnless(_backend_disponible(), f"Requiere el backend accesible en {BASE_URL} (docker-compose up)")
class FlujoCalificacionesIntegracionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token_admin = cls._login(*ADMIN)["access_token"]
        docente = cls._login(*DOCENTE)
        cls.token_docente = docente["access_token"]
        cls.id_docente = docente["id_usuario"]
        estudiante = cls._login(*ESTUDIANTE)
        cls.token_estudiante = estudiante["access_token"]
        cls.id_estudiante = estudiante["id_usuario"]

        # La matrícula es única por (estudiante, año) y el validador del backend
        # exige año <= 2100. Elegimos uno alto y libre para este estudiante, así la
        # prueba es repetible aunque quedara basura de una corrida interrumpida.
        cls.anio = cls._anio_libre(cls.id_estudiante)
        sufijo = cls.anio

        # --- Admin arma el escenario ---
        cls.id_grado = cls._crear("/api/grados", cls.token_admin, {"nombre": f"G{sufijo % 100000}"})["id_grado"]
        cls.id_materia = cls._crear("/api/materias", cls.token_admin, {"nombre": f"Mat-{sufijo}"})["id_materia"]

        cls.id_periodo_abierto = cls._crear(
            "/api/periodos", cls.token_admin,
            {"nombre": "Periodo IT", "anio": cls.anio, "estado": "Abierto"},
        )["id_periodo"]
        cls.id_periodo_cerrado = cls._crear(
            "/api/periodos", cls.token_admin,
            {"nombre": "Periodo IT", "anio": cls.anio, "estado": "Cerrado"},
        )["id_periodo"]

        cls.id_curso = cls._crear(
            "/api/cursos", cls.token_admin,
            {"id_docente": cls.id_docente, "id_grado": cls.id_grado,
             "id_materia": cls.id_materia, "id_periodo": cls.id_periodo_abierto},
        )["id_curso"]
        cls.id_curso_cerrado = cls._crear(
            "/api/cursos", cls.token_admin,
            {"id_docente": cls.id_docente, "id_grado": cls.id_grado,
             "id_materia": cls.id_materia, "id_periodo": cls.id_periodo_cerrado},
        )["id_curso"]

        cls.id_matricula = cls._crear(
            "/api/matriculas", cls.token_admin,
            {"id_estudiante": cls.id_estudiante, "id_grado": cls.id_grado, "anio": cls.anio},
        )["id_matricula"]

    @classmethod
    def tearDownClass(cls):
        # Borra lo creado respetando las FKs (notas -> actividades -> secciones -> cursos ...).
        cursos = [getattr(cls, "id_curso", None), getattr(cls, "id_curso_cerrado", None)]
        cursos = [c for c in cursos if c is not None]
        if not cursos:
            return
        try:
            with SessionLocal() as session:
                session.execute(text(
                    "DELETE FROM nota WHERE id_actividad IN "
                    "(SELECT a.id_actividad FROM actividadevaluativa a "
                    " JOIN seccionporcentaje s ON s.id_seccion = a.id_seccion "
                    " WHERE s.id_curso = ANY(:cursos))"
                ), {"cursos": cursos})
                session.execute(text(
                    "DELETE FROM actividadevaluativa WHERE id_seccion IN "
                    "(SELECT id_seccion FROM seccionporcentaje WHERE id_curso = ANY(:cursos))"
                ), {"cursos": cursos})
                session.execute(text("DELETE FROM seccionporcentaje WHERE id_curso = ANY(:cursos)"),
                                {"cursos": cursos})
                session.execute(text("DELETE FROM curso WHERE id_curso = ANY(:cursos)"), {"cursos": cursos})
                if getattr(cls, "id_matricula", None) is not None:
                    session.execute(text("DELETE FROM matricula WHERE id_matricula = :m"), {"m": cls.id_matricula})
                periodos = [p for p in (getattr(cls, "id_periodo_abierto", None),
                                        getattr(cls, "id_periodo_cerrado", None)) if p is not None]
                if periodos:
                    session.execute(text("DELETE FROM periodoacademico WHERE id_periodo = ANY(:p)"), {"p": periodos})
                if getattr(cls, "id_materia", None) is not None:
                    session.execute(text("DELETE FROM materia WHERE id_materia = :m"), {"m": cls.id_materia})
                if getattr(cls, "id_grado", None) is not None:
                    session.execute(text("DELETE FROM grado WHERE id_grado = :g"), {"g": cls.id_grado})
                session.commit()
        except SQLAlchemyError as err:
            # No enmascarar un fallo del test con un fallo de limpieza; solo avisar.
            print(f"[integracion] no se pudo limpiar los datos de prueba: {err}")

    # --- helpers ---

    @classmethod
    def _anio_libre(cls, id_estudiante):
        with SessionLocal() as session:
            usados = set(session.execute(
                text("SELECT anio FROM matricula WHERE id_estudiante = :e"), {"e": id_estudiante}
            ).scalars().all())
        candidatos = [a for a in range(2100, 2050, -1) if a not in usados]
        if not candidatos:
            raise unittest.SkipTest("No hay un año libre <= 2100 para el estudiante de prueba")
        return random.choice(candidatos)

    @classmethod
    def _login(cls, correo, password):
        status, cuerpo = _peticion("POST", "/api/auth/login", {"correo": correo, "password": password})
        assert status == 200, f"login {correo}: {status} {cuerpo}"
        return cuerpo

    @classmethod
    def _crear(cls, ruta, token, payload):
        status, cuerpo = _peticion("POST", ruta, payload, token=token)
        assert status == 200, f"POST {ruta}: {status} {cuerpo}"
        return cuerpo

    # --- casos (el prefijo numérico fija el orden de ejecución) ---

    def test_01_docente_ve_su_curso_con_anidados(self):
        """BE-2: /api/cursos entrega materia/grado/periodo anidados y el estado del periodo."""
        status, cursos = _peticion("GET", f"/api/cursos?id_docente={self.id_docente}", token=self.token_docente)
        self.assertEqual(status, 200)
        curso = next(c for c in cursos if c["id_curso"] == self.id_curso)

        self.assertIsNotNone(curso["materia"])
        self.assertEqual(curso["materia"]["id_materia"], self.id_materia)
        self.assertIsNotNone(curso["grado"])
        self.assertEqual(curso["periodo"]["estado"], "Abierto")
        self.assertEqual(curso["periodo"]["anio"], self.anio)

    def test_02_docente_crea_seccion_actividad_y_nota(self):
        """Flujo feliz: sección -> actividad -> nota, todo del docente dueño del curso."""
        seccion = self._crear(
            "/api/secciones", self.token_docente,
            {"nombre_seccion": "Talleres", "porcentaje": 40, "id_curso": self.id_curso},
        )
        type(self).id_seccion = seccion["id_seccion"]

        actividad = self._crear(
            "/api/actividades", self.token_docente,
            {"nombre": "Taller 1", "fecha": "2026-03-15", "id_seccion": self.id_seccion},
        )
        type(self).id_actividad = actividad["id_actividad"]

        nota = self._crear(
            "/api/notas", self.token_docente,
            {"id_actividad": self.id_actividad, "id_estudiante": self.id_estudiante,
             "calificacion": 4.5, "comentario": "Buen trabajo"},
        )
        self.assertEqual(nota["calificacion"], 4.5)
        self.assertEqual(nota["id_estudiante"], self.id_estudiante)

    def test_03_estudiante_solo_ve_sus_notas(self):
        """RN-04: el estudiante consulta la actividad y ve únicamente su propia nota."""
        status, notas = _peticion("GET", f"/api/notas?id_actividad={self.id_actividad}", token=self.token_estudiante)
        self.assertEqual(status, 200)
        self.assertTrue(notas, "el estudiante debería ver su nota")
        self.assertTrue(all(n["id_estudiante"] == self.id_estudiante for n in notas))

    def test_04_estudiante_solo_ve_sus_matriculas(self):
        """RN-04: /api/matriculas ignora cualquier filtro y devuelve las del propio estudiante."""
        status, matriculas = _peticion("GET", "/api/matriculas?id_estudiante=999999", token=self.token_estudiante)
        self.assertEqual(status, 200)
        self.assertTrue(all(m["id_estudiante"] == self.id_estudiante for m in matriculas))

    def test_05_carga_masiva_actualiza_la_nota(self):
        """La carga masiva hace upsert: reescribe la nota del estudiante sin duplicarla."""
        status, resultado = _peticion(
            "POST", "/api/notas/carga-masiva",
            {"id_actividad": self.id_actividad,
             "notas": [{"id_estudiante": self.id_estudiante, "calificacion": 3.0, "comentario": "Recalificado"}]},
            token=self.token_docente,
        )
        self.assertEqual(status, 200, resultado)
        self.assertEqual(resultado[0]["calificacion"], 3.0)

        _, verificacion = _peticion("GET", f"/api/notas?id_actividad={self.id_actividad}", token=self.token_docente)
        mias = [n for n in verificacion if n["id_estudiante"] == self.id_estudiante]
        self.assertEqual(len(mias), 1, "el upsert no debe duplicar la nota")
        self.assertEqual(mias[0]["calificacion"], 3.0)

    def test_06_docente_ajeno_no_puede_calificar_curso_de_otro(self):
        """RN-03: otro docente recibe 403 al crear una sección en un curso que no dicta."""
        token_otro = self._login(*OTRO_DOCENTE)["access_token"]
        status, _ = _peticion(
            "POST", "/api/secciones",
            {"nombre_seccion": "Intruso", "porcentaje": 10, "id_curso": self.id_curso},
            token=token_otro,
        )
        self.assertEqual(status, 403)

    def test_07_periodo_cerrado_bloquea_notas(self):
        """RN-d: con el periodo del curso 'Cerrado' no se pueden registrar notas (400)."""
        seccion = self._crear(
            "/api/secciones", self.token_docente,
            {"nombre_seccion": "Cerrada", "porcentaje": 50, "id_curso": self.id_curso_cerrado},
        )
        actividad = self._crear(
            "/api/actividades", self.token_docente,
            {"nombre": "Fuera de plazo", "fecha": "2026-03-20", "id_seccion": seccion["id_seccion"]},
        )
        status, _ = _peticion(
            "POST", "/api/notas",
            {"id_actividad": actividad["id_actividad"], "id_estudiante": self.id_estudiante, "calificacion": 4.0},
            token=self.token_docente,
        )
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
