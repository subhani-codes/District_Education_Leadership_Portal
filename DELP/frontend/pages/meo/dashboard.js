import Link from 'next/link';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useRequireRole, useApi } from '../../lib/hooks';

export default function MEODashboard() {
  const { ready } = useRequireRole('meo');
  const { data, error, loading } = useApi('/dashboard/meo/', [ready]);

  if (!ready || loading) return <p className="text-sm text-gray-600">Loading dashboard…</p>;
  if (error) {
    return (
      <Card title="Could not load dashboard">
        <p className="text-sm text-red-600">{error}</p>
        <p className="text-xs text-gray-600 mt-2">
          MEO logins must be linked to a Mandal. Use `python manage.py seed_pilot` if you don't have one.
        </p>
      </Card>
    );
  }

  const { meo, mandal_statistics, recent_approved_submissions, pending_submissions_count } = data;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-navy">
          MEO Dashboard — {meo?.mandal_name}
        </h1>
        <p className="text-gray-600">Employee ID: {meo?.employee_id}</p>
      </header>

      <div className="grid sm:grid-cols-4 gap-4">
        <Stat label="Schools in mandal" value={mandal_statistics.total_schools} />
        <Stat label="Headmasters" value={mandal_statistics.total_hms} />
        <Stat label="Pending verification" value={pending_submissions_count} accent="saffron" />
        <Stat label="Avg qualifying %" value={`${mandal_statistics.average_qualifying_percentage}%`} accent="navy" />
      </div>

      <Card
        title="Quick actions"
        action={
          <Link href="/meo/queue">
            <Button>Open verification queue</Button>
          </Link>
        }
      >
        <div className="flex flex-wrap gap-3">
          <Link href="/meo/queue"><Button variant="primary">Verify submissions</Button></Link>
          <Link href="/rankings"><Button variant="ghost">View mandal rank board</Button></Link>
        </div>
      </Card>

      <Card title="Recently approved">
        {recent_approved_submissions?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-600 border-b border-line">
                  <th className="py-2">School</th>
                  <th>Year</th>
                  <th>Qual %</th>
                  <th>Reviewed</th>
                </tr>
              </thead>
              <tbody>
                {recent_approved_submissions.map((s) => (
                  <tr key={s.id} className="border-b border-line/60">
                    <td className="py-2">{s.school_name}</td>
                    <td>{s.academic_year}</td>
                    <td>{s.qualifying_percentage}%</td>
                    <td>{s.reviewed_at ? new Date(s.reviewed_at).toLocaleDateString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-600">Nothing approved yet.</p>
        )}
      </Card>
    </div>
  );
}

function Stat({ label, value, accent }) {
  const color =
    accent === 'saffron' ? 'text-saffron' :
    accent === 'navy'    ? 'text-navy'    : 'text-gray-900';
  return (
    <Card>
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
      <div className={`text-3xl font-bold mt-1 ${color}`}>{value}</div>
    </Card>
  );
}
