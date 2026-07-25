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

async function listarCursosDeGrado(idGrado) {
  try {
    const response = await api.get("/api/cursos", { params: { id_grado: idGrado } });
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

export {
  listarMisCursos,
  listarCursosDeGrado,
  listarSecciones,
  crearSeccion,
  listarActividades,
  crearActividad,
  listarNotas,
  registrarNota,
  cargaMasiva,
  listarMisMatriculas,
  // Reexportada desde cursoService para no duplicar la llamada al mismo endpoint.
  listarEstudiantesDeGrado
};
