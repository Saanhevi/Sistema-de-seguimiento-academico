import api from "../../../services/api";

export async function login(credentials) {

    try {

        const response = await api.post(
            "/api/auth/login",
            credentials
        );

        return response.data;

    } catch (error) {

        throw error.response?.data || {
            detail: "Error de conexión con el servidor"
        };

    }

}