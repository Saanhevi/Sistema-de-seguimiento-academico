import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import LoginPage from "../modules/auth/pages/LoginPage";
import DashboardPage from "../modules/dashboard/pages/DashboardPage";

function RutaLogin() {
    const { user } = useAuth();
    return user ? <Navigate to="/dashboard" replace /> : <LoginPage />;
}

function RutaDashboard() {
    const { user } = useAuth();
    return user ? <DashboardPage /> : <Navigate to="/login" replace />;
}

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<RutaLogin />} />
                <Route path="/dashboard" element={<RutaDashboard />} />
                <Route path="*" element={<RutaDashboard />} />
            </Routes>
        </BrowserRouter>
    );
}
