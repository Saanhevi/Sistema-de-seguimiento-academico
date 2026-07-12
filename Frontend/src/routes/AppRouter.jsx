import { useAuth } from "../context/AuthContext";

import LoginPage from "../modules/auth/pages/LoginPage";

import DashboardPage from "../modules/dashboard/pages/DashboardPage";

export default function AppRouter() {

    const { user } = useAuth();

    if (!user) {

        return <LoginPage />;

    }

    return <DashboardPage />;

}