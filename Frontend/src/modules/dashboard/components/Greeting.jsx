import { useAuth } from "../../../context/AuthContext";

export default function Greeting() {

    const { user } = useAuth();

    const hora = new Date().getHours();

    let saludo = "Buenos días";

    if (hora >= 12 && hora < 18) {

        saludo = "Buenas tardes";

    } else if (hora >= 18) {

        saludo = "Buenas noches";

    }

    return (

        <div className="greeting">

            <h2>

                {saludo}, {user.nombres}

            </h2>

            <p>

                {new Date().toLocaleDateString("es-CO", {

                    weekday: "long",

                    day: "numeric",

                    month: "long",

                    year: "numeric"

                })}

            </p>

        </div>

    );

}