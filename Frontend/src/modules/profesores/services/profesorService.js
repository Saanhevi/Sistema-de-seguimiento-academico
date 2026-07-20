import api from "../../../services/api";

export async function listarProfesores() {
  const response = await api.get("/api/docentes");
  return response.data;
}

export async function crearProfesor(data) {
  const response = await api.post("/api/docentes", data);
  return response.data;
}

export async function actualizarProfesor(id, data) {
  const response = await api.put(`/api/docentes/${id}`, data);
  return response.data;
}

export async function activarDesactivarProfesor(id, estado) {
  const response = await api.patch(`/api/docentes/${id}/estado`, { estado });
  return response.data;
}

export async function obtenerProfesoresDesdeApi() {
  return listarProfesores();
}
