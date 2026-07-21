import RegisterForm from "../components/RegisterForm";

export default function RegisterPage() {

    return (

        <div className="login-container">

            <div className="login-card">

                <div className="login-header">

                    <h1>Crear Cuenta</h1>

                    <p>
                        Registra una nueva cuenta de estudiante
                    </p>

                </div>

                <RegisterForm />

            </div>

        </div>

    );

}