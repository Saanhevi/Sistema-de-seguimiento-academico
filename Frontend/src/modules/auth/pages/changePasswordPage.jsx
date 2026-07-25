// El archivo en disco es changePasswordForm.jsx (c minúscula): con la mayúscula
// el build funcionaba en Windows/macOS pero fallaba en Linux, que sí distingue.
import ChangePasswordForm from "../components/changePasswordForm";

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