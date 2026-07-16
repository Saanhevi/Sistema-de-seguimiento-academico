import { useAuth } from "../../../context/AuthContext";

export default function Header() {

    const { user, logout } = useAuth();

    const iniciales =
        `${user?.nombres?.[0] ?? ""}${user?.apellidos?.[0] ?? ""}`;

    return (

        <header className="topbar">

            <div className="logo-area">

                <div className="logo-icon">

                    <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="white"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    >

                        <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>

                        <path d="M6 12v5c3 3 9 3 12 0v-5"/>

                    </svg>

                </div>

                <div className="logo-text">

                    <h1>Colegio San Andrés</h1>

                    <p>Portal Académico</p>

                </div>

            </div>

            <div className="topbar-right">

                <button
                    className="notif-btn"
                    aria-label="Notificaciones"
                >

                    <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#4A6060"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    >

                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>

                        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>

                    </svg>

                    <span className="dot"></span>

                </button>

                <div className="user-pill">

                    <div className="avatar">

                        {iniciales}

                    </div>

                    <div className="user-info">

                        <p>

                            {user.nombres} {user.apellidos}

                        </p>

                        <p>

                            {user.rol}

                        </p>

                    </div>

                </div>

                <button
                    className="logout-btn"
                    onClick={logout}
                >

                    Cerrar sesión

                </button>

            </div>

        </header>

    );

}