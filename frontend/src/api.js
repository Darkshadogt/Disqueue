import { API_BASE_URL } from "./config"

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(method, path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  const data = text ? JSON.parse(text) : undefined;

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem("token");
      // Already on the landing page — a reload there is enough to reset
      // any stale auth state. Anywhere else, send the user back to it
      // rather than reloading a page they're no longer authorized to see
      if (window.location.pathname === "/") {
        window.location.reload();
      } else {
        window.location.href = "/";
      }
    }

    const err = new Error(`Request failed: ${res.status}`);
    err.response = { status: res.status, data };
    throw err;
  }

  return { data, status: res.status };
}

const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  patch: (path, body) => request("PATCH", path, body),
  put: (path, body) => request("PUT", path, body),
  delete: (path) => request("DELETE", path),
};

export default api;