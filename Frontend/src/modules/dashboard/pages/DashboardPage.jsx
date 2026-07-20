//import { useAuth } from "../../../context/AuthContext";

import Header from "../components/Header";
import Navbar from "../components/Navbar";
import { Outlet } from "react-router-dom";

export default function DashboardPage() {
    return (
        <>
            <Header />
            <Navbar />

            <main>
                <Outlet />
            </main>
        </>
    );
}