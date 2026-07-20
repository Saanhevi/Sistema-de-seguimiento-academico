import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import LoginPage from "../modules/auth/pages/LoginPage";
import DashboardPage from "../modules/dashboard/pages/DashboardPage";
import PortalAdmin from "../modules/dashboard/pages/admin/PortalAdmin";
import { AdminCursos } from "../modules/dashboard/pages/admin/AdminCursos";
import AdminEstudiantes from "../modules/dashboard/pages/admin/AdminEstudiantes";
import { AdminProfesores } from "../modules/dashboard/pages/admin/AdminProfesores";
import PortalDocente from "../modules/dashboard/pages/docente/PortalDocente";
import DocenteAsistencia from "../modules/dashboard/pages/docente/DocenteAsistencia";
import DocenteCalificaciones from "../modules/dashboard/pages/docente/DocenteCalificaciones";
import DocenteReportes from "../modules/dashboard/pages/docente/DocenteReportes";
import PortalEstudiantil from "../modules/dashboard/pages/estudiante/PortalEstudiantil";
import EstudianteAsistencia from "../modules/dashboard/pages/estudiante/EstudianteAsistencia";
import EstudiantePerfil from "../modules/dashboard/pages/estudiante/EstudiantePerfil";
import EstudianteAsignaturas from "../modules/dashboard/pages/estudiante/EstudianteAsignaturas";


function RutaLogin() {
    const { user } = useAuth();
    return user ? <Navigate to="/dashboard" replace /> : <LoginPage />;
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
                        <Route path="calificaciones" element={<DocenteCalificaciones />} />
                        <Route path="reportes" element={<DocenteReportes />} />
                    </Route>
                    <Route path="estudiante" element={<PortalEstudiantil />}>
                        <Route index element={null} />
                        <Route path="asistencia" element={<EstudianteAsistencia />} />
                        <Route path="asignaturas" element={<EstudianteAsignaturas />} />
                        <Route path="perfil" element={<EstudiantePerfil />} />
                    </Route>
                </Route>
                <Route path="*" element={<RutaLogin />} />
            </Routes>
        </BrowserRouter>
    );
}
