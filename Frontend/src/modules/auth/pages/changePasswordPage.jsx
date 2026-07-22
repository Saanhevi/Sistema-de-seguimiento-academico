import ChangePasswordForm from "../components/ChangePasswordForm";

export default function ChangePasswordPage() {

    return (

        <div className="login-container">

            <div className="login-card">

                <div className="login-header">

                    <h1>Cambiar Contraseña</h1>

                    <p>
                        Actualiza la contraseña de tu cuenta
                    </p>

                </div>

                <ChangePasswordForm />

            </div>

        </div>

    );

}