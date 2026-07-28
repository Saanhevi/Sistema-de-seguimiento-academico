import { useAuth } from "../../../context/AuthContext";
import { useEffect, useRef, useState } from "react";
import { listarAlertas } from "../../alertas/services/alertaService";

export default function Header() {

    const { user, logout } = useAuth();
    const [open, setOpen] = useState(false);
    const [alertas, setAlertas] = useState([]);
    const [loadingAlertas, setLoadingAlertas] = useState(false);
    const dropdownRef = useRef(null);

    const iniciales =
        `${user?.nombres?.[0] ?? ""}${user?.apellidos?.[0] ?? ""}`;

    useEffect(() => {
        if (!open) return;

        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [open]);

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

                    <h1>Colegio Lara Bonilla</h1>

                    <p>Portal Académico</p>

                </div>

            </div>

            <div className="topbar-right">

                <div ref={dropdownRef} style={{ position: 'relative' }}>
                <button
                    className="notif-btn"
                    aria-label="Notificaciones"
                    onClick={async () => {
                        setOpen(!open);
                        if (!open) {
                            setLoadingAlertas(true);
                            try {
                                const res = await listarAlertas({ estado: 'Pendiente' });
                                setAlertas(res || []);
                            } catch (err) {
                                console.error('Error cargando alertas', err);
                                setAlertas([]);
                            } finally {
                                setLoadingAlertas(false);
                            }
                        }
                    }}
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

                {open && (
                    <div className="alerts-dropdown" style={{ position: 'absolute', right: 0, top: '40px', width: '320px', background: 'white', boxShadow: '0 4px 12px rgba(0,0,0,0.12)', borderRadius: 6, zIndex: 40 }}>
                        <div style={{ padding: '8px 12px', borderBottom: '1px solid #eee', fontWeight: 600 }}>Alertas</div>
                        {loadingAlertas ? (
                            <div style={{ padding: 12 }}>Cargando...</div>
                        ) : alertas.length === 0 ? (
                            <div style={{ padding: 12 }}>No hay alertas</div>
                        ) : (
                            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
                                {alertas.map((a) => (
                                    <div key={a.id_alerta} style={{ padding: '10px 12px', borderBottom: '1px solid #f5f5f5', display: 'flex', gap: 8 }}>
                                        <div style={{ width: 10, height: 10, borderRadius: 6, marginTop: 6, background: a.nivel === 'Alto' ? 'var(--alert)' : a.nivel === 'Medio' ? 'orange' : '#ccc' }} />
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontSize: 13, fontWeight: 600 }}>{a.tipo}</div>
                                            {a.nombre_estudiante ? (
                                                <div style={{ fontSize: 12, color: '#555', marginBottom: 4 }}>
                                                    Estudiante: {a.nombre_estudiante}
                                                    {a.nombre_curso ? ` · Curso: ${a.nombre_curso}` : ''}
                                                </div>
                                            ) : null}
                                            <div style={{ fontSize: 13 }}>{a.mensaje}</div>
                                            <div style={{ fontSize: 12, color: '#666', marginTop: 6 }}>{new Date(a.fecha).toLocaleString()}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                </div>

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