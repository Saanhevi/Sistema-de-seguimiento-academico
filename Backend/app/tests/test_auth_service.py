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
            documento="1023456789",
            password="Estudiante123!",
        )
        # HU22: por defecto el documento está libre; los tests que prueban el
        # choque lo sobreescriben.
        self.repositorio.buscar_por_documento.return_value = None

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

    # --- HU22: documento ---

    def test_guarda_el_documento_en_el_usuario(self):
        self.repositorio.buscar_por_correo.return_value = None
        self._simular_insercion()

        with patch("app.services.auth.controlador_contrasena.hashear", return_value="hash"):
            self.service.crear_cuenta_estudiantil(self.credenciales)

        usuario = self.repositorio.crear.call_args.args[0]
        self.assertEqual(usuario.documento, "1023456789")

    def test_documento_se_guarda_normalizado(self):
        """RN-r: se guarda con la misma forma con la que llegará desde un Excel."""
        credenciales = CrearCuentaEstudiantilRequest(
            nombres="Ana",
            apellidos="Perez",
            correo="otra.ana@colegio.edu.co",
            documento="1.023.456.789",
            password="Estudiante123!",
        )
        self.assertEqual(credenciales.documento, "1023456789")

    def test_documento_repetido_devuelve_409(self):
        self.repositorio.buscar_por_correo.return_value = None
        self.repositorio.buscar_por_documento.return_value = Usuario(id_usuario=1, rol="Estudiante")

        with self.assertRaises(HTTPException) as exc:
            self.service.crear_cuenta_estudiantil(self.credenciales)

        # 409 y no un 500 por violación del UNIQUE de Usuario.documento
        self.assertEqual(exc.exception.status_code, 409)
        self.repositorio.crear.assert_not_called()
        self.service.repositorio_estudiante.crear_estudiante.assert_not_called()

    def test_documento_vacio_o_corto_es_rechazado_por_el_schema(self):
        for invalido in ("", "123", "1.2.3", "no-son-veinte-caracteres-validos"):
            with self.assertRaises(ValidationError):
                CrearCuentaEstudiantilRequest(
                    nombres="Ana",
                    apellidos="Perez",
                    correo="ana.perez@colegio.edu.co",
                    documento=invalido,
                    password="Estudiante123!",
                )


if __name__ == "__main__":
    unittest.main()
