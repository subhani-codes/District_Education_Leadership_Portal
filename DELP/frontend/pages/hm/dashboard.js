import Link from 'next/link';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useRequireRole, useApi } from '../../lib/hooks';

export default function HMDashboard() {
  const { ready } = useRequireRole('hm');
  const { data, error, loading } = useApi('/dashboard/hm/', [ready]);

  if (!ready || loading) {
    return <p className="text-sm text-gray-600">Loading dashboard…</p>;
  }
  if (error) {
    return (
      <Card title="Could not load dashboard">
        <p className="text-sm text-red-600">{error}</p>
        <p className="text-xs text-gray-600 mt-2">
          Make sure your account has a Headmaster profile (HM logins must be linked to a school).
        </p>
      </Card>
    );
  }

  const { headmaster, recent_submissions, current_ranking, statistics } = data;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-navy">
          Welcome, {headmaster?.user?.name || 'Headmaster'}
        </h1>
        <p className="text-gray-600">
          {headmaster?.school_name} <span className="text-gray-400">({headmaster?.school_code})</span>
        </p>
      </header>

      <div className="grid sm:grid-cols-3 gap-4">
        <Card title="Current rank">
          {current_ranking?.mandal_rank ? (
            <div>
              <div className="text-4xl font-bold text-navy">#{current_ranking.mandal_rank}</div>
              <div className="text-sm text-gray-600 mt-1">
                in {current_ranking.mandal_name} • AY {current_ranking.academic_year}
              </div>
              <div className="text-xs text-gray-500 mt-2">
                Qualifying %: <span className="font-semibold text-saffron">
                  {current_ranking.qualifying_percentage}%
                </span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-600">
              No approved ranking yet. Submit results to appear on the board.
            </p>
          )}
        </Card>

        <Card title="Submissions">
          <div className="space-y-1 text-sm">
            <div>Total: <span className="font-semibold">{statistics.total_submissions}</span></div>
            <div>Approved: <span className="font-semibold text-green-700">{statistics.approved_submissions}</span></div>
            <div>Pending: <span className="font-semibold text-saffron">{statistics.pending_submissions}</span></div>
          </div>
        </Card>

        <Card title="Quick actions">
          <div className="flex flex-col gap-2">
            <Link href="/hm/submit"><Button>Submit Class 10 results</Button></Link>
            <Link href="/rankings"><Button variant="ghost">View mandal rank board</Button></Link>
          </div>
        </Card>
      </div>

      <Card title="Recent submissions">
        {recent_submissions?.length ? (
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
                {recent_submissions.map((s) => (
                  <tr key={s.id} className="border-b border-line/60">
                    <td className="py-2">{s.academic_year}</td>
                    <td>{s.total_students_appeared}</td>
                    <td>{s.students_meeting_threshold}</td>
                    <td>{s.qualifying_percentage}%</td>
                    <td>
                      <StatusPill status={s.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-600">No submissions yet.</p>
        )}
      </Card>
    </div>
  );
}

function StatusPill({ status }) {
  const styles = {
    approved: 'bg-green-100 text-green-800',
    pending:  'bg-amber-100 text-amber-800',
    rejected: 'bg-red-100 text-red-800',
  };
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
      {status}
    </span>
  );
}
