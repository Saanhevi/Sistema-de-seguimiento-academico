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
    const [error, setError] = useState("");

    useEffect(() => {
        if (user) {
            cargarCursos();
        }
    }, [user]);

    async function cargarCursos() {

        try {

            console.log("Usuario autenticado:", user);

            const data = await listarCursosDocente(user.id_usuario);

            setCursos(data);

        } catch (err) {

            console.error(err);

            setError("No fue posible cargar los cursos.");

        }

    }

    async function seleccionarCurso(idCurso) {

        setCursoSeleccionado(idCurso);

        setListaAsistencia(null);

        if (!idCurso) {

            setDias([]);

            return;

        }

        try {

            const historial = await historialDiasCurso(idCurso);

            setDias(historial);

        } catch (err) {

            console.error("Error cargando historial", err);
            setError(
                "No fue posible cargar el historial. " +
                (err.response?.data?.detail || err.message || "Revise la consola.")
            );

        }

    }

    async function cargarLista(fecha) {

        try {

            setLoading(true);

            const lista = await obtenerListaAsistencia(
                cursoSeleccionado,
                fecha
            );

            setListaAsistencia(lista);

        } catch {

            setError("No fue posible cargar la lista.");

        } finally {

            setLoading(false);

        }

    }

    async function crearNuevoDia(fecha) {

        await cargarLista(fecha);

        const historial = await historialDiasCurso(cursoSeleccionado);

        setDias(historial);

    }

    async function guardar(asistencias) {

        try {

            await guardarListaAsistencia(
                listaAsistencia.id_dia,
                asistencias
            );

            alert("Lista guardada correctamente.");

        } catch {

            alert("Error al guardar.");

        }

    }

    return (

        <div className="asistencia-container">

            <h2>Tomar asistencia</h2>

            {error && <p className="error">{error}</p>}

            <CursoSelector
                cursos={cursos}
                cursoSeleccionado={cursoSeleccionado}
                onSeleccionarCurso={seleccionarCurso}
            />

            {
                cursoSeleccionado !== "" &&

                <HistorialDias
                    dias={dias}
                    onSeleccionarDia={cargarLista}
                    onCrearDia={crearNuevoDia}
                />
            }

            {loading && <p>Cargando...</p>}

            {
                listaAsistencia &&

                <AsistenciaTable
                    asistencias={listaAsistencia.asistencias}
                    onGuardar={guardar}
                />
            }

        </div>

    );

}