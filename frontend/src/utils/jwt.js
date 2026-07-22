/**
 * Decodes a JWT payload without verifying the signature. This is safe
 * for reading claims client-side (e.g. user id, expiry) but must never
 * be trusted as proof of authenticity — the backend is the source of
 * truth for that
 */
export function decodeJwt(token) {
  try {
    const payload = token.split(".")[1];
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function getCurrentUserId() {
  const token = localStorage.getItem("token");
  if (!token) return null;
  const payload = decodeJwt(token);
  return payload?.sub ?? null;
}

export function isTokenExpired(token) {
  const payload = decodeJwt(token);
  if (!payload?.exp) return true;
  return Date.now() >= payload.exp * 1000;
}

export function isLoggedIn() {
  const token = localStorage.getItem("token");
  return !!token && !isTokenExpired(token);
}