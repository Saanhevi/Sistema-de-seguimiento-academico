/**
 * Representa al usuario autenticado en el frontend.
 * @typedef {Object} Usuario
 * @property {number} id_usuario
 * @property {string} rol
 * @property {string} nombres
 * @property {string} apellidos
 */

/**
 * Construye un Usuario a partir de los datos devueltos por el login.
 * @param {{id_usuario: number, rol: string, nombres: string, apellidos: string}} datos
 * @returns {Usuario}
 */
export function crearUsuario({ id_usuario, rol, nombres, apellidos }) {
    return { id_usuario, rol, nombres, apellidos };
}
