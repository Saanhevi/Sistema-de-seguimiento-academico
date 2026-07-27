import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registrar } from "../services/authService";

export default function RegisterForm() {

    const [nombres, setNombres] = useState("");
    const [apellidos, setApellidos] = useState("");
    const [correo, setCorreo] = useState("");
    // HU22: el documento es la clave con la que un docente empareja su propia
    // planilla de Excel con los estudiantes del sistema.
    const [documento, setDocumento] = useState("");
    const [password, setPassword] = useState("");

    const  navigate = useNavigate()

    const handleSubmit = async (e) => {


        e.preventDefault();

        try {

            await registrar({

                nombres,
                apellidos,
                correo,
                documento,
                password

            });

            alert("Cuenta creada correctamente.");

            setNombres("");
            setApellidos("");
            setCorreo("");
            setDocumento("");
            setPassword("");

            navigate("/login")
        } catch (error) {

            // Un 422 de Pydantic manda `detail` como lista de errores, no como
            // texto: sin este aplanado el alert muestra "[object Object]".
            const detalle = Array.isArray(error.detail)
                ? error.detail.map((item) => item.msg).join(" · ")
                : error.detail;

            alert(detalle || "No se pudo crear la cuenta");

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

                Número de documento

                <input
                    type="text"
                    value={documento}
                    onChange={(e) => setDocumento(e.target.value)}
                    placeholder="1023456789"
                    minLength={5}
                    maxLength={20}
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