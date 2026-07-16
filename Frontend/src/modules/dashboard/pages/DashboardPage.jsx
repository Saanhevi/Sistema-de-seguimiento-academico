import { useAuth } from "../../../context/AuthContext";

import Header from "../components/Header";
import Navbar from "../components/Navbar";
import PortalDocente from "./PortalDocente";
import PortalEstudiantil from "./PortalEstudiantil";

export default function DashboardPage() {

    const { user } = useAuth();
    const isDocente = user?.rol === "Docente";

    return (

        <>

            <Header />

            <Navbar />

            {isDocente ? <PortalDocente /> : <PortalEstudiantil />}

        </>

    );

}