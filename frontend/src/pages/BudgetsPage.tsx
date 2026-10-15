import { useEffect, useState, useCallback } from 'react';
import { Plus, Pencil, Trash2, Wallet, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { budgetsApi, categoriesApi, extractError } from '../api/client';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { ConfirmDialog } from '../components/ui/ConfirmDialog';
import { cn, formatCurrency, monthLabel } from '../utils/format';
import type { BudgetWithProgress, Category } from '../types';

interface FormState {
  category_id: string;
  year: string;
  month: string;
  amount: string;
}

const now = new Date();

export function BudgetsPage() {
  const [items, setItems] = useState<BudgetWithProgress[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<BudgetWithProgress | null>(null);
  const [form, setForm] = useState<FormState>({
    category_id: '',
    year: String(now.getFullYear()),
    month: String(now.getMonth() + 1),
    amount: '',
  });
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<BudgetWithProgress | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError('');
    budgetsApi
      .list()
      .then(setItems)
      .catch((err) => setError(extractError(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  useEffect(() => {
    categoriesApi.list('expense').then(setCategories).catch(() => {});
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({
      category_id: categories[0] ? String(categories[0].id) : '',
      year: String(now.getFullYear()),
      month: String(now.getMonth() + 1),
      amount: '',
    });
    setModalOpen(true);
  };

  const openEdit = (b: BudgetWithProgress) => {
    setEditing(b);
    setForm({
      category_id: String(b.category_id),
      year: String(b.year),
      month: String(b.month),
      amount: b.amount,
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.category_id) {
      toast.error('Select a category');
      return;
    }
    if (!form.amount || parseFloat(form.amount) <= 0) {
      toast.error('Enter a valid amount');
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        await budgetsApi.update(editing.id, { amount: form.amount });
        toast.success('Budget updated');
      } else {
        await budgetsApi.create({
          category_id: Number(form.category_id),
          year: Number(form.year),
          month: Number(form.month),
          amount: form.amount,
        });
        toast.success('Budget created');
      }
      setModalOpen(false);
      load();
    } catch (err) {
      toast.error(extractError(err, 'Save failed'));
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await budgetsApi.delete(deleteTarget.id);
      toast.success('Budget deleted');
      setDeleteTarget(null);
      load();
    } catch (err) {
      toast.error(extractError(err, 'Delete failed'));
    } finally {
      setDeleting(false);
    }
  };

  const statusVariant = (status: BudgetWithProgress['status']) =>
    status === 'exceeded' ? 'red' : status === 'warning' ? 'amber' : 'green';

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Budgets</h1>
          <p className="mt-1 text-sm text-slate-500">Set monthly spending limits per category.</p>
        </div>
        <button className="btn-primary" onClick={openCreate}>
          <Plus className="h-4 w-4" /> New budget
        </button>
      </div>

      {loading ? (
        <PageSpinner />
      ) : error ? (
        <ErrorState message={error} onRetry={load} />
      ) : items.length === 0 ? (
        <EmptyState
          title="No budgets yet"
          description="Create a budget to track your spending against a limit."
          action={
            <button className="btn-primary" onClick={openCreate}>
              <Plus className="h-4 w-4" /> New budget
            </button>
          }
          icon={<Wallet className="h-7 w-7" />}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {items.map((b) => {
            const pct = b.percent_used;
            const barColor = b.status === 'exceeded' ? 'bg-red-500' : b.status === 'warning' ? 'bg-amber-500' : 'bg-green-500';
            return (
              <div key={b.id} className="card p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-100">{b.category_name}</p>
                    <p className="text-xs text-slate-400">{monthLabel(b.year, b.month)}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <button className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => openEdit(b)} aria-label="Edit">
                      <Pencil className="h-4 w-4" />
                    </button>
                    <button className="rounded-lg p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-950" onClick={() => setDeleteTarget(b)} aria-label="Delete">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="flex items-end justify-between text-sm">
                    <span className="text-slate-500">
                      {formatCurrency(b.spent)} spent
                    </span>
                    <span className="font-semibold">{formatCurrency(b.amount)}</span>
                  </div>
                  <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                    <div className={cn('h-full rounded-full transition-all', barColor)} style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <Badge variant={statusVariant(b.status)}>
                      {b.status === 'exceeded' && <AlertTriangle className="mr-1 h-3 w-3" />}
                      {pct.toFixed(0)}% used
                    </Badge>
                    <span className={cn('font-medium', parseFloat(b.remaining) < 0 ? 'text-red-600' : 'text-slate-500')}>
                      {parseFloat(b.remaining) < 0 ? `${formatCurrency(Math.abs(parseFloat(b.remaining)))} over` : `${formatCurrency(b.remaining)} left`}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit budget' : 'New budget'}
        footer={
          <>
            <button className="btn-secondary" onClick={() => setModalOpen(false)} disabled={saving}>
              Cancel
            </button>
            <button className="btn-primary" form="budget-form" type="submit" disabled={saving}>
              {saving ? 'Saving…' : editing ? 'Save' : 'Create'}
            </button>
          </>
        }
      >
        <form id="budget-form" onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Category</label>
            <select
              className="input"
              value={form.category_id}
              onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
              disabled={!!editing}
            >
              <option value="">Select a category…</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Year</label>
              <select
                className="input"
                value={form.year}
                onChange={(e) => setForm((f) => ({ ...f, year: e.target.value }))}
                disabled={!!editing}
              >
                {[now.getFullYear() - 1, now.getFullYear(), now.getFullYear() + 1].map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Month</label>
              <select
                className="input"
                value={form.month}
                onChange={(e) => setForm((f) => ({ ...f, month: e.target.value }))}
                disabled={!!editing}
              >
                {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                  <option key={m} value={m}>
                    {monthLabel(2000, m).split(' ')[0]}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="label">Budget amount</label>
            <input
              type="number"
              step="0.01"
              min="0"
              required
              className="input"
              placeholder="0.00"
              value={form.amount}
              onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
            />
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={!!deleteTarget}
        message={`Delete the budget for "${deleteTarget?.category_name}"?`}
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
        loading={deleting}
      />
    </div>
  );
}
