import { useState, useEffect } from 'react';
// Importamos las funciones desde tu archivo de servicios
import { obtenerPromedioEstudiante, obtenerPromedioGrupal } from '../services/calificacionService';

export const usePromedios = (idMateria, idPeriodo, usuarioActual) => {
  // 1. Definimos los estados donde se guardará la información
  const [promedioEstudiante, setPromedioEstudiante] = useState(null);
  const [promedioGrupal, setPromedioGrupal] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  // 2. El useEffect se ejecuta cuando el componente carga
  useEffect(() => {
    const cargarDatos = async () => {
      setCargando(true);
      setError(null);
      
      try {
        // Cargar promedio del estudiante 
        const dataEstudiante = await obtenerPromedioEstudiante(usuarioActual.id, idMateria, idPeriodo);
        setPromedioEstudiante(dataEstudiante.promedio);

        // Cargar promedio grupal SOLO si el usuario NO es un estudiante
        if (usuarioActual.rol !== "Estudiante") {
          const dataGrupal = await obtenerPromedioGrupal(idMateria, idPeriodo);
          setPromedioGrupal(dataGrupal.promedio_grupal);
        }
      } catch (err) {
        console.error("Error cargando promedios:", err);
        setError(err.detail || "Hubo un problema al cargar los promedios.");
      } finally {
        setCargando(false);
      }
    };

    // Validamos que existan los datos mínimos antes de llamar al backend
    if (idMateria && idPeriodo && usuarioActual) {
      cargarDatos();
    }
  }, [idMateria, idPeriodo, usuarioActual]);

  // 3. Devolvemos los estados para que las pantallas los puedan utilizar
  return { promedioEstudiante, promedioGrupal, cargando, error };
};