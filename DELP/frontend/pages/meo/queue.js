import { useState } from 'react';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useRequireRole, useApi } from '../../lib/hooks';
import { api } from '../../lib/api';

export default function MEOQueue() {
  const { ready } = useRequireRole('meo');
  const { data, loading, error, setState } = useApi('/submissions/', [ready]);
  const [busyId, setBusyId]   = useState(null);
  const [comments, setComments] = useState({});   // submissionId -> comment text
  const [flash, setFlash]     = useState('');

  // The submissions endpoint returns everything the MEO can see; we filter client-side.
  const submissions = Array.isArray(data) ? data : data?.results || [];
  const pending = submissions.filter((s) => s.status === 'pending');
  const others  = submissions.filter((s) => s.status !== 'pending');

  async function decide(submission, status) {
    setBusyId(submission.id);
    setFlash('');
    try {
      await api.patch(`/submissions/${submission.id}`, {
        status,
        reviewer_comment: comments[submission.id] || '',
      });
      // Refresh the list
      const fresh = await api.get('/submissions');
      setState({ data: fresh, error: null, loading: false });
      setFlash(`Submission #${submission.id} ${status}.`);
    } catch (e) {
      setFlash(`Error: ${e.message}`);
    } finally {
      setBusyId(null);
    }
  }

  if (!ready || loading) return <p className="text-sm text-gray-600">Loading queue…</p>;
  if (error) return <Card title="Error"><p className="text-sm text-red-600">{error}</p></Card>;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-navy">Verification queue</h1>
        <p className="text-gray-600">{pending.length} pending submission{pending.length === 1 ? '' : 's'}.</p>
      </header>

      {flash && (
        <div className="text-sm text-gray-800 bg-gray-100 border border-line rounded px-3 py-2">
          {flash}
        </div>
      )}

      <Card title={`Pending (${pending.length})`}>
        {pending.length === 0 ? (
          <p className="text-sm text-gray-600">Nothing to review right now.</p>
        ) : (
          <div className="space-y-4">
            {pending.map((s) => (
              <div key={s.id} className="border border-line rounded-md p-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <div className="font-semibold text-navy">{s.school_name}</div>
                    <div className="text-xs text-gray-500">
                      {s.school_code} • AY {s.academic_year} • submitted {new Date(s.submitted_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="text-right text-sm">
                    <div>Appeared: <span className="font-semibold">{s.total_students_appeared}</span></div>
                    <div>≥ threshold: <span className="font-semibold">{s.students_meeting_threshold}</span></div>
                    <div>Qual %: <span className="font-semibold text-saffron">{s.qualifying_percentage}%</span></div>
                  </div>
                </div>

                {s.extra_credit_details && (
                  <div className="mt-2 text-sm text-gray-700">
                    <span className="font-medium">Extra credit:</span> {s.extra_credit_points} pts — {s.extra_credit_details}
                  </div>
                )}

                <div className="mt-3">
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Reviewer comment (optional for approve, recommended for reject)
                  </label>
                  <textarea
                    rows={2}
                    value={comments[s.id] || ''}
                    onChange={(e) => setComments((c) => ({ ...c, [s.id]: e.target.value }))}
                    className="w-full border border-line rounded-md px-3 py-2 text-sm"
                    placeholder="e.g. Verified against board gazette; figures match."
                  />
                </div>

                <div className="mt-3 flex gap-2">
                  <Button
                    onClick={() => decide(s, 'approved')}
                    disabled={busyId === s.id}
                  >
                    {busyId === s.id ? 'Saving…' : 'Approve'}
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => decide(s, 'rejected')}
                    disabled={busyId === s.id}
                  >
                    Reject
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card title={`Already processed (${others.length})`}>
        {others.length === 0 ? (
          <p className="text-sm text-gray-600">No history yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-600 border-b border-line">
                  <th className="py-2">School</th>
                  <th>Year</th>
                  <th>Qual %</th>
                  <th>Status</th>
                  <th>Reviewed</th>
                </tr>
              </thead>
              <tbody>
                {others.map((s) => (
                  <tr key={s.id} className="border-b border-line/60">
                    <td className="py-2">{s.school_name}</td>
                    <td>{s.academic_year}</td>
                    <td>{s.qualifying_percentage}%</td>
                    <td>{s.status}</td>
                    <td>{s.reviewed_at ? new Date(s.reviewed_at).toLocaleString() : '—'}</td>
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
