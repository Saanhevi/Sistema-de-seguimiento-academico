import { useState } from "react";
import { cambiarPassword } from "../services/authService";
import { useNavigate } from "react-router-dom";

export default function ChangePasswordForm() {

    const [correo, setCorreo] = useState("");
    const [passwordAnterior, setPasswordAnterior] = useState("");
    const [passwordNueva, setPasswordNueva] = useState("");

    const navigate = useNavigate();

    const handleSubmit = async (e) => {

        e.preventDefault();

        try {

            await cambiarPassword({

                correo,
                password_anterior: passwordAnterior,
                password_nueva: passwordNueva

            });

            alert("Contraseña actualizada correctamente.");

            navigate("/login");

        } catch (error) {

            alert(error.detail);

        }

    };

    return (

        <form
            className="login-form"
            onSubmit={handleSubmit}
        >

            <label>

                Correo electrónico

                <input
                    type="email"
                    value={correo}
                    onChange={(e) => setCorreo(e.target.value)}
                    required
                />

            </label>

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

        </form>

    );

}