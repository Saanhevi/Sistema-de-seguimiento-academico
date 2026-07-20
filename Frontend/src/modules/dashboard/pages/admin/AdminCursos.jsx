import { useState } from "react";
import GradoPanel from "../../../cursos/components/GradoPanel";
import MateriaPanel from "../../../cursos/components/MateriaPanel";
import PeriodoPanel from "../../../cursos/components/PeriodoPanel";
import CursoPanel from "../../../cursos/components/CursoPanel";
import MatriculaPanel from "../../../cursos/components/MatriculaPanel";

export const AdminCursos = () => {
  const [tabActiva, setTabActiva] = useState("grados");

  const tabs = [
    { key: "grados", label: "Grados" },
    { key: "materias", label: "Materias" },
    { key: "periodos", label: "Períodos" },
    { key: "cursos", label: "Cursos" },
    { key: "matriculas", label: "Matrículas" }
  ];

  return (
    <div className="main">
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Gestión académica</h2>
        </div>

        <div className="curso-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              className={`curso-tab ${tabActiva === tab.key ? "active" : ""}`}
              onClick={() => setTabActiva(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {tabActiva === "grados" && <GradoPanel />}
        {tabActiva === "materias" && <MateriaPanel />}
        {tabActiva === "periodos" && <PeriodoPanel />}
        {tabActiva === "cursos" && <CursoPanel />}
        {tabActiva === "matriculas" && <MatriculaPanel />}
      </div>
    </div>
  );
};
