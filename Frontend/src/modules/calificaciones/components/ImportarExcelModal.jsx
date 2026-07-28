import { useState } from "react";
import { cargaMasiva, descargarPlantilla, importarExcel } from "../services/calificacionService";
import { claseBadge, formatearNota } from "../utils/notas";
import { descargarBlob } from "../utils/descargas";

/**
 * Importa las notas de una actividad desde un .xlsx (HU22).
 *
 * Tres estados: elegir archivo -> ver la vista previa -> resultado. La vista
 * previa la calcula el backend sin escribir nada; guardar reutiliza el mismo
 * POST /api/notas/carga-masiva que usa la carga manual, así que la vía Excel no
 * puede saltarse ninguna regla que la vía manual sí aplique.
 *
 * Misma firma de props que CargaMasivaModal para que TablaNotas los monte igual.
 */
export default function ImportarExcelModal({ actividad, onCerrar, onGuardadas }) {
  const [archivo, setArchivo] = useState(null);
  const [previa, setPrevia] = useState(null);
  const [subiendo, setSubiendo] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");

  const validas = previa?.filas_validas ?? [];
  const errores = previa?.errores ?? [];
  const sinNota = previa?.estudiantes_sin_nota ?? [];

  const handleDescargarPlantilla = async () => {
    setError("");
    try {
      const { blob, nombreArchivo } = await descargarPlantilla(actividad.id_actividad);
      descargarBlob(blob, nombreArchivo);
    } catch (err) {
      setError(err.detail || "No se pudo descargar la plantilla");
    }
  };

  const handleArchivo = (e) => {
    setArchivo(e.target.files?.[0] || null);
    setPrevia(null);
    setError("");
    setExito("");
  };

  const handleSubir = async (e) => {
    e.preventDefault();
    if (!archivo) {
      setError("Elige un archivo .xlsx antes de continuar");
      return;
    }

    setSubiendo(true);
    setError("");
    try {
      setPrevia(await importarExcel(actividad.id_actividad, archivo));
    } catch (err) {
      setPrevia(null);
      setError(err.detail || "No se pudo leer el archivo");
    } finally {
      setSubiendo(false);
    }
  };

  const handleGuardar = async () => {
    setGuardando(true);
    setError("");
    try {
      // nombre/apellido y fila solo servían para pintar la vista previa.
      const notas = validas.map(({ id_estudiante, calificacion, comentario }) => ({
        id_estudiante,
        calificacion,
        comentario: comentario || null
      }));
      const guardadas = await cargaMasiva({ id_actividad: actividad.id_actividad, notas });
      onGuardadas(guardadas);
      // El modal no se cierra solo: uno que desaparece deja la duda de si guardó.
      setExito(`Se guardaron ${guardadas.length} notas en «${actividad.nombre}».`);
      setPrevia(null);
      setArchivo(null);
    } catch (err) {
      setError(err.detail || "No se pudieron guardar las notas");
    } finally {
      setGuardando(false);
    }
  };

  const volverAElegir = () => {
    setPrevia(null);
    setArchivo(null);
    setError("");
  };

  return (
    <div className="cal-modal-overlay" onClick={onCerrar}>
      <div className="cal-modal cal-import" onClick={(e) => e.stopPropagation()}>
        <div className="cal-modal-header">
          <span className="cal-modal-title">Importar notas desde Excel · {actividad.nombre}</span>
          <button type="button" className="cal-modal-close" onClick={onCerrar} aria-label="Cerrar">
            ×
          </button>
        </div>

        {!previa && !exito && (
          <form onSubmit={handleSubir}>
            <p className="cal-hint">
              El archivo debe ser <strong>.xlsx</strong> y traer una columna de identidad
              (<code>correo</code>, <code>documento</code> o <code>id_estudiante</code>) y una columna{" "}
              <code>calificacion</code> con valores entre 0.00 y 5.00. Las filas sin nota se omiten.
              Si usaste fórmulas, abre y guarda el archivo en Excel antes de subirlo.
            </p>

            <p className="cal-hint">
              Lo más fácil es descargar la plantilla: ya trae la lista del curso y solo hay que
              escribir las notas.
            </p>

            <div className="cal-import-acciones">
              <button type="button" className="cal-btn secondary" onClick={handleDescargarPlantilla}>
                Descargar plantilla
              </button>
            </div>

            <div className="cal-field">
              <label htmlFor="cal-import-archivo">Archivo de notas</label>
              <input
                id="cal-import-archivo"
                type="file"
                accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                onChange={handleArchivo}
              />
            </div>

            {error && <p className="cal-error">{error}</p>}

            <div className="cal-modal-actions">
              <button type="button" className="cal-btn secondary" onClick={onCerrar}>
                Cerrar
              </button>
              <button type="submit" className="cal-btn primary" disabled={subiendo || !archivo}>
                {subiendo ? "Leyendo archivo..." : "Ver vista previa"}
              </button>
            </div>
          </form>
        )}

        {previa && (
          <>
            {/* 1. Destino: a dónde va esto, antes que nada. */}
            <p className="cal-import-destino">
              Vas a cargar notas en: <strong>{previa.actividad}</strong>
            </p>

            {/* 2. Resumen en una línea. */}
            <p className="cal-hint">
              {validas.length} notas listas · {errores.length} filas con error ·{" "}
              {previa.filas_omitidas} sin nota · {sinNota.length} sin mencionar
            </p>

            {/* 3. Filas válidas: la confirmación de que las notas cayeron donde debían. */}
            {validas.length > 0 && (
              <div className="cal-table-wrap cal-import-lista">
                <table className="cal-table">
                  <thead>
                    <tr>
                      <th>Fila</th>
                      <th>Estudiante</th>
                      <th>Nota</th>
                      <th>Comentario</th>
                    </tr>
                  </thead>
                  <tbody>
                    {validas.map((fila) => (
                      <tr key={fila.fila}>
                        <td>{fila.fila}</td>
                        <td>
                          {fila.nombre} {fila.apellido}
                        </td>
                        <td>
                          <span className={`cal-badge ${claseBadge(fila.calificacion)}`}>
                            {formatearNota(fila.calificacion)}
                          </span>
                        </td>
                        <td>{fila.comentario || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* 4. Errores: fila de Excel, columna, valor y qué hacer. */}
            {errores.length > 0 && (
              <div className="cal-import-errores">
                <h4 className="cal-section-title">Filas con error ({errores.length})</h4>
                <ul>
                  {errores.map((item, indice) => (
                    <li key={`${item.fila}-${item.columna}-${indice}`} className="cal-error">
                      <strong>Fila {item.fila}</strong> · columna <code>{item.columna}</code>
                      {item.valor ? ` · valor "${item.valor}"` : ""} — {item.mensaje}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 5. Estudiantes sin nota: aviso, no error. */}
            {sinNota.length > 0 && (
              <div className="cal-import-avisos">
                <h4 className="cal-section-title">Sin nota en esta actividad ({sinNota.length})</h4>
                <ul>
                  {sinNota.map((estudiante) => (
                    <li key={estudiante.id_estudiante} className="cal-hint">
                      {estudiante.nombre} {estudiante.apellido} no aparece en el archivo y sigue sin
                      nota en esta actividad.
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {error && <p className="cal-error">{error}</p>}

            {/* 6. El botón nombra el destino: es lo que reemplaza a meter el
                id_actividad en el archivo. Al lado, lo que queda fuera. */}
            <div className="cal-modal-actions">
              <button type="button" className="cal-btn secondary" onClick={volverAElegir}>
                Elegir otro archivo
              </button>
              {errores.length > 0 && validas.length > 0 && (
                <span className="cal-hint">
                  {errores.length} {errores.length === 1 ? "fila queda" : "filas quedan"} fuera
                </span>
              )}
              <button
                type="button"
                className="cal-btn primary"
                disabled={guardando || validas.length === 0}
                onClick={handleGuardar}
              >
                {guardando
                  ? "Guardando..."
                  : `Guardar ${validas.length} notas en «${previa.actividad}»`}
              </button>
            </div>
          </>
        )}

        {exito && (
          <>
            <p className="cal-success">{exito}</p>
            <p className="cal-hint">
              Si tienes que corregir algo, vuelve a subir el archivo: las notas ya guardadas se
              actualizan en vez de duplicarse.
            </p>
            {error && <p className="cal-error">{error}</p>}
            <div className="cal-modal-actions">
              <button type="button" className="cal-btn secondary" onClick={() => setExito("")}>
                Importar otro archivo
              </button>
              <button type="button" className="cal-btn primary" onClick={onCerrar}>
                Cerrar
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
