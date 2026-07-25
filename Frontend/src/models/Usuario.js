/**
 * Representa al usuario autenticado en el frontend.
 * @typedef {Object} Usuario
 * @property {string} rol
 * @property {string} nombres
 * @property {string} apellidos
 * @property {number} id_usuario
 */

/**
 * Construye un Usuario a partir de los datos devueltos por el login.
 * @param {{rol: string, nombres: string, apellidos: string, id_usuario: number}} datos
 * @returns {Usuario}
 */
export function crearUsuario({ rol, nombres, apellidos, id_usuario }) {
    return { rol, nombres, apellidos, id_usuario };
}
