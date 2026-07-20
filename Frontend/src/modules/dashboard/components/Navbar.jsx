import { NavLink } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";

export default function Navbar() {
    const { user } = useAuth();
    const homeLink = user?.rol === "Docente"
        ? "/dashboard/docente"
        : user?.rol === "Estudiante"
            ? "/dashboard/estudiante"
            : user?.rol === "Administrador"
                ? "/dashboard/admin"
                : "/dashboard";
    const asistenciaLink = user?.rol === "Docente"
        ? "/dashboard/docente/asistencia"
        : user?.rol === "Estudiante"
            ? "/dashboard/estudiante/asistencia"
            : "/dashboard";

    return (
        <nav className="nav">
            <NavLink to={homeLink} end className={({ isActive }) => (isActive ? "active" : "") }>
                <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <rect x="3" y="3" width="7" height="7" />
                    <rect x="14" y="3" width="7" height="7" />
                    <rect x="14" y="14" width="7" height="7" />
                    <rect x="3" y="14" width="7" height="7" />
                </svg>
                Inicio
            </NavLink>

            {(user?.rol === "Docente" || user?.rol === "Estudiante") && (
                <NavLink to={asistenciaLink} className={({ isActive }) => (isActive ? "active" : "") }>
                    <svg
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    >
                        <rect x="3" y="4" width="18" height="18" rx="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                        <line x1="3" y1="10" x2="21" y2="10" />
                    </svg>
                    Asistencia
                </NavLink>
            )}

            {user?.rol === "Docente" && (
                <>
                    <NavLink to="/dashboard/docente/calificaciones" className={({ isActive }) => (isActive ? "active" : "") }>
                        <svg
                            width="15"
                            height="15"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                        </svg>
                        Calificaciones
                    </NavLink>

                    <NavLink to="/dashboard/docente/reportes" className={({ isActive }) => (isActive ? "active" : "") }>
                        <svg
                            width="15"
                            height="15"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1"
                        >
                            <rect x="5" y="8" width="3" height="11" rx="1" fill="currentColor" />
                            <rect x="10.5" y="4" width="3" height="15" rx="1" fill="currentColor" />
                            <rect x="16" y="11" width="3" height="8" rx="1" fill="currentColor" />
                        </svg>
                        Reportes
                    </NavLink>
                </>
            )}

            {user?.rol === "Estudiante" && (
                <>
                    <NavLink to="/dashboard/estudiante/asignaturas" className={({ isActive }) => (isActive ? "active" : "") }>
                        <svg
                            width="15"
                            height="15"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                        </svg>
                        Mis Asignaturas
                    </NavLink>
                    <NavLink to="/dashboard/estudiante/perfil" className={({ isActive }) => (isActive ? "active" : "") }>
                        <svg
                            width="15"
                            height="15"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                            <circle cx="9" cy="7" r="4" />
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                        </svg>
                        Perfil
                    </NavLink>
                </>
            )}

            {user?.rol === "Administrador" && (
                <>
                    <NavLink to="/dashboard/admin/cursos" className={({ isActive }) => (isActive ? "active" : "") }>
                        Cursos
                    </NavLink>
                    <NavLink to="/dashboard/admin/estudiantes" className={({ isActive }) => (isActive ? "active" : "") }>
                        Estudiantes
                    </NavLink>
                    <NavLink to="/dashboard/admin/profesores" className={({ isActive }) => (isActive ? "active" : "") }>
                        Profesores
                    </NavLink>
                </>
            )}
        </nav>
    );
}
