import api from "../../../services/api";

const useMocks = import.meta.env.DEV && import.meta.env.VITE_USE_MOCKS === "true";

const mockGrados = [
  { id_grado: 1, nombre: "10°" },
  { id_grado: 2, nombre: "11°" }
];

const mockMaterias = [
  { id_materia: 1, nombre: "Matemáticas" },
  { id_materia: 2, nombre: "Ciencias" }
];

const mockPeriodos = [
  { id_periodo: 1, nombre: "Primer Periodo", anio: 2026, estado: "Abierto" }
];

const mockCursos = [
  { id_curso: 1, id_docente: 1, id_grado: 1, id_materia: 1, id_periodo: 1 }
];

const mockMatriculas = [
  { id_matricula: 1, id_estudiante: 1, id_grado: 1, anio: 2026 }
];

const mockEstudiantes = [
  { id_estudiante: 1, nombre: "Luis", apellido: "Pérez", correo: "luis@colegio.com" }
];

async function listarGrados() {
  if (useMocks) return mockGrados;
  try {
    const response = await api.get("/api/grados");
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function crearGrado(nombre) {
  if (useMocks) {
    const nuevo = { id_grado: Date.now(), nombre };
    mockGrados.push(nuevo);
    return nuevo;
  }
  try {
    const response = await api.post("/api/grados", { nombre });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function listarMaterias() {
  if (useMocks) return mockMaterias;
  try {
    const response = await api.get("/api/materias");
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function crearMateria(nombre) {
  if (useMocks) {
    const nueva = { id_materia: Date.now(), nombre };
    mockMaterias.push(nueva);
    return nueva;
  }
  try {
    const response = await api.post("/api/materias", { nombre });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function listarPeriodos() {
  if (useMocks) return mockPeriodos;
  try {
    const response = await api.get("/api/periodos");
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function crearPeriodo(nombre, anio, estado) {
  if (useMocks) {
    const nuevo = { id_periodo: Date.now(), nombre, anio, estado };
    mockPeriodos.push(nuevo);
    return nuevo;
  }
  try {
    const response = await api.post("/api/periodos", { nombre, anio, estado });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function listarCursos(idGrado) {
  if (useMocks) {
    if (idGrado) return mockCursos.filter((curso) => curso.id_grado === Number(idGrado));
    return mockCursos;
  }
  try {
    const response = await api.get("/api/cursos", { params: { id_grado: idGrado } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function crearCurso(payload) {
  if (useMocks) {
    const nuevo = { id_curso: Date.now(), ...payload };
    mockCursos.push(nuevo);
    return nuevo;
  }
  try {
    const response = await api.post("/api/cursos", payload);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function listarMatriculas(idGrado, anio) {
  if (useMocks) {
    let result = mockMatriculas;
    if (idGrado) result = result.filter((item) => item.id_grado === Number(idGrado));
    if (anio) result = result.filter((item) => item.anio === Number(anio));
    return result;
  }
  try {
    const response = await api.get("/api/matriculas", { params: { id_grado: idGrado, anio } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function crearMatricula(payload) {
  if (useMocks) {
    const nueva = { id_matricula: Date.now(), ...payload };
    mockMatriculas.push(nueva);
    return nueva;
  }
  try {
    const response = await api.post("/api/matriculas", payload);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

async function listarEstudiantesDeGrado(idGrado, anio) {
  if (useMocks) {
    return mockEstudiantes.filter((estudiante) => estudiante.id_estudiante === 1 && Number(idGrado) === 1 && (!anio || Number(anio) === 2026));
  }
  try {
    const response = await api.get(`/api/grados/${idGrado}/estudiantes`, { params: { anio } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

export {
  listarGrados,
  crearGrado,
  listarMaterias,
  crearMateria,
  listarPeriodos,
  crearPeriodo,
  listarCursos,
  crearCurso,
  listarMatriculas,
  crearMatricula,
  listarEstudiantesDeGrado
};
