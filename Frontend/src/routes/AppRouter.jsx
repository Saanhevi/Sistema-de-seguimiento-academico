import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import LoginPage from "../modules/auth/pages/LoginPage";
import RegisterPage from "../modules/auth/pages/RegisterPage";
import DashboardPage from "../modules/dashboard/pages/DashboardPage";
import PortalAdmin from "../modules/dashboard/pages/admin/PortalAdmin";
import { AdminCursos } from "../modules/dashboard/pages/admin/AdminCursos";
import AdminEstudiantes from "../modules/dashboard/pages/admin/AdminEstudiantes";
import { AdminProfesores } from "../modules/dashboard/pages/admin/AdminProfesores";
import PortalDocente from "../modules/dashboard/pages/docente/PortalDocente";
import DocenteAsistencia from "../modules/dashboard/pages/docente/DocenteAsistencia";
import DocenteEstudiantes from "../modules/dashboard/pages/docente/DocenteEstudiantes";
import DocenteCalificaciones from "../modules/dashboard/pages/docente/DocenteCalificaciones";
import DocenteReportes from "../modules/dashboard/pages/docente/DocenteReportes";
import PortalEstudiantil from "../modules/dashboard/pages/estudiante/PortalEstudiantil";
import EstudianteAsistencia from "../modules/dashboard/pages/estudiante/EstudianteAsistencia";
import EstudiantePerfil from "../modules/dashboard/pages/estudiante/EstudiantePerfil";
import EstudianteCambioContrasena from "../modules/dashboard/pages/estudiante/EstudianteCambioContrasena";
import EstudianteCalificaciones from "../modules/dashboard/pages/estudiante/EstudianteCalificaciones";


function RutaLogin() {
    const { user } = useAuth();
    return user ? <Navigate to="/dashboard" replace /> : <LoginPage />;
}

function RutaRegistro() {
    const { user } = useAuth();
    return user ? <Navigate to="/dashboard" replace /> : <RegisterPage />;
}

function RutaCambioPassword() {

    const { user } = useAuth();

    if (!user) return <Navigate to="/login" replace />;

    if (user.rol === "Estudiante") {
        return <Navigate to="/dashboard/estudiante/cambiar-password" replace />;
    }

    if (user.rol === "Docente") {
        return <Navigate to="/dashboard/docente" replace />;
    }

    if (user.rol === "Administrador") {
        return <Navigate to="/dashboard/admin" replace />;
    }

    return <Navigate to="/dashboard" replace />;

}

function RutaDashboard() {
    const { user } = useAuth();
    return user ? <DashboardPage /> : <Navigate to="/login" replace />;
}

function RutaDashboardIndex() {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" replace />;

    switch (user.rol) {
        case "Docente":
            return <Navigate to="/dashboard/docente" replace />;
        case "Estudiante":
            return <Navigate to="/dashboard/estudiante" replace />;
        case "Administrador":
            return <Navigate to="/dashboard/admin" replace />;
        default:
            return <Navigate to="/dashboard/docente" replace />;
    }
}

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<RutaLogin />} />
                <Route path="/registro" element={<RutaRegistro />} />
                <Route path="/cambiar-password" element={<RutaCambioPassword />} />
                <Route path="/dashboard" element={<RutaDashboard />}>
                    <Route index element={<RutaDashboardIndex />} />
                    <Route path="admin" element={<PortalAdmin />}>
                        <Route index element={null} />
                        <Route path="cursos" element={<AdminCursos />} />
                        <Route path="estudiantes" element={<AdminEstudiantes />} />
                        <Route path="profesores" element={<AdminProfesores />} />
                    </Route>
                    <Route path="docente" element={<PortalDocente />}>
                        <Route index element={null} />
                        <Route path="asistencia" element={<DocenteAsistencia />} />
                        <Route path="estudiantes" element={<DocenteEstudiantes />} />
                        <Route path="calificaciones" element={<DocenteCalificaciones />} />
                        <Route path="reportes" element={<DocenteReportes />} />
                    </Route>
                    <Route path="estudiante" element={<PortalEstudiantil />}>
                        <Route index element={null} />
                        <Route path="asistencia" element={<EstudianteAsistencia />} />
                        {/* "Mis Asignaturas" mostraba materias, docentes y notas
                            inventadas; su función real la cubre "calificaciones". */}
                        <Route path="asignaturas" element={<Navigate to="/dashboard/estudiante/calificaciones" replace />} />
                        <Route path="calificaciones" element={<EstudianteCalificaciones />} />
                        <Route path="perfil" element={<EstudiantePerfil />} />
                        <Route path="cambiar-password" element={<EstudianteCambioContrasena />} />
                    </Route>
                </Route>
                <Route path="*" element={<RutaLogin />} />
            </Routes>
        </BrowserRouter>
    );
}
