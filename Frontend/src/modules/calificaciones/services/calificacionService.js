import api from "../../../services/api";
import { listarEstudiantesDeGrado } from "../../cursos/services/cursoService";

const ERROR_CONEXION = { detail: "Error de conexión con el servidor" };

async function listarMisCursos(idDocente) {
  try {
    const response = await api.get("/api/cursos", { params: { id_docente: idDocente } });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

/**
 * Cursos del estudiante autenticado. No lleva filtros: el backend aplica RN-10a
 * y devuelve solo los cursos de su grado y año de matrícula (ignora cualquier
 * id_grado que se le mande), así que el alcance no se decide en el cliente.
 */
async function listarMisCursosEstudiante() {
  try {
    const response = await api.get("/api/cursos");
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function listarSecciones(idCurso) {
  try {
    const response = await api.get("/api/secciones", { params: { id_curso: idCurso } });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function crearSeccion(data) {
  try {
    const response = await api.post("/api/secciones", data);
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function listarActividades(idSeccion) {
  try {
    const response = await api.get("/api/actividades", { params: { id_seccion: idSeccion } });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function crearActividad(data) {
  try {
    const response = await api.post("/api/actividades", data);
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function listarNotas(idActividad) {
  try {
    const response = await api.get("/api/notas", { params: { id_actividad: idActividad } });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function registrarNota(data) {
  try {
    const response = await api.post("/api/notas", data);
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function actualizarNota(data) {
  try {
    const response = await api.put("/api/notas", data);
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function eliminarActividad(idActividad) {
  try {
    await api.delete(`/api/actividades/${idActividad}`);
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function eliminarSeccion(idSeccion) {
  try {
    await api.delete(`/api/secciones/${idSeccion}`);
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function cargaMasiva(data) {
  try {
    const response = await api.post("/api/notas/carga-masiva", data);
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function listarMisMatriculas(idEstudiante) {
  try {
    const response = await api.get("/api/matriculas", { params: { id_estudiante: idEstudiante } });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}
async function obtenerPromedioEstudiante(idEstudiante, idMateria, idPeriodo) {
  try {
    const response = await api.get("/api/notas/promedio", { 
      params: { 
        id_estudiante: idEstudiante, 
        id_materia: idMateria, 
        id_periodo: idPeriodo 
      } 
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

async function obtenerPromedioGrupal(idMateria, idPeriodo) {
  try {
    const response = await api.get(`/api/materia/${idMateria}/promedio-grupal`, { 
      params: { 
        id_periodo: idPeriodo 
      } 
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}
// HU8: una sola llamada devuelve el promedio de todos los estudiantes de la materia,
// en vez de pedir /api/notas/promedio una vez por estudiante.
async function obtenerPromediosEstudiantes(idMateria, idPeriodo) {
  try {
    const response = await api.get(`/api/materia/${idMateria}/promedios-estudiantes`, {
      params: {
        id_periodo: idPeriodo
      }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

export {
  listarMisCursos,
  listarMisCursosEstudiante,
  listarSecciones,
  crearSeccion,
  listarActividades,
  crearActividad,
  listarNotas,
  registrarNota,
  cargaMasiva,
  listarMisMatriculas,
  // Reexportada desde cursoService para no duplicar la llamada al mismo endpoint.
  listarEstudiantesDeGrado,
  actualizarNota,
  eliminarActividad,
  eliminarSeccion,
  obtenerPromedioEstudiante,
  obtenerPromedioGrupal,
  obtenerPromediosEstudiantes
};
