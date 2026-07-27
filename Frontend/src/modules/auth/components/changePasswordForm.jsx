import { useState } from "react";
import { cambiarPassword } from "../services/authService";

export default function ChangePasswordForm() {

    const [passwordAnterior, setPasswordAnterior] = useState("");
    const [passwordNueva, setPasswordNueva] = useState("");
    const [mensajeExito, setMensajeExito] = useState("");
    const [mensajeError, setMensajeError] = useState("");

    const handleSubmit = async (e) => {

        e.preventDefault();
        setMensajeExito("");
        setMensajeError("");

        try {

            await cambiarPassword({
                password_anterior: passwordAnterior,
                password_nueva: passwordNueva

            });

            setPasswordAnterior("");
            setPasswordNueva("");
            setMensajeExito("Contraseña actualizada correctamente.");

        } catch (error) {

            setMensajeError(error.detail || "No se pudo actualizar la contraseña.");

        }

    };

    return (

        <form
            className="login-form"
            onSubmit={handleSubmit}
        >

            <label>

                Contraseña actual

                <input
                    type="password"
                    value={passwordAnterior}
                    onChange={(e) => setPasswordAnterior(e.target.value)}
                    required
                />

            </label>

            <label>

                Nueva contraseña

                <input
                    type="password"
                    value={passwordNueva}
                    onChange={(e) => setPasswordNueva(e.target.value)}
                    required
                />

            </label>

            <button type="submit">

                Cambiar contraseña

            </button>

            {mensajeExito && (
                <p className="cal-success">{mensajeExito}</p>
            )}

            {mensajeError && (
                <p className="cal-error">{mensajeError}</p>
            )}

        </form>

    );

}