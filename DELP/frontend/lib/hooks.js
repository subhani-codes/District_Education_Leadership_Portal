// Hooks shared by role-gated pages.
//
// useRequireRole(roles) — gate a page on a logged-in user having one of `roles`.
//   Redirects to /login if missing, or to that role's home if mismatched.
//   Returns { ready, user, token }.
//
// useApi(path, deps) — fetch + parse JSON, returning { data, error, loading }.

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { isLoggedIn, getUser, getToken } from './auth';
import { api } from './api';

export function useRequireRole(roles) {
  const router = useRouter();
  const allowed = Array.isArray(roles) ? roles : [roles];
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!isLoggedIn()) {
      router.replace('/login');
      return;
    }
    const u = getUser();
    if (u && !allowed.includes(u.role)) {
      if (u.role === 'hm') router.replace('/hm/dashboard');
      else if (u.role === 'meo') router.replace('/meo/dashboard');
      else router.replace('/');
      return;
    }
    setReady(true);
  }, [router, allowed.join(',')]);

  return { ready, token: getToken(), user: getUser() };
}

export function useApi(path, deps = []) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  useEffect(() => {
    let cancelled = false;
    setState({ data: null, error: null, loading: true });
    api.get(path)
      .then((data) => { if (!cancelled) setState({ data, error: null, loading: false }); })
      .catch((err) => { if (!cancelled) setState({ data: null, error: err.message, loading: false }); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return { ...state, setState };
}
