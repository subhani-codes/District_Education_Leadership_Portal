import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { clearSession } from '../lib/auth';

// Defensive: an explicit /logout route that always wipes storage and goes home.
export default function LogoutPage() {
  const router = useRouter();
  useEffect(() => {
    clearSession();
    router.replace('/');
  }, [router]);
  return <p className="text-sm text-gray-600">Signing out…</p>;
}
