import { useState } from "react";
import "../styles/Asistencia.css";
export default function HistorialDias({

    dias,

    onSeleccionarDia,

    onCrearDia

}) {
console.log("Dias recibidos:", dias);
    const [nuevaFecha, setNuevaFecha] = useState("");

        return (

    <div className="asistencia-card">

        <h3>

            Días registrados

        </h3>

        {

            dias.length===0 ?

            <p>

                No existen registros.

            </p>

            :

            <div className="historial-lista">

            {

                dias.map((dia)=>(

                    <button

                        key={dia.fecha}

                        className="historial-btn"

                        onClick={()=>onSeleccionarDia(dia.fecha)}

                    >

                        {dia.fecha}

                    </button>

                ))

            }

            </div>

        }

        <hr/>

        <h4>

            Crear nuevo día

        </h4>

        <input

            className="asistencia-input"

            type="date"

            value={nuevaFecha}

            onChange={(e)=>setNuevaFecha(e.target.value)}

        />

        <button

            className="asistencia-btn"

            onClick={()=>{

                if(!nuevaFecha) return;

                onCrearDia(nuevaFecha);

                setNuevaFecha("");

            }}

        >

            Crear día

        </button>

    </div>

    );

}