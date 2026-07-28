import api from "../../../services/api";

const ERROR_CONEXION = { detail: "Error de conexión con el servidor" };

async function listarAlertas(params) {
  try {
    const response = await api.get("/api/alertas", { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}

export { listarAlertas };
