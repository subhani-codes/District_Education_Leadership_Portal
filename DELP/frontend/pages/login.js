import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Card from '../components/Card';
import Button from '../components/Button';
import { api } from '../lib/api';
import { setSession, isLoggedIn, getUser } from '../lib/auth';

const ROLE_HOME = {
  hm: '/hm/dashboard',
  meo: '/meo/dashboard',
};

export default function LoginPage() {
  const router = useRouter();
  const hintRole = router.query.role; // optional ?role=hm | meo
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [busy, setBusy]         = useState(false);

  // If already logged in, bounce to the appropriate dashboard.
  useEffect(() => {
    if (isLoggedIn()) {
      const u = getUser();
      const dest = ROLE_HOME[u?.role] || '/';
      router.replace(dest);
    }
  }, [router]);

  async function onSubmit(e) {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const data = await api.post('/auth/login/', { email, password });
      setSession({ token: data.token, user: data });
      const dest = ROLE_HOME[data.role] || '/';
      router.push(dest);
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <Card title="Sign in">
        {hintRole && (
          <div className="mb-4 text-sm text-gray-600">
            Signing in as{' '}
            <span className="font-semibold text-navy">
              {hintRole === 'hm' ? 'Headmaster' : 'Mandal Education Officer'}
            </span>
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-line rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-navy"
              placeholder="hm1@pilot.test"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-line rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-navy"
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
              {error}
            </div>
          )}

          <Button type="submit" disabled={busy} className="w-full">
            {busy ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
