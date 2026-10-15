import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  PiggyBank,
  ArrowRight,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { dashboardApi } from '../api/client';
import { extractError } from '../api/client';
import { StatCard } from '../components/ui/StatCard';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Badge } from '../components/ui/Badge';
import {
  cn,
  formatCurrency,
  formatDate,
  monthShortLabel,
} from '../utils/format';
import type { DashboardSummary } from '../types';

const PIE_COLORS = ['#2563eb', '#16a34a', '#dc2626', '#f59e0b', '#9333ea', '#0891b2', '#db2777', '#65a30d', '#ea580c', '#64748b'];

export function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    dashboardApi
      .summary()
      .then(setData)
      .catch((err) => setError(extractError(err)))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (loading) return <PageSpinner label="Loading dashboard…" />;
  if (error || !data) return <ErrorState message={error || 'No data'} onRetry={load} />;

  const trendData = data.monthly_trend.map((p) => ({
    month: monthShortLabel(p.month),
    income: parseFloat(p.income),
    expense: parseFloat(p.expense),
  }));
  const pieData = data.expense_breakdown.map((b) => ({
    name: b.category_name,
    value: parseFloat(b.amount),
  }));
  const hasData = parseFloat(data.total_income) > 0 || parseFloat(data.total_expense) > 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">
          Your financial overview at a glance.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Income"
          value={data.total_income}
          icon={<TrendingUp className="h-5 w-5" />}
          accent="green"
          change={data.income_change_pct ?? undefined}
          hint="vs last month"
        />
        <StatCard
          label="Total Expenses"
          value={data.total_expense}
          icon={<TrendingDown className="h-5 w-5" />}
          accent="red"
          change={data.expense_change_pct ?? undefined}
          hint="vs last month"
        />
        <StatCard
          label="Current Balance"
          value={data.current_balance}
          icon={<Wallet className="h-5 w-5" />}
          accent="blue"
        />
        <StatCard
          label="This Month"
          value={data.monthly_balance}
          icon={<PiggyBank className="h-5 w-5" />}
          accent="purple"
          hint={`${formatCurrency(data.monthly_income)} in / ${formatCurrency(data.monthly_expense)} out`}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Trend chart */}
        <div className="card p-5 lg:col-span-2">
          <h2 className="mb-4 text-base font-semibold">Income vs Expenses (12 months)</h2>
          {trendData.length === 0 ? (
            <EmptyState title="No transactions yet" description="Add a transaction to see your trend." />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="incomeFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#16a34a" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expenseFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#dc2626" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#dc2626" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={{ borderRadius: 8, fontSize: 12 }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Area
                  type="monotone"
                  dataKey="income"
                  name="Income"
                  stroke="#16a34a"
                  strokeWidth={2}
                  fill="url(#incomeFill)"
                />
                <Area
                  type="monotone"
                  dataKey="expense"
                  name="Expense"
                  stroke="#dc2626"
                  strokeWidth={2}
                  fill="url(#expenseFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Expense breakdown */}
        <div className="card p-5">
          <h2 className="mb-4 text-base font-semibold">Expense Breakdown</h2>
          {pieData.length === 0 ? (
            <EmptyState title="No expenses this month" />
          ) : (
            <>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={2}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-3 space-y-2">
                {data.expense_breakdown.slice(0, 5).map((b, i) => (
                  <div key={b.category_id ?? i} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span
                        className="h-2.5 w-2.5 rounded-full"
                        style={{ background: PIE_COLORS[i % PIE_COLORS.length] }}
                      />
                      <span className="text-slate-600 dark:text-slate-300">{b.category_name}</span>
                    </div>
                    <span className="font-medium">{formatCurrency(b.amount)}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Recent transactions */}
      <div className="card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold">Recent Transactions</h2>
          <Link
            to="/transactions"
            className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
          >
            View all <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        {!hasData || data.recent_transactions.length === 0 ? (
          <EmptyState
            title="No transactions yet"
            description="Create your first transaction to see it here."
            action={
              <Link to="/transactions" className="btn-primary">
                Add transaction
              </Link>
            }
          />
        ) : (
          <div className="-mx-5 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-y border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50">
                <tr>
                  <th className="px-5 py-2 text-left font-medium text-slate-500">Date</th>
                  <th className="px-5 py-2 text-left font-medium text-slate-500">Description</th>
                  <th className="px-5 py-2 text-left font-medium text-slate-500">Category</th>
                  <th className="px-5 py-2 text-left font-medium text-slate-500">Type</th>
                  <th className="px-5 py-2 text-right font-medium text-slate-500">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {data.recent_transactions.map((t) => (
                  <tr key={t.id}>
                    <td className="px-5 py-3 text-slate-500">{formatDate(t.transaction_date)}</td>
                    <td className="px-5 py-3 text-slate-800 dark:text-slate-100">
                      {t.description ?? '—'}
                    </td>
                    <td className="px-5 py-3 text-slate-500">{t.category_name ?? 'Uncategorized'}</td>
                    <td className="px-5 py-3">
                      <Badge variant={t.type === 'income' ? 'green' : 'red'}>{t.type}</Badge>
                    </td>
                    <td
                      className={cn(
                        'px-5 py-3 text-right font-semibold',
                        t.type === 'income' ? 'text-green-600' : 'text-red-600',
                      )}
                    >
                      {t.type === 'income' ? '+' : '−'}
                      {formatCurrency(t.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
