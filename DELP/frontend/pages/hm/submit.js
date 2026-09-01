import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useRequireRole, useApi } from '../../lib/hooks';
import { api } from '../../lib/api';

const CURRENT_YEAR = new Date().getFullYear();
const YEAR_OPTIONS = [String(CURRENT_YEAR), String(CURRENT_YEAR - 1), String(CURRENT_YEAR - 2)];

export default function HMSubmit() {
  const { ready } = useRequireRole('hm');
  const router = useRouter();
  const { data: dashData } = useApi('/dashboard/hm/', [ready]);

  const [form, setForm] = useState({
    school: '',
    academic_year: String(CURRENT_YEAR),
    total_students_appeared: '',
    students_meeting_threshold: '',
    threshold_value: 500,
    extra_credit_points: 0,
    extra_credit_details: '',
  });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [ok,  setOk]  = useState('');

  // Pre-fill the school once we know the HM's profile
  useEffect(() => {
    if (dashData?.headmaster?.school) {
      setForm((f) => ({ ...f, school: dashData.headmaster.school }));
    }
  }, [dashData]);

  function update(k, v) { setForm((f) => ({ ...f, [k]: v })); }

  async function onSubmit(e) {
    e.preventDefault();
    setErr(''); setOk(''); setBusy(true);
    try {
      const payload = {
        school: Number(form.school),
        academic_year: form.academic_year,
        total_students_appeared: Number(form.total_students_appeared),
        students_meeting_threshold: Number(form.students_meeting_threshold),
        threshold_value: Number(form.threshold_value),
        extra_credit_points: Number(form.extra_credit_points || 0),
        extra_credit_details: form.extra_credit_details,
      };
      await api.post('/submissions/', payload);
      setOk('Submission saved. The MEO will review and approve it.');
      setTimeout(() => router.push('/hm/dashboard'), 800);
    } catch (e2) {
      setErr(e2.message || 'Submission failed');
    } finally {
      setBusy(false);
    }
  }

  if (!ready) return <p className="text-sm text-gray-600">Loading…</p>;

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold text-navy">Submit Class 10 results</h1>

      <Card>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">School</label>
            <input
              value={dashData?.headmaster?.school_name || ''}
              disabled
              className="w-full border border-line rounded-md px-3 py-2 bg-gray-50 text-gray-700"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Academic year</label>
            <select
              value={form.academic_year}
              onChange={(e) => update('academic_year', e.target.value)}
              className="w-full border border-line rounded-md px-3 py-2"
            >
              {YEAR_OPTIONS.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Total students appeared</label>
              <input
                type="number" min="1" required
                value={form.total_students_appeared}
                onChange={(e) => update('total_students_appeared', e.target.value)}
                className="w-full border border-line rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Students meeting threshold</label>
              <input
                type="number" min="0" required
                value={form.students_meeting_threshold}
                onChange={(e) => update('students_meeting_threshold', e.target.value)}
                className="w-full border border-line rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Threshold value (e.g. 500/600)</label>
              <input
                type="number" min="0" required
                value={form.threshold_value}
                onChange={(e) => update('threshold_value', e.target.value)}
                className="w-full border border-line rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Extra credit points</label>
              <input
                type="number" min="0"
                value={form.extra_credit_points}
                onChange={(e) => update('extra_credit_points', e.target.value)}
                className="w-full border border-line rounded-md px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Extra credit details (optional)</label>
            <textarea
              rows={3}
              value={form.extra_credit_details}
              onChange={(e) => update('extra_credit_details', e.target.value)}
              className="w-full border border-line rounded-md px-3 py-2"
              placeholder="Sports medals, science fair wins, etc."
            />
          </div>

          {err && <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded px-3 py-2">{err}</div>}
          {ok  && <div className="text-sm text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">{ok}</div>}

          <Button type="submit" disabled={busy} className="w-full">
            {busy ? 'Submitting…' : 'Submit for verification'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
