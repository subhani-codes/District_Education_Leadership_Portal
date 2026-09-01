import Link from 'next/link';
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Card from '../components/Card';
import { isLoggedIn, getUser } from '../lib/auth';

export default function Home() {
  const router = useRouter();

  // If the user is already signed in, send them to the right dashboard.
  useEffect(() => {
    if (isLoggedIn()) {
      const u = getUser();
      if (u?.role === 'hm') router.replace('/hm/dashboard');
      else if (u?.role === 'meo') router.replace('/meo/dashboard');
    }
  }, [router]);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-navy">
          Government School HM Performance Portal
        </h1>
        <p className="text-gray-600 mt-2">
          Track, verify, and rank Class 10 (SSC) performance at the mandal level.
        </p>
      </div>

      <Card title="Sign in to continue">
        <p className="text-sm text-gray-600 mb-4">
          Select your role to go to the login page.
        </p>
        <div className="grid sm:grid-cols-2 gap-4">
          <Link
            href="/login?role=hm"
            className="block border border-navy rounded-lg p-5 hover:bg-navy hover:text-white transition group"
          >
            <div className="font-semibold text-navy group-hover:text-white">
              Headmaster
            </div>
            <div className="text-sm text-gray-600 group-hover:text-white/90 mt-1">
              Submit Class 10 results, view your rank.
            </div>
          </Link>
          <Link
            href="/login?role=meo"
            className="block border border-saffron rounded-lg p-5 hover:bg-saffron hover:text-white transition group"
          >
            <div className="font-semibold text-saffron group-hover:text-white">
              Mandal Education Officer
            </div>
            <div className="text-sm text-gray-600 group-hover:text-white/90 mt-1">
              Review and verify school submissions.
            </div>
          </Link>
        </div>
        <div className="mt-4 text-sm">
          <Link href="/rankings" className="text-navy underline hover:no-underline">
            Browse the public rank board
          </Link>
        </div>
      </Card>
    </div>
  );
}
