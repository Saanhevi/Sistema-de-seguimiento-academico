import LoginForm from "../components/LoginForm";
import "../styles/login.css";

export default function LoginPage() {
    return (
        <div className="login-container">

            <div className="login-card">

                <div className="login-header">

                    <h1>Plataforma Académica</h1>

                    <p>
                        Inicia sesión para continuar
                    </p>

                </div>

                <LoginForm />

            </div>

        </div>
    );
}