import api from "../../../services/api";

const mockProfesores = [
  {
    id: 1,
    nombres: "Ana",
    apellidos: "Pérez",
    correo: "ana.perez@institucion.edu",
    password: "123456",
    estado: true,
  },
  {
    id: 2,
    nombres: "Carlos",
    apellidos: "Ruiz",
    correo: "carlos.ruiz@institucion.edu",
    password: "123456",
    estado: false,
  },
];

export async function listarProfesores() {
  // TODO: reemplazar por llamada real al backend cuando exista el endpoint.
  return mockProfesores;
}

export async function crearProfesor(data) {
  // TODO: conectar con POST /docentes o /usuarios cuando exista el endpoint.
  return { id: Date.now(), ...data };
}

export async function actualizarProfesor(id, data) {
  // TODO: conectar con PUT /docentes/{id} cuando exista el endpoint.
  return { id, ...data };
}

export async function activarDesactivarProfesor(id, estado) {
  // TODO: conectar con el endpoint real de activación/desactivación.
  return { id, estado };
}

export async function obtenerProfesoresDesdeApi() {
  try {
    const response = await api.get("/api/docentes");
    return response.data;
  } catch (error) {
    console.warn("No se pudo cargar la lista desde el backend; se usa mock data temporal.", error);
    return mockProfesores;
  }
}
