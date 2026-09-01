import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { getUser, clearSession } from '@/lib/auth';

const ROLE_LABELS = {
  hm: 'Headmaster',
  meo: 'Mandal Education Officer',
  deo: 'District Education Officer',
  state_official: 'State Official',
  admin: 'Platform Admin',
};

function NavLink({ href, active, children }) {
  return (
    <Link
      href={href}
      className={`px-2 py-1 rounded text-sm hover:bg-white/10 ${
        active ? 'bg-white/15 font-semibold' : 'text-white/85'
      }`}
    >
      {children}
    </Link>
  );
}

export default function Layout({ children }) {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    setUser(getUser());
  }, []);

  function handleLogout() {
    clearSession();
    router.push('/');
  }

  // Active-link helper
  const isActive = (href) => router.pathname === href || router.pathname.startsWith(href + '/');

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-navy text-white">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="inline-block w-2 h-6 bg-saffron rounded-sm" />
            <span className="font-semibold tracking-wide">
              District Education Leadership Portal
            </span>
          </Link>

          {user && (
            <nav className="hidden md:flex items-center gap-1">
              {user.role === 'hm' && (
                <>
                  <NavLink href="/hm/dashboard"    active={isActive('/hm/dashboard')}>Dashboard</NavLink>
                  <NavLink href="/hm/submit"       active={isActive('/hm/submit')}>Submit</NavLink>
                  <NavLink href="/hm/performance"  active={isActive('/hm/performance')}>Performance</NavLink>
                  <NavLink href="/rankings"        active={isActive('/rankings')}>Rank board</NavLink>
                </>
              )}
              {user.role === 'meo' && (
                <>
                  <NavLink href="/meo/dashboard"   active={isActive('/meo/dashboard')}>Dashboard</NavLink>
                  <NavLink href="/meo/queue"       active={isActive('/meo/queue')}>Queue</NavLink>
                  <NavLink href="/rankings"        active={isActive('/rankings')}>Rank board</NavLink>
                </>
              )}
              {user.role !== 'hm' && user.role !== 'meo' && (
                <NavLink href="/rankings" active={isActive('/rankings')}>Rank board</NavLink>
              )}
            </nav>
          )}

          {user && (
            <div className="flex items-center gap-4 text-sm">
              <span className="hidden sm:inline">
                {user.name || user.email}
                <span className="ml-2 px-2 py-0.5 rounded bg-saffron/90 text-white text-xs">
                  {ROLE_LABELS[user.role] || user.role}
                </span>
              </span>
              <button
                onClick={handleLogout}
                className="underline hover:no-underline"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
        {children}
      </main>

      <footer className="border-t border-line bg-white">
        <div className="max-w-6xl mx-auto px-6 py-3 text-xs text-gray-500">
          District Education Leadership Portal — Phase 1 MVP
        </div>
      </footer>
    </div>
  );
}

