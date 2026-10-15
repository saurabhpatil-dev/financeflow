import { useEffect, useState } from 'react';
import { User as UserIcon, Mail, Lock, Save } from 'lucide-react';
import toast from 'react-hot-toast';
import { usersApi, extractError } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { formatDate } from '../utils/format';

export function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [savingProfile, setSavingProfile] = useState(false);
  const [pw, setPw] = useState({ current: '', next: '', confirm: '' });
  const [savingPw, setSavingPw] = useState(false);
  const [loading, setLoading] = useState(!user);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      usersApi
        .getMe()
        .then((u) => {
          setName(u.name);
          setEmail(u.email);
        })
        .catch((err) => setError(extractError(err)))
        .finally(() => setLoading(false));
    }
  }, [user]);

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      await usersApi.updateMe({ name, email });
      await refreshUser();
      toast.success('Profile updated');
    } catch (err) {
      toast.error(extractError(err, 'Update failed'));
    } finally {
      setSavingProfile(false);
    }
  };

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pw.next !== pw.confirm) {
      toast.error('Passwords do not match');
      return;
    }
    if (pw.next.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setSavingPw(true);
    try {
      await usersApi.changePassword({
        current_password: pw.current,
        new_password: pw.next,
        new_password_confirm: pw.confirm,
      });
      toast.success('Password changed');
      setPw({ current: '', next: '', confirm: '' });
    } catch (err) {
      toast.error(extractError(err, 'Change failed'));
    } finally {
      setSavingPw(false);
    }
  };

  if (loading) return <PageSpinner />;
  if (error || !user) return <ErrorState message={error || 'No user'} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile & Settings</h1>
        <p className="mt-1 text-sm text-slate-500">Manage your account information and password.</p>
      </div>

      <div className="card p-6">
        <div className="mb-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 text-2xl font-bold text-brand-700 dark:bg-brand-950 dark:text-brand-300">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="text-lg font-semibold">{user.name}</p>
            <p className="text-sm text-slate-500">{user.email}</p>
            <p className="mt-1 text-xs text-slate-400">Member since {formatDate(user.created_at)}</p>
          </div>
        </div>

        <form onSubmit={saveProfile} className="space-y-4">
          <h2 className="flex items-center gap-2 text-base font-semibold">
            <UserIcon className="h-4 w-4" /> Profile
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="name">Full name</label>
              <input
                id="name"
                className="input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="label" htmlFor="email">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  id="email"
                  type="email"
                  className="input pl-9"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>
          </div>
          <button type="submit" className="btn-primary" disabled={savingProfile}>
            <Save className="h-4 w-4" /> {savingProfile ? 'Saving…' : 'Save changes'}
          </button>
        </form>
      </div>

      <div className="card p-6">
        <form onSubmit={changePassword} className="space-y-4">
          <h2 className="flex items-center gap-2 text-base font-semibold">
            <Lock className="h-4 w-4" /> Change password
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label className="label" htmlFor="cur">Current password</label>
              <input
                id="cur"
                type="password"
                className="input"
                value={pw.current}
                onChange={(e) => setPw((p) => ({ ...p, current: e.target.value }))}
                required
                minLength={8}
                autoComplete="current-password"
              />
            </div>
            <div>
              <label className="label" htmlFor="new">New password</label>
              <input
                id="new"
                type="password"
                className="input"
                value={pw.next}
                onChange={(e) => setPw((p) => ({ ...p, next: e.target.value }))}
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>
            <div>
              <label className="label" htmlFor="conf">Confirm new password</label>
              <input
                id="conf"
                type="password"
                className="input"
                value={pw.confirm}
                onChange={(e) => setPw((p) => ({ ...p, confirm: e.target.value }))}
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>
          </div>
          <button type="submit" className="btn-primary" disabled={savingPw}>
            <Lock className="h-4 w-4" /> {savingPw ? 'Changing…' : 'Change password'}
          </button>
        </form>
      </div>
    </div>
  );
}
