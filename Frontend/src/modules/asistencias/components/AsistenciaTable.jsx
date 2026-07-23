import { useEffect, useState } from "react";
import "../styles/Asistencia.css";
export default function AsistenciaTable({

    asistencias,

    onGuardar

}) {

    const [lista, setLista] = useState([]);

    useEffect(() => {

        setLista(asistencias);

    }, [asistencias]);

    function cambiarEstado(idEstudiante, nuevoEstado) {

        setLista(

            lista.map((estudiante) =>

                estudiante.id_estudiante === idEstudiante

                    ? {

                        ...estudiante,

                        estado: nuevoEstado

                    }

                    : estudiante

            )

        );

    }

    function guardarCambios() {

        const datos = lista.map((estudiante) => ({

            id_estudiante: estudiante.id_estudiante,

            estado: estudiante.estado

        }));

        onGuardar(datos);

    }

    if (lista.length === 0) {

        return (

            <p>

                No existen estudiantes.

            </p>

        );

    }

    return (

    <div className="asistencia-card">

        <h3>

            Lista de asistencia

        </h3>

        <table className="tabla-asistencia">

            <thead>

                <tr>

                    <th>Estudiante</th>

                    <th>Estado</th>

                </tr>

            </thead>

            <tbody>

            {

                lista.map((estudiante)=>(

                    <tr key={estudiante.id_estudiante}>

                        <td>

                            {estudiante.nombres} {estudiante.apellidos}

                        </td>

                        <td>

                            <select

                                className="estado-select"

                                value={estudiante.estado}

                                onChange={(e)=>

                                    cambiarEstado(

                                        estudiante.id_estudiante,

                                        e.target.value

                                    )

                                }

                            >

                                <option value="Presente">

                                    Presente

                                </option>

                                <option value="Ausente">

                                    Ausente

                                </option>

                                <option value="Tardanza">

                                    Tardanza

                                </option>

                            </select>

                        </td>

                    </tr>

                ))

            }

            </tbody>

        </table>

        <div className="guardar-container">

            <button

                className="asistencia-btn"

                onClick={guardarCambios}

            >

                Guardar asistencia

            </button>

        </div>

    </div>

    );

}