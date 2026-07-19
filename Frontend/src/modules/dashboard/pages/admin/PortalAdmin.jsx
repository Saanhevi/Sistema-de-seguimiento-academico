// eslint-disable-next-line no-unused-vars
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';

export default function PortalAdmin() {
  const location = useLocation();
  const isHomeView = location.pathname === '/dashboard/admin';

  if (!isHomeView) {
    return <Outlet />;
  }

  return (
    <>
      <main className="main">
        <div className="admin-panel-header">
          <h1>Panel administrativo</h1>
          <p>Selecciona una sección del menú para navegar entre cursos, estudiantes y profesores.</p>
        </div>
      </main>
    </>
  );
}
