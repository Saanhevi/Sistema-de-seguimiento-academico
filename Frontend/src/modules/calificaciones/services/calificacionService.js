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

/**
 * HU22: sube un .xlsx y devuelve la vista previa (filas válidas + errores).
 * No escribe nada: quien guarda es cargaMasiva() cuando el docente confirma.
 */
async function importarExcel(idActividad, archivo) {
  const formData = new FormData();
  formData.append("id_actividad", idActividad);
  formData.append("archivo", archivo);

  try {
    // El Content-Type global de services/api.js es application/json y aquí no
    // sirve. Axios detecta el FormData y pone el boundary por su cuenta, pero
    // no puede adivinar que este POST no es JSON.
    const response = await api.post("/api/notas/importar-excel", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

/**
 * HU22: descarga la plantilla del curso como Blob.
 *
 * No se puede usar un <a href> normal: el endpoint exige Authorization Bearer y
 * un enlace directo del navegador no pasa por el interceptor de axios, así que
 * devolvería un 401 o un archivo con el JSON del error dentro.
 */
async function descargarPlantilla(idActividad) {
  try {
    const response = await api.get("/api/notas/plantilla-excel", {
      params: { id_actividad: idActividad },
      responseType: "blob"
    });
    return { blob: response.data, nombreArchivo: nombreDeContentDisposition(response.headers) };
  } catch (error) {
    // Con responseType blob, el cuerpo de un error también llega como Blob y
    // `error.response.data.detail` sería undefined.
    throw (await leerErrorBlob(error)) || ERROR_CONEXION;
  }
}

/** Nombre de archivo del header Content-Disposition, con un respaldo razonable. */
function nombreDeContentDisposition(headers) {
  const cabecera = headers?.["content-disposition"] || "";
  const coincidencia = cabecera.match(/filename="?([^"]+)"?/);
  return coincidencia?.[1] || "notas.xlsx";
}

/** Traduce a {detail} un error cuyo cuerpo vino como Blob. */
async function leerErrorBlob(error) {
  const datos = error.response?.data;
  if (!datos) return null;
  if (typeof datos.text !== "function") return datos;
  try {
    return JSON.parse(await datos.text());
  } catch {
    return null;
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
  listarMisCursosEstudiante,
  listarSecciones,
  crearSeccion,
  listarActividades,
  crearActividad,
  listarNotas,
  registrarNota,
  cargaMasiva,
  importarExcel,
  descargarPlantilla,
  listarMisMatriculas,
  // Reexportada desde cursoService para no duplicar la llamada al mismo endpoint.
  listarEstudiantesDeGrado,
  actualizarNota,
  eliminarActividad,
  eliminarSeccion
};
