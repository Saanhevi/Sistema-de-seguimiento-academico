import { useState, useEffect } from 'react';
// Importamos las funciones desde tu archivo de servicios
import { obtenerPromedioEstudiante, obtenerPromedioGrupal } from '../services/calificacionService';

export const usePromedios = (idMateria, idPeriodo, usuarioActual) => {
  // 1. Definimos los estados donde se guardará la información
  const [promedioEstudiante, setPromedioEstudiante] = useState(null);
  const [promedioGrupal, setPromedioGrupal] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  // Sin los datos mínimos no hay nada que consultar. Se deriva en vez de apagar
  // el flag dentro del efecto, para no dejar "Calculando..." encendido para siempre.
  const parametrosListos = Boolean(idMateria && idPeriodo && usuarioActual);

  // 2. El useEffect se ejecuta cuando el componente carga
  useEffect(() => {
    if (!parametrosListos) return undefined;

    let vigente = true;

    const cargarDatos = async () => {
      setCargando(true);
      setError(null);

      try {
        // El usuario autenticado expone id_usuario (ver models/Usuario.js); sin él
        // el backend responde 422 porque id_estudiante es obligatorio.
        const dataEstudiante = await obtenerPromedioEstudiante(usuarioActual.id_usuario, idMateria, idPeriodo);
        if (!vigente) return;
        setPromedioEstudiante(dataEstudiante.promedio);

        // Cargar promedio grupal SOLO si el usuario NO es un estudiante
        if (usuarioActual.rol !== "Estudiante") {
          const dataGrupal = await obtenerPromedioGrupal(idMateria, idPeriodo);
          if (!vigente) return;
          setPromedioGrupal(dataGrupal.promedio_grupal);
        }
      } catch (err) {
        if (vigente) setError(err.detail || "Hubo un problema al cargar los promedios.");
      } finally {
        if (vigente) setCargando(false);
      }
    };

    cargarDatos();

    return () => {
      vigente = false;
    };
  }, [idMateria, idPeriodo, usuarioActual, parametrosListos]);

  // 3. Devolvemos los estados para que las pantallas los puedan utilizar
  return { promedioEstudiante, promedioGrupal, cargando: parametrosListos && cargando, error };
};