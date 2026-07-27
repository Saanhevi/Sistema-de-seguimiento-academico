import "../styles/Asistencia.css";

export default function CursoSelector({

    cursos,

    cursoSeleccionado,

    onSeleccionarCurso

}){

    return(

    <div className="asistencia-card">

    <h3>

    Curso

    </h3>

    <select

    className="asistencia-select"

    value={cursoSeleccionado}

    onChange={(e)=>onSeleccionarCurso(Number(e.target.value))}

    >

    <option value="">

    Seleccione un curso

    </option>

    {

    cursos.map((curso)=>(

    <option

    key={curso.id_curso}

    value={curso.id_curso}

    >

    {curso.grado} - {curso.materia}

    </option>

    ))

    }

    </select>

    </div>

    );

}