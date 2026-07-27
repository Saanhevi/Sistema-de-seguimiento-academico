import { useState } from "react";
import "../styles/Asistencia.css";

export default function HistorialDias({ dias, onSeleccionarDia, onCrearDia }) {
    const [nuevaFecha, setNuevaFecha] = useState("");
    const diasRegistrados = dias ?? [];

    return (
        <div className="asistencia-card">
            <h3>Días registrados</h3>

            {diasRegistrados.length === 0 ? (
                <p>No existen registros.</p>
            ) : (
                <div className="historial-lista">
                    {diasRegistrados.map((dia) => (
                        <button
                            key={dia.fecha}
                            className="historial-btn"
                            onClick={() => onSeleccionarDia(dia.fecha)}
                        >
                            {dia.fecha}
                        </button>
                    ))}
                </div>
            )}

            <hr />

            <h4>Crear nuevo día</h4>
            <input
                className="asistencia-input"
                type="date"
                value={nuevaFecha}
                onChange={(e) => setNuevaFecha(e.target.value)}
            />

            <button
                className="asistencia-btn"
                onClick={() => {
                    if (!nuevaFecha) return;
                    onCrearDia(nuevaFecha);
                    setNuevaFecha("");
                }}
            >
                Crear día
            </button>
        </div>
    );
}