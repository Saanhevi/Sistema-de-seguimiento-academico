import { createContext, useContext, useState } from "react";
import { getStoredAuth, setStoredAuth, clearStoredAuth } from "../utils/authStorage";
import { crearUsuario } from "../models/Usuario";

const AuthContext = createContext();

export function AuthProvider({ children }) {

    const stored = getStoredAuth();

    const [user, setUser] = useState(stored?.user ?? null);
    const [token, setToken] = useState(stored?.token ?? null);

    const login = ({ access_token, rol, nombres, apellidos, id_usuario }) => {
        const userData = crearUsuario({ rol, nombres, apellidos, id_usuario });
        setUser(userData);
        setToken(access_token);
        setStoredAuth({ user: userData, token: access_token });
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        clearStoredAuth();
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                login,
                logout
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth debe usarse dentro de <AuthProvider>");
    }
    return context;
}
