import { useEffect, useState } from 'react';
import Card from '../../components/Card';
import { useRequireRole, useApi } from '../../lib/hooks';
import { api } from '../../lib/api';

// Dynamic-import recharts so SSR doesn't blow up (it touches `window`).
import dynamic from 'next/dynamic';
const LineChart = dynamic(() => import('recharts').then((m) => m.LineChart), { ssr: false });
const Line      = dynamic(() => import('recharts').then((m) => m.Line),      { ssr: false });
const XAxis     = dynamic(() => import('recharts').then((m) => m.XAxis),     { ssr: false });
const YAxis     = dynamic(() => import('recharts').then((m) => m.YAxis),     { ssr: false });
const Tooltip   = dynamic(() => import('recharts').then((m) => m.Tooltip),   { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then((m) => m.CartesianGrid), { ssr: false });
const ResponsiveContainer = dynamic(() => import('recharts').then((m) => m.ResponsiveContainer), { ssr: false });

export default function HMPerformance() {
  const { ready } = useRequireRole('hm');
  const { data: subs, loading } = useApi('/submissions/', [ready]);

  const submissions = Array.isArray(subs) ? subs : subs?.results || [];

  // Build year-by-year trend from approved submissions
  const trend = submissions
    .filter((s) => s.status === 'approved')
    .map((s) => ({ year: s.academic_year, qualifying_percentage: Number(s.qualifying_percentage) || 0 }))
    .sort((a, b) => a.year.localeCompare(b.year));

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-navy">Performance trend</h1>

      <Card title="Qualifying % by year">
        {!ready || loading ? (
          <p className="text-sm text-gray-600">Loading…</p>
        ) : trend.length === 0 ? (
          <p className="text-sm text-gray-600">
            No approved submissions yet. Once the MEO approves your results, your trend will appear here.
          </p>
        ) : (
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={trend} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis domain={[0, 100]} unit="%" />
                <Tooltip />
                <Line type="monotone" dataKey="qualifying_percentage" stroke="#0B3D91" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      <Card title="All my submissions">
        {!ready || loading ? (
          <p className="text-sm text-gray-600">Loading…</p>
        ) : !submissions.length ? (
          <p className="text-sm text-gray-600">No submissions yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-600 border-b border-line">
                  <th className="py-2">Year</th>
                  <th>Appeared</th>
                  <th>≥ threshold</th>
                  <th>Qual %</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((s) => (
                  <tr key={s.id} className="border-b border-line/60">
                    <td className="py-2">{s.academic_year}</td>
                    <td>{s.total_students_appeared}</td>
                    <td>{s.students_meeting_threshold}</td>
                    <td>{s.qualifying_percentage}%</td>
                    <td>{s.status}</td>
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
