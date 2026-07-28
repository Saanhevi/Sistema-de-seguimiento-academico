/**
 * Dispara la descarga de un Blob en el navegador.
 *
 * Hace falta porque los endpoints que devuelven archivos exigen Authorization
 * Bearer: un <a href> apuntando a la API no pasa por el interceptor de axios y
 * bajaría un 401. El archivo se pide con responseType "blob" y se entrega desde
 * memoria con un <a> sintético.
 */
export function descargarBlob(blob, nombreArchivo) {
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  document.body.removeChild(enlace);
  // Sin esto el Blob se queda en memoria hasta que se cierre la pestaña.
  URL.revokeObjectURL(url);
}
