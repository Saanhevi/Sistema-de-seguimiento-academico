import { useEffect, useState } from "react";
import "../../../asistencias/styles/Asistencia.css";
import { useAuth } from "../../../../context/AuthContext";

import {
    listarCursosDocente,
    historialDiasCurso,
    obtenerListaAsistencia,
    guardarListaAsistencia
} from "../../../asistencias/services/asistenciaService";

import CursoSelector from "../../../asistencias/components/CursoSelector";
import HistorialDias from "../../../asistencias/components/HistorialDias";
import AsistenciaTable from "../../../asistencias/components/AsistenciaTable";

export default function DocenteAsistencia() {
    const { user } = useAuth();

    const [cursos, setCursos] = useState([]);
    const [cursoSeleccionado, setCursoSeleccionado] = useState("");
    const [dias, setDias] = useState([]);
    const [listaAsistencia, setListaAsistencia] = useState(null);
    const [loading, setLoading] = useState(false);
    const [mensaje, setMensaje] = useState({ type: "", text: "" });

    useEffect(() => {
        if (user) {
            cargarCursos();
        }
    }, [user]);

    async function cargarCursos() {
        try {
            const data = await listarCursosDocente(user.id_usuario);
            setCursos(data);
            setMensaje({ type: "", text: "" });
        } catch (err) {
            console.error(err);
            setMensaje({
                type: "error",
                text: "No fue posible cargar los cursos."
            });
        }
    }

    async function seleccionarCurso(idCurso) {
        setCursoSeleccionado(idCurso);
        setListaAsistencia(null);
        setMensaje({ type: "", text: "" });

        if (!idCurso) {
            setDias([]);
            return;
        }

        try {
            const historial = await historialDiasCurso(idCurso);
            setDias(historial);
        } catch (err) {
            console.error("Error cargando historial", err);
            setMensaje({
                type: "error",
                text: "No fue posible cargar el historial del curso."
            });
        }
    }

    async function cargarLista(fecha) {
        if (!cursoSeleccionado || !fecha) return;

        try {
            setLoading(true);
            setMensaje({ type: "", text: "" });
            const lista = await obtenerListaAsistencia(cursoSeleccionado, fecha);
            setListaAsistencia(lista);
        } catch (err) {
            console.error(err);
            setMensaje({
                type: "error",
                text: "No fue posible cargar la lista de asistencia."
            });
        } finally {
            setLoading(false);
        }
    }

    async function crearNuevoDia(fecha) {
        await cargarLista(fecha);
        try {
            const historial = await historialDiasCurso(cursoSeleccionado);
            setDias(historial);
        } catch (err) {
            console.error(err);
        }
    }

    async function guardar(asistencias) {
        if (!listaAsistencia?.id_dia) {
            setMensaje({ type: "error", text: "No hay una lista activa para guardar." });
            return;
        }

        try {
            await guardarListaAsistencia(listaAsistencia.id_dia, asistencias);
            setMensaje({ type: "success", text: "Asistencia guardada correctamente." });
        } catch (err) {
            console.error(err);
            setMensaje({
                type: "error",
                text: "No fue posible guardar la asistencia."
            });
        }
    }

    return (
        <div className="asistencia-container">
            <h2>Tomar asistencia</h2>

            {mensaje.text && (
                <p className={`message ${mensaje.type}`}>{mensaje.text}</p>
            )}

            <CursoSelector
                cursos={cursos}
                cursoSeleccionado={cursoSeleccionado}
                onSeleccionarCurso={seleccionarCurso}
            />

            {cursoSeleccionado !== "" && (
                <HistorialDias
                    dias={dias}
                    onSeleccionarDia={cargarLista}
                    onCrearDia={crearNuevoDia}
                />
            )}

            {loading && <p>Cargando...</p>}

            {listaAsistencia && (
                <AsistenciaTable
                    asistencias={listaAsistencia.asistencias}
                    onGuardar={guardar}
                />
            )}
        </div>
    );
}