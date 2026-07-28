"""
Pruebas del cálculo de promedios en NotaRepository (HU8 y HU9).

La fórmula vive en el repositorio, no en el servicio: `CalificacionService` solo
delega, así que probar el servicio no verificaría ninguna operación aritmética.

  - H10: el promedio pondera por el porcentaje de cada sección, no es una media
         aritmética de todas las notas sueltas.
  - H10 (HU9): el promedio grupal promedia los promedios de cada estudiante, para
         que quien tiene 10 actividades no pese más que quien tiene 2.
  - H13: la ausencia de notas devuelve None, nunca 0.0.
  - H7:  el filtro por docente se omite para el Administrador (RN-03 sigue
         aplicando al Docente).

Todo con dobles de prueba; no se toca la base de datos.
"""

import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from app.repositories.nota import NotaRepository


class SesionFalsa:
    """
    Imita el encadenamiento de SQLAlchemy `query(...).join(...).filter(...).all()`.

    Cada eslabón devuelve la misma instancia, así que el repositorio recorre su
    cadena real y al final recibe las filas que le pasamos. `filtros_aplicados`
    permite comprobar si se añadió el filtro opcional por docente.
    """

    def __init__(self, filas):
        self._filas = filas
        self.filtros_aplicados = 0

    def query(self, *args, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        self.filtros_aplicados += 1
        return self

    def all(self):
        return self._filas


def _repo(filas):
    sesion = SesionFalsa(filas)
    return NotaRepository(sesion), sesion


# Secciones de ejemplo: un examen que pesa 60% y unos talleres que pesan 40%.
EXAMEN, TALLERES = 1, 2


class PromedioEstudianteTests(unittest.TestCase):
    """Filas de la consulta: (calificacion, id_seccion, porcentaje)."""

    def test_caso_documentado_h10(self):
        # Examen (60%) = 2.0 y Talleres (40%) = cuatro 5.0.
        # Ponderado: (2.0*60 + 5.0*40) / 100 = 3.2
        # La media aritmética que devolvía el código anterior daba 4.4.
        filas = [
            (2.0, EXAMEN, 60),
            (5.0, TALLERES, 40),
            (5.0, TALLERES, 40),
            (5.0, TALLERES, 40),
            (5.0, TALLERES, 40),
        ]
        repo, _ = _repo(filas)

        promedio = repo.obtener_promedio_estudiante_materia(1, 1, 1)

        self.assertEqual(promedio, 3.2)
        self.assertNotEqual(promedio, 4.4)

    def test_el_numero_de_actividades_no_altera_el_peso_de_la_seccion(self):
        # Misma nota por sección que el caso anterior, pero con una sola actividad
        # en Talleres: el peso lo pone el porcentaje, no cuántas notas hay.
        filas = [(2.0, EXAMEN, 60), (5.0, TALLERES, 40)]
        repo, _ = _repo(filas)

        self.assertEqual(repo.obtener_promedio_estudiante_materia(1, 1, 1), 3.2)

    def test_actividades_de_una_seccion_se_promedian_entre_si(self):
        # Talleres (40%) tiene 4.0 y 2.0 -> 3.0 antes de ponderar.
        # (5.0*60 + 3.0*40) / 100 = 4.2
        filas = [(5.0, EXAMEN, 60), (4.0, TALLERES, 40), (2.0, TALLERES, 40)]
        repo, _ = _repo(filas)

        self.assertEqual(repo.obtener_promedio_estudiante_materia(1, 1, 1), 4.2)

    def test_sin_notas_devuelve_none_y_no_cero(self):
        # H13: 0.0 es una nota válida; "sin datos" tiene que ser None.
        repo, _ = _repo([])

        promedio = repo.obtener_promedio_estudiante_materia(1, 1, 1)

        self.assertIsNone(promedio)
        self.assertNotEqual(promedio, 0.0)

    def test_promedio_parcial_se_normaliza_sobre_las_secciones_calificadas(self):
        """
        Documenta el comportamiento actual, que sigue en discusión.

        Con solo la sección de 40% calificada, el resultado se normaliza sobre ese
        40% y un 5.0 se reporta como promedio 5.0 de la materia completa, sin
        indicar que el corte está incompleto. Si se decide dividir sobre el peso
        total del curso (100%), este test debe cambiar a 2.0.
        """
        repo, _ = _repo([(5.0, TALLERES, 40)])

        self.assertEqual(repo.obtener_promedio_estudiante_materia(1, 1, 1), 5.0)


class PromedioGrupalTests(unittest.TestCase):
    """Filas de la consulta: (id_estudiante, calificacion, id_seccion, porcentaje)."""

    def test_promedia_promedios_no_notas_sueltas(self):
        # Estudiante 1: cinco notas de 5.0 -> promedio 5.0
        # Estudiante 2: dos notas de 1.0   -> promedio 1.0
        # Grupal correcto: (5.0 + 1.0) / 2 = 3.0
        # Promediando las 7 filas en bruto saldría 3.86, dominado por quien tiene
        # más actividades; eso es lo que H10 señalaba en HU9.
        filas = [
            (1, 5.0, EXAMEN, 60),
            (1, 5.0, TALLERES, 40),
            (1, 5.0, TALLERES, 40),
            (1, 5.0, TALLERES, 40),
            (1, 5.0, TALLERES, 40),
            (2, 1.0, EXAMEN, 60),
            (2, 1.0, TALLERES, 40),
        ]
        repo, _ = _repo(filas)

        promedio = repo.obtener_promedio_grupal_materia(1, None, 1)

        self.assertEqual(promedio, 3.0)
        self.assertNotEqual(promedio, 3.86)

    def test_cada_estudiante_se_pondera_por_seccion(self):
        # Estudiante 1: (2.0*60 + 5.0*40)/100 = 3.2
        # Estudiante 2: (5.0*60 + 5.0*40)/100 = 5.0
        # Grupal: (3.2 + 5.0) / 2 = 4.1
        filas = [
            (1, 2.0, EXAMEN, 60),
            (1, 5.0, TALLERES, 40),
            (2, 5.0, EXAMEN, 60),
            (2, 5.0, TALLERES, 40),
        ]
        repo, _ = _repo(filas)

        self.assertEqual(repo.obtener_promedio_grupal_materia(1, None, 1), 4.1)

    def test_sin_notas_devuelve_none_y_no_cero(self):
        repo, _ = _repo([])

        promedio = repo.obtener_promedio_grupal_materia(1, None, 1)

        self.assertIsNone(promedio)
        self.assertNotEqual(promedio, 0.0)

    def test_docente_agrega_el_filtro_por_curso_propio(self):
        # RN-03: al Docente se le acota la consulta a sus propios cursos.
        repo, sesion = _repo([(1, 5.0, EXAMEN, 60)])

        repo.obtener_promedio_grupal_materia(1, 7, 1)

        self.assertEqual(sesion.filtros_aplicados, 2)

    def test_administrador_no_agrega_filtro_de_docente(self):
        # H7: el id_usuario de un administrador nunca aparece en Curso.id_docente;
        # filtrarlo dejaba la consulta vacía y devolvía 0.0 como si fuera un promedio.
        repo, sesion = _repo([(1, 5.0, EXAMEN, 60)])

        promedio = repo.obtener_promedio_grupal_materia(1, None, 1)

        self.assertEqual(sesion.filtros_aplicados, 1)
        self.assertEqual(promedio, 5.0)


if __name__ == "__main__":
    unittest.main()
