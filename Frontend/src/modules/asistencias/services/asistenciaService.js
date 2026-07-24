import api from "../../../services/api";

export async function listarCursosDocente(id_docente) {
    const response = await api.get("/api/docente/cursos", {
        params: { id_docente }
    });
    return response.data;
}

export async function obtenerListaAsistencia(idCurso, fecha) {
    const response = await api.get("/api/asistencias/listas", {
        params: {
            id_curso: idCurso,
            fecha
        }
    });

    return response.data;
}

export async function guardarListaAsistencia(idDia, asistencias) {
    const response = await api.put(
        `/api/asistencias/listas/${idDia}`,
        asistencias
    );

    return response.data;
}

export async function historialDiasCurso(idCurso) {
    const response = await api.get(`/api/asistencias/listas/${idCurso}`);
    return response.data;
}

export async function misAsistencias() {
    const response = await api.get("/api/asistencias/mis-asistencias");
    return response.data;
}