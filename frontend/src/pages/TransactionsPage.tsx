import { useEffect, useState, useCallback } from 'react';
import { Plus, Search, Pencil, Trash2, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import toast from 'react-hot-toast';
import { transactionsApi, categoriesApi, extractError, type TransactionFilters } from '../api/client';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { ConfirmDialog } from '../components/ui/ConfirmDialog';
import { cn, formatCurrency, formatDate, todayISO } from '../utils/format';
import type { Category, PaginatedResponse, Transaction, TransactionType } from '../types';

interface FormState {
  type: TransactionType;
  amount: string;
  category_id: string;
  description: string;
  transaction_date: string;
}

const emptyForm: FormState = {
  type: 'expense',
  amount: '',
  category_id: '',
  description: '',
  transaction_date: todayISO(),
};

export function TransactionsPage() {
  const [data, setData] = useState<PaginatedResponse<Transaction> | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<TransactionFilters>({ page: 1, page_size: 10, sort_by: 'transaction_date', sort_order: 'desc' });
  const [searchInput, setSearchInput] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Transaction | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Transaction | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError('');
    transactionsApi
      .list(filters)
      .then(setData)
      .catch((err) => setError(extractError(err)))
      .finally(() => setLoading(false));
  }, [filters]);

  useEffect(() => {
    categoriesApi.list().then(setCategories).catch(() => {});
  }, []);

  useEffect(load, [load]);

  useEffect(() => {
    const t = setTimeout(() => {
      setFilters((f) => ({ ...f, search: searchInput || undefined, page: 1 }));
    }, 350);
    return () => clearTimeout(t);
  }, [searchInput]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (txn: Transaction) => {
    setEditing(txn);
    setForm({
      type: txn.type,
      amount: txn.amount,
      category_id: txn.category_id ? String(txn.category_id) : '',
      description: txn.description ?? '',
      transaction_date: txn.transaction_date,
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.amount || parseFloat(form.amount) <= 0) {
      toast.error('Enter a valid amount');
      return;
    }
    setSaving(true);
    const payload = {
      type: form.type,
      amount: form.amount,
      category_id: form.category_id ? Number(form.category_id) : null,
      description: form.description || null,
      transaction_date: form.transaction_date,
    };
    try {
      if (editing) {
        await transactionsApi.update(editing.id, payload);
        toast.success('Transaction updated');
      } else {
        await transactionsApi.create(payload);
        toast.success('Transaction created');
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
      await transactionsApi.delete(deleteTarget.id);
      toast.success('Transaction deleted');
      setDeleteTarget(null);
      load();
    } catch (err) {
      toast.error(extractError(err, 'Delete failed'));
    } finally {
      setDeleting(false);
    }
  };

  const availableCategories = categories.filter((c) => c.type === form.type);
  const totalPages = data?.meta.total_pages ?? 0;
  const currentPage = data?.meta.page ?? 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Transactions</h1>
          <p className="mt-1 text-sm text-slate-500">Create, edit and review your income and expenses.</p>
        </div>
        <button className="btn-primary" onClick={openCreate}>
          <Plus className="h-4 w-4" /> Add transaction
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              className="input pl-9"
              placeholder="Search descriptions…"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
          </div>
          <select
            className="input w-auto"
            value={filters.type ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, type: (e.target.value || undefined) as TransactionType | undefined, page: 1 }))}
          >
            <option value="">All types</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
          <select
            className="input w-auto"
            value={filters.category_id ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, category_id: e.target.value ? Number(e.target.value) : undefined, page: 1 }))}
          >
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <select
            className="input w-auto"
            value={`${filters.sort_by}:${filters.sort_order}`}
            onChange={(e) => {
              const [by, order] = e.target.value.split(':');
              setFilters((f) => ({ ...f, sort_by: by as TransactionFilters['sort_by'], sort_order: order as 'asc' | 'desc' }));
            }}
          >
            <option value="transaction_date:desc">Newest first</option>
            <option value="transaction_date:asc">Oldest first</option>
            <option value="amount:desc">Amount: high→low</option>
            <option value="amount:asc">Amount: low→high</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        {loading ? (
          <PageSpinner />
        ) : error ? (
          <ErrorState message={error} onRetry={load} />
        ) : !data || data.items.length === 0 ? (
          <EmptyState
            title="No transactions found"
            description="Try adjusting your filters or add a new transaction."
            action={
              <button className="btn-primary" onClick={openCreate}>
                <Plus className="h-4 w-4" /> Add transaction
              </button>
            }
            icon={<Filter className="h-7 w-7" />}
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50">
                  <tr>
                    <th className="px-5 py-3 text-left font-medium text-slate-500">Date</th>
                    <th className="px-5 py-3 text-left font-medium text-slate-500">Description</th>
                    <th className="px-5 py-3 text-left font-medium text-slate-500">Category</th>
                    <th className="px-5 py-3 text-left font-medium text-slate-500">Type</th>
                    <th className="px-5 py-3 text-right font-medium text-slate-500">Amount</th>
                    <th className="px-5 py-3 text-right font-medium text-slate-500">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {data.items.map((t) => (
                    <tr key={t.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30">
                      <td className="px-5 py-3 text-slate-500">{formatDate(t.transaction_date)}</td>
                      <td className="px-5 py-3 text-slate-800 dark:text-slate-100">{t.description ?? '—'}</td>
                      <td className="px-5 py-3 text-slate-500">{t.category_name ?? 'Uncategorized'}</td>
                      <td className="px-5 py-3">
                        <Badge variant={t.type === 'income' ? 'green' : 'red'}>{t.type}</Badge>
                      </td>
                      <td className={cn('px-5 py-3 text-right font-semibold', t.type === 'income' ? 'text-green-600' : 'text-red-600')}>
                        {t.type === 'income' ? '+' : '−'}
                        {formatCurrency(t.amount)}
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex justify-end gap-1">
                          <button className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => openEdit(t)} aria-label="Edit">
                            <Pencil className="h-4 w-4" />
                          </button>
                          <button className="rounded-lg p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-950" onClick={() => setDeleteTarget(t)} aria-label="Delete">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3 dark:border-slate-800">
              <p className="text-sm text-slate-500">
                Showing {data.items.length} of {data.meta.total}
              </p>
              <div className="flex items-center gap-2">
                <button
                  className="btn-secondary disabled:opacity-50"
                  disabled={currentPage <= 1}
                  onClick={() => setFilters((f) => ({ ...f, page: currentPage - 1 }))}
                >
                  <ChevronLeft className="h-4 w-4" /> Prev
                </button>
                <span className="text-sm text-slate-500">
                  Page {currentPage} of {Math.max(totalPages, 1)}
                </span>
                <button
                  className="btn-secondary disabled:opacity-50"
                  disabled={currentPage >= totalPages}
                  onClick={() => setFilters((f) => ({ ...f, page: currentPage + 1 }))}
                >
                  Next <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Create/Edit modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit transaction' : 'New transaction'}
        footer={
          <>
            <button className="btn-secondary" onClick={() => setModalOpen(false)} disabled={saving}>
              Cancel
            </button>
            <button className="btn-primary" form="txn-form" type="submit" disabled={saving}>
              {saving ? 'Saving…' : editing ? 'Save changes' : 'Create'}
            </button>
          </>
        }
      >
        <form id="txn-form" onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Type</label>
              <select
                className="input"
                value={form.type}
                onChange={(e) => setForm((f) => ({ ...f, type: e.target.value as TransactionType, category_id: '' }))}
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>
            <div>
              <label className="label">Amount</label>
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
          </div>
          <div>
            <label className="label">Category</label>
            <select
              className="input"
              value={form.category_id}
              onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
            >
              <option value="">Uncategorized</option>
              {availableCategories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Description</label>
            <input
              className="input"
              placeholder="Optional note"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Date</label>
            <input
              type="date"
              required
              max={todayISO()}
              className="input"
              value={form.transaction_date}
              onChange={(e) => setForm((f) => ({ ...f, transaction_date: e.target.value }))}
            />
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={!!deleteTarget}
        message={`Delete this transaction? This cannot be undone.`}
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
        loading={deleting}
      />
    </div>
  );
}
