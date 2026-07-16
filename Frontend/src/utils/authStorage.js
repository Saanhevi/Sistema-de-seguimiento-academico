const AUTH_STORAGE_KEY = "auth";

export function getStoredAuth() {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
}

export function setStoredAuth(auth) {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
}

export function clearStoredAuth() {
    localStorage.removeItem(AUTH_STORAGE_KEY);
}
