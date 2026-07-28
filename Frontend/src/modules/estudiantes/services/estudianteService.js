import api from "../../../services/api";

export async function listarEstudiantes(incluirInactivos = true) {
  const response = await api.get("/api/estudiantes", {
    params: { incluir_inactivos: incluirInactivos }
  });
  return response.data;
}

export async function retirarEstudiante(idEstudiante) {
  const response = await api.patch(`/api/estudiantes/${idEstudiante}/retiro`);
  return response.data;
}
