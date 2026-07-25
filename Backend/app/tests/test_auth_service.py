"""
Pruebas del AuthService y del esquema TokenResponse.

Cubren los dos cambios que el módulo de calificaciones necesita del login:
  - el login devuelve id_usuario (el frontend lo usa para pedir "mis cursos"
    y "mis matrículas" sin tener que decodificar el JWT);
  - al crear una cuenta estudiantil se crea también la fila en Estudiante,
    sin la cual las notas del alumno no se pueden guardar (Nota.id_estudiante
    tiene FK contra estudiante, no contra usuario).

No tocan la base de datos: la sesión y los repositorios son dobles de prueba.
"""

import os
import unittest
from unittest.mock import MagicMock, Mock, patch

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5433/gestion_academica")
os.environ.setdefault("SECRET_KEY", "dev_secret_key_local_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi import HTTPException
from pydantic import ValidationError

from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.schemas.auth import CrearCuentaEstudiantilRequest, LoginRequest, TokenResponse
from app.services.auth import AuthService


class LoginTests(unittest.TestCase):

    def setUp(self):
        # MagicMock y no Mock: AuthService usa `with self.session as session`.
        self.session = MagicMock()
        self.repositorio = Mock()
        self.service = AuthService(self.session, self.repositorio)
        self.credenciales = LoginRequest(correo="carlos.rodriguez@colegio.edu.co", password="Docente123!")

    def test_login_devuelve_id_usuario(self):
        self.repositorio.buscar_por_correo.return_value = Usuario(
            id_usuario=7,
            nombres="Carlos",
            apellidos="Rodriguez Diaz",
            correo="carlos.rodriguez@colegio.edu.co",
            password_hash="hash",
            rol="Docente",
        )

        with patch("app.services.auth.controlador_contrasena.verificar_contrasena", return_value=True):
            respuesta = self.service.autenticar_usuario(self.credenciales)

        self.assertEqual(respuesta["id_usuario"], 7)
        self.assertEqual(respuesta["rol"], "Docente")
        # El contrato completo que consume el frontend en AuthContext.login
        self.assertEqual(
            set(respuesta),
            {"access_token", "token_type", "rol", "nombres", "apellidos", "id_usuario"},
        )

    def test_login_con_password_incorrecta_no_expone_id_usuario(self):
        self.repositorio.buscar_por_correo.return_value = Usuario(
            id_usuario=7,
            nombres="Carlos",
            apellidos="Rodriguez Diaz",
            correo="carlos.rodriguez@colegio.edu.co",
            password_hash="hash",
            rol="Docente",
        )

        with patch("app.services.auth.controlador_contrasena.verificar_contrasena", return_value=False):
            with self.assertRaises(HTTPException) as exc:
                self.service.autenticar_usuario(self.credenciales)

        self.assertEqual(exc.exception.status_code, 401)

    def test_token_response_exige_id_usuario(self):
        payload = {
            "access_token": "jwt",
            "token_type": "bearer",
            "rol": "Docente",
            "nombres": "Carlos",
            "apellidos": "Rodriguez Diaz",
        }

        with self.assertRaises(ValidationError):
            TokenResponse(**payload)

        token = TokenResponse(**payload, id_usuario=7)
        self.assertEqual(token.id_usuario, 7)


class CrearCuentaEstudiantilTests(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock()
        self.repositorio = Mock()
        self.service = AuthService(self.session, self.repositorio)
        self.service.repositorio_estudiante = Mock()
        self.credenciales = CrearCuentaEstudiantilRequest(
            nombres="Ana",
            apellidos="Perez",
            correo="ana.perez@colegio.edu.co",
            password="Estudiante123!",
        )

    def _simular_insercion(self, id_usuario=31):
        def crear(usuario):
            usuario.id_usuario = id_usuario  # lo que hace el refresh() del repositorio real
            return usuario

        self.repositorio.crear.side_effect = crear

    def test_crea_la_fila_en_estudiante(self):
        self.repositorio.buscar_por_correo.return_value = None
        self._simular_insercion(id_usuario=31)

        with patch("app.services.auth.controlador_contrasena.hashear", return_value="hash"):
            respuesta = self.service.crear_cuenta_estudiantil(self.credenciales)

        self.assertEqual(respuesta, {"mensaje": "Registro Exitoso"})

        self.service.repositorio_estudiante.crear_estudiante.assert_called_once()
        estudiante = self.service.repositorio_estudiante.crear_estudiante.call_args.args[0]
        self.assertIsInstance(estudiante, Estudiante)
        # El id de Estudiante es el mismo del Usuario recién creado
        self.assertEqual(estudiante.id_estudiante, 31)
        self.assertEqual(estudiante.estado, "Activo")

    def test_correo_repetido_no_crea_estudiante(self):
        self.repositorio.buscar_por_correo.return_value = Usuario(id_usuario=1, rol="Estudiante")

        with self.assertRaises(HTTPException) as exc:
            self.service.crear_cuenta_estudiantil(self.credenciales)

        self.assertEqual(exc.exception.status_code, 401)
        self.repositorio.crear.assert_not_called()
        self.service.repositorio_estudiante.crear_estudiante.assert_not_called()


if __name__ == "__main__":
    unittest.main()
