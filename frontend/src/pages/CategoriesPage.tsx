import { useEffect, useState, useCallback } from 'react';
import { Plus, Pencil, Trash2, Tag } from 'lucide-react';
import toast from 'react-hot-toast';
import { categoriesApi, extractError } from '../api/client';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { ConfirmDialog } from '../components/ui/ConfirmDialog';
import type { Category, CategoryType } from '../types';

interface FormState {
  name: string;
  type: CategoryType;
  color: string;
}

const emptyForm: FormState = { name: '', type: 'expense', color: '#6366f1' };

export function CategoriesPage() {
  const [items, setItems] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Category | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Category | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError('');
    categoriesApi
      .list()
      .then(setItems)
      .catch((err) => setError(extractError(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (c: Category) => {
    setEditing(c);
    setForm({ name: c.name, type: c.type, color: c.color ?? '#6366f1' });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      toast.error('Name is required');
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        await categoriesApi.update(editing.id, { name: form.name, type: form.type, color: form.color });
        toast.success('Category updated');
      } else {
        await categoriesApi.create({ name: form.name, type: form.type, color: form.color });
        toast.success('Category created');
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
      await categoriesApi.delete(deleteTarget.id);
      toast.success('Category deleted');
      setDeleteTarget(null);
      load();
    } catch (err) {
      toast.error(extractError(err, 'Delete failed'));
    } finally {
      setDeleting(false);
    }
  };

  const income = items.filter((c) => c.type === 'income');
  const expense = items.filter((c) => c.type === 'expense');

  const renderRow = (c: Category) => (
    <div
      key={c.id}
      className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 p-4 dark:border-slate-800"
    >
      <div className="flex items-center gap-3">
        <span className="h-3 w-3 rounded-full" style={{ background: c.color ?? '#94a3b8' }} />
        <div>
          <p className="font-medium text-slate-800 dark:text-slate-100">{c.name}</p>
          <p className="text-xs text-slate-400">Created {new Date(c.created_at).toLocaleDateString()}</p>
        </div>
      </div>
      <div className="flex items-center gap-1">
        <button className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => openEdit(c)} aria-label="Edit">
          <Pencil className="h-4 w-4" />
        </button>
        <button className="rounded-lg p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-950" onClick={() => setDeleteTarget(c)} aria-label="Delete">
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Categories</h1>
          <p className="mt-1 text-sm text-slate-500">Organize your transactions with custom categories.</p>
        </div>
        <button className="btn-primary" onClick={openCreate}>
          <Plus className="h-4 w-4" /> New category
        </button>
      </div>

      {loading ? (
        <PageSpinner />
      ) : error ? (
        <ErrorState message={error} onRetry={load} />
      ) : items.length === 0 ? (
        <EmptyState
          title="No categories"
          description="Create your first category to start organizing transactions."
          action={
            <button className="btn-primary" onClick={openCreate}>
              <Plus className="h-4 w-4" /> New category
            </button>
          }
          icon={<Tag className="h-7 w-7" />}
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card p-5">
            <div className="mb-4 flex items-center gap-2">
              <Badge variant="green">Income</Badge>
              <h2 className="text-base font-semibold">{income.length} categories</h2>
            </div>
            <div className="space-y-2">{income.map(renderRow)}</div>
          </div>
          <div className="card p-5">
            <div className="mb-4 flex items-center gap-2">
              <Badge variant="red">Expense</Badge>
              <h2 className="text-base font-semibold">{expense.length} categories</h2>
            </div>
            <div className="space-y-2">{expense.map(renderRow)}</div>
          </div>
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit category' : 'New category'}
        footer={
          <>
            <button className="btn-secondary" onClick={() => setModalOpen(false)} disabled={saving}>
              Cancel
            </button>
            <button className="btn-primary" form="cat-form" type="submit" disabled={saving}>
              {saving ? 'Saving…' : editing ? 'Save' : 'Create'}
            </button>
          </>
        }
      >
        <form id="cat-form" onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Name</label>
            <input
              className="input"
              required
              placeholder="e.g. Groceries"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Type</label>
            <select
              className="input"
              value={form.type}
              onChange={(e) => setForm((f) => ({ ...f, type: e.target.value as CategoryType }))}
            >
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div>
            <label className="label">Color</label>
            <div className="flex items-center gap-3">
              <input
                type="color"
                className="h-10 w-14 cursor-pointer rounded border border-slate-300 dark:border-slate-700"
                value={form.color}
                onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
              />
              <span className="text-sm text-slate-500">{form.color}</span>
            </div>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={!!deleteTarget}
        message={`Delete "${deleteTarget?.name}"? Categories in use by transactions cannot be deleted.`}
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
        loading={deleting}
      />
    </div>
  );
}
