import axios from "axios";
import { getStoredAuth } from "../utils/authStorage";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
    headers: {
        "Content-Type": "application/json"
    }
});

api.interceptors.request.use((config) => {
    const stored = getStoredAuth();
    if (stored?.token) {
        config.headers.Authorization = `Bearer ${stored.token}`;
    }
    return config;
});

export default api;
