import { useState } from 'react';
import Card from '../components/Card';
import { useRequireRole, useApi } from '../lib/hooks';

const CURRENT_YEAR = new Date().getFullYear();
const YEAR_OPTIONS = [String(CURRENT_YEAR), String(CURRENT_YEAR - 1), String(CURRENT_YEAR - 2)];

export default function Rankings() {
  const { ready, user } = useRequireRole(['hm', 'meo', 'admin', 'deo', 'state_official']);
  const [year, setYear] = useState(String(CURRENT_YEAR));
  const { data, loading, error } = useApi(`/rankings/?academic_year=${year}`, [ready, year]);

  if (!ready || loading) return <p className="text-sm text-gray-600">Loading rank board…</p>;
  if (error) return <Card title="Error"><p className="text-sm text-red-600">{error}</p></Card>;

  const rankingData = Array.isArray(data) ? data : data?.results || [];
  const rows = rankingData.slice().sort((a, b) => {
    const ra = a.mandal_rank ?? 9999;
    const rb = b.mandal_rank ?? 9999;
    return ra - rb;
  });

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-navy">Mandal rank board</h1>
          <p className="text-gray-600 text-sm">
            {user?.role === 'hm'
              ? 'Your school within the mandal.'
              : 'All schools in your mandal, ranked by qualifying %.'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Year</label>
          <select
            value={year}
            onChange={(e) => setYear(e.target.value)}
            className="border border-line rounded-md px-3 py-2 text-sm"
          >
            {YEAR_OPTIONS.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </header>

      <Card>
        {rows.length === 0 ? (
          <p className="text-sm text-gray-600">
            No approved rankings for {year} yet. MEOs need to approve submissions first.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-600 border-b border-line">
                  <th className="py-2 w-16">Rank</th>
                  <th>School</th>
                  <th>Code</th>
                  <th>Mandal</th>
                  <th>Qualifying %</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className="border-b border-line/60">
                    <td className="py-2 font-bold text-navy">
                      {r.mandal_rank ? `#${r.mandal_rank}` : '—'}
                    </td>
                    <td>{r.school_name}</td>
                    <td className="text-gray-600">{r.school_code}</td>
                    <td className="text-gray-600">{r.mandal_name}</td>
                    <td className="font-semibold text-saffron">{r.qualifying_percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
