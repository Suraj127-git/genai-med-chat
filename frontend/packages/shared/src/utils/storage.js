const TOKEN_KEY = "token";

export function getToken() {
  try {
    const raw = localStorage.getItem(TOKEN_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return localStorage.getItem(TOKEN_KEY);
  }
}

export function setToken(token) {
  try {
    localStorage.setItem(TOKEN_KEY, JSON.stringify(token));
  } catch (e) {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getItem(key) {
  return localStorage.getItem(key);
}

export function setItem(key, value) {
  localStorage.setItem(key, value);
}

export function removeItem(key) {
  localStorage.removeItem(key);
}
