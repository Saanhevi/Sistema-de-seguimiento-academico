/**
 * Representa al usuario autenticado en el frontend.
 * @typedef {Object} Usuario
 * @property {string} rol
 * @property {string} nombres
 * @property {string} apellidos
 */

/**
 * Construye un Usuario a partir de los datos devueltos por el login.
 * @param {{rol: string, nombres: string, apellidos: string}} datos
 * @returns {Usuario}
 */
export function crearUsuario({ rol, nombres, apellidos }) {
    return { rol, nombres, apellidos };
}
