from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.docente import Docente
from app.models.acudiente import Acudiente
from app.models.estudiante import Estudiante

from app.core.database import SessionLocal
from app.repositories.usuario import UsuarioRepository
from app.core.security import controlador_contrasena

usuarios = [

    # ==========================================================
    # ADMINISTRADORES (2)
    # ==========================================================

    {
        "nombres": "Samuel Andres",
        "apellidos": "Herrera Villero",
        "correo": "samuel.herrera@colegio.edu.co",
        "password": "Admin123!",
        "rol": "Administrador"
    },
    {
        "nombres": "Laura",
        "apellidos": "Gomez Perez",
        "correo": "laura.gomez@colegio.edu.co",
        "password": "Admin123!",
        "rol": "Administrador"
    },

    # ==========================================================
    # DOCENTES (10)
    # ==========================================================

    {
        "nombres": "Carlos",
        "apellidos": "Rodriguez Diaz",
        "correo": "carlos.rodriguez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Mariana",
        "apellidos": "Lopez Torres",
        "correo": "mariana.lopez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Juan",
        "apellidos": "Martinez Ruiz",
        "correo": "juan.martinez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Sofia",
        "apellidos": "Castro Silva",
        "correo": "sofia.castro@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Diana",
        "apellidos": "Ramirez Vargas",
        "correo": "diana.ramirez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Fernando",
        "apellidos": "Jimenez Ortiz",
        "correo": "fernando.jimenez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Paola",
        "apellidos": "Suarez Gomez",
        "correo": "paola.suarez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Andres Felipe",
        "apellidos": "Perez Molina",
        "correo": "andres.perez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Liliana",
        "apellidos": "Castillo Cruz",
        "correo": "liliana.castillo@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Oscar",
        "apellidos": "Rojas Medina",
        "correo": "oscar.rojas@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },

    # ==========================================================
    # ESTUDIANTES (20)
    # ==========================================================

    {
        "nombres": "David",
        "apellidos": "Ramirez Moreno",
        "correo": "david.ramirez@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Camila",
        "apellidos": "Vargas Romero",
        "correo": "camila.vargas@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Andres",
        "apellidos": "Morales Rojas",
        "correo": "andres.morales@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Valentina",
        "apellidos": "Garcia Pinto",
        "correo": "valentina.garcia@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Miguel",
        "apellidos": "Suarez Medina",
        "correo": "miguel.suarez@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Daniela",
        "apellidos": "Ortega Gil",
        "correo": "daniela.ortega@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Felipe",
        "apellidos": "Pineda Cruz",
        "correo": "felipe.pineda@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Natalia",
        "apellidos": "Hernandez Lara",
        "correo": "natalia.hernandez@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Sebastian",
        "apellidos": "Ruiz Gomez",
        "correo": "sebastian.ruiz@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Laura",
        "apellidos": "Mendoza Ortiz",
        "correo": "laura.mendoza@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Nicolas",
        "apellidos": "Castro Vega",
        "correo": "nicolas.castro@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Sara",
        "apellidos": "Lozano Arias",
        "correo": "sara.lozano@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Julian",
        "apellidos": "Cortes Medina",
        "correo": "julian.cortes@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Valeria",
        "apellidos": "Rios Herrera",
        "correo": "valeria.rios@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Mateo",
        "apellidos": "Silva Navarro",
        "correo": "mateo.silva@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Gabriela",
        "apellidos": "Torres Leon",
        "correo": "gabriela.torres@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Juan Pablo",
        "apellidos": "Moreno Cruz",
        "correo": "juanpablo.moreno@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Maria Jose",
        "apellidos": "Alvarez Pinto",
        "correo": "mariajose.alvarez@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Cristian",
        "apellidos": "Vargas Soto",
        "correo": "cristian.vargas@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Ana Sofia",
        "apellidos": "Prieto Rojas",
        "correo": "anasofia.prieto@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },

    # ==========================================================
    # ACUDIENTES (20)
    # ==========================================================

    {
        "nombres": "Jorge",
        "apellidos": "Sanchez Cardenas",
        "correo": "jorge.sanchez@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Paula",
        "apellidos": "Navarro Fuentes",
        "correo": "paula.navarro@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Luis",
        "apellidos": "Cifuentes Leon",
        "correo": "luis.cifuentes@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Isabella",
        "apellidos": "Mendoza Rios",
        "correo": "isabella.mendoza@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Diego",
        "apellidos": "Velasquez Arias",
        "correo": "diego.velasquez@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Sara",
        "apellidos": "Quintero Vega",
        "correo": "sara.quintero@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Ricardo",
        "apellidos": "Lopez Gil",
        "correo": "ricardo.lopez@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Patricia",
        "apellidos": "Moreno Diaz",
        "correo": "patricia.moreno@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Javier",
        "apellidos": "Castillo Ruiz",
        "correo": "javier.castillo@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Martha",
        "apellidos": "Ortega Perez",
        "correo": "martha.ortega@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Hector",
        "apellidos": "Ramirez Torres",
        "correo": "hector.ramirez@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Claudia",
        "apellidos": "Silva Romero",
        "correo": "claudia.silva@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Eduardo",
        "apellidos": "Rojas Vega",
        "correo": "eduardo.rojas@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Adriana",
        "apellidos": "Gutierrez Leon",
        "correo": "adriana.gutierrez@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Mauricio",
        "apellidos": "Garzon Molina",
        "correo": "mauricio.garzon@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Gloria",
        "apellidos": "Herrera Cruz",
        "correo": "gloria.herrera@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "William",
        "apellidos": "Parra Medina",
        "correo": "william.parra@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Sandra",
        "apellidos": "Fonseca Arias",
        "correo": "sandra.fonseca@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Alberto",
        "apellidos": "Reyes Cardenas",
        "correo": "alberto.reyes@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Monica",
        "apellidos": "Campos Lozano",
        "correo": "monica.campos@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    }
]

with SessionLocal() as session:

    repositorio_usuario = UsuarioRepository(session)

    for datos in usuarios:

        usuario = Usuario(
            nombres=datos["nombres"],
            apellidos=datos["apellidos"],
            correo=datos["correo"],
            password_hash=controlador_contrasena.hashear(datos["password"]),
            rol=datos["rol"]
        )

        repositorio_usuario.crear(usuario)

        if usuario.rol == "Administrador":

            session.add(
                Administrador(
                    id_admin=usuario.id_usuario
                )
            )

        elif usuario.rol == "Docente":

            session.add(
                Docente(
                    id_docente=usuario.id_usuario,
                    estado="Activo"
                )
            )

        elif usuario.rol == "Estudiante":

            session.add(
                Estudiante(
                    id_estudiante=usuario.id_usuario,
                    estado="Activo"
                )
            )

        elif usuario.rol == "Acudiente":

            session.add(
                Acudiente(
                    id_acudiente=usuario.id_usuario
                )
            )

        print(f"✓ {usuario.rol}: {usuario.nombres} {usuario.apellidos}")

    session.commit()

print("Usuarios creados correctamente.")