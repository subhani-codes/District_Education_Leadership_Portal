// Thin fetch wrapper. Attaches the DRF token (if any) and parses JSON.
// All requests go through the Next.js rewrite to /api/* -> Django on :8000.

import { getToken, clearSession } from './auth';

async function request(method, path, body) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Token ${token}`;

  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const res = await fetch(`/api${normalizedPath}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401) {
    // Token rejected — wipe session so the UI can re-route to /login.
    clearSession();
  }

  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }

  if (!res.ok) {
    const message =
      (data && typeof data === 'object' && (data.error || data.detail)) ||
      `Request failed (${res.status})`;
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

export const api = {
  get:    (path)        => request('GET',    path),
  post:   (path, body)  => request('POST',   path, body),
  patch:  (path, body)  => request('PATCH',  path, body),
  put:    (path, body)  => request('PUT',    path, body),
  delete: (path)        => request('DELETE', path),
};
