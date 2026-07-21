import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registrar } from "../services/authService";

export default function RegisterForm() {

    const [nombres, setNombres] = useState("");
    const [apellidos, setApellidos] = useState("");
    const [correo, setCorreo] = useState("");
    const [password, setPassword] = useState("");

    const  navigate = useNavigate()

    const handleSubmit = async (e) => {


        e.preventDefault();

        try {

            await registrar({

                nombres,
                apellidos,
                correo,
                password

            });

            alert("Cuenta creada correctamente.");

            setNombres("");
            setApellidos("");
            setCorreo("");
            setPassword("");

            navigate("/login")
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

                Nombres

                <input
                    type="text"
                    value={nombres}
                    onChange={(e) => setNombres(e.target.value)}
                    placeholder="Juan"
                    required
                />

            </label>

            <label>

                Apellidos

                <input
                    type="text"
                    value={apellidos}
                    onChange={(e) => setApellidos(e.target.value)}
                    placeholder="Pérez"
                    required
                />

            </label>

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

                Crear Cuenta

            </button>

        </form>

    );

}