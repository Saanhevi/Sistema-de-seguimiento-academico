import { useState } from "react";
import { login } from "../services/authService";
import { useAuth } from "../../../context/AuthContext";

export default function LoginForm() {

    const [correo, setCorreo] = useState("");
    const [password, setPassword] = useState("");

    const { login: authLogin } = useAuth();

    const handleSubmit = async (e) => {

        e.preventDefault();

        try {

            const response = await login({

                correo,
                password

            });

            if (import.meta.env.DEV) console.log(response);

            authLogin(response.user);

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
                    placeholder="correo@colegio.com"
                    required
                />

            </label>

            <label>

                Contraseña

                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="********"
                    required
                />

            </label>

            <button type="submit">

                Iniciar Sesión

            </button>

        </form>

    );

}