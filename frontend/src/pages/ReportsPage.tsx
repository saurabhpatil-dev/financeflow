import { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
} from 'recharts';
import { TrendingUp, TrendingDown, Wallet, Award, Receipt } from 'lucide-react';
import { reportsApi, extractError } from '../api/client';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { StatCard } from '../components/ui/StatCard';
import { formatCurrency, monthShortLabel } from '../utils/format';
import type {
  MonthlyReport,
  CategoryReport,
  TrendReport,
  SummaryReport,
} from '../types';

export function ReportsPage() {
  const [monthly, setMonthly] = useState<MonthlyReport | null>(null);
  const [categories, setCategories] = useState<CategoryReport | null>(null);
  const [trends, setTrends] = useState<TrendReport | null>(null);
  const [summary, setSummary] = useState<SummaryReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    Promise.all([
      reportsApi.monthly(),
      reportsApi.categories(),
      reportsApi.trends(),
      reportsApi.summary(),
    ])
      .then(([m, c, t, s]) => {
        setMonthly(m);
        setCategories(c);
        setTrends(t);
        setSummary(s);
      })
      .catch((err) => setError(extractError(err)))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (loading) return <PageSpinner label="Generating reports…" />;
  if (error || !monthly || !categories || !trends || !summary)
    return <ErrorState message={error || 'No data'} onRetry={load} />;

  const monthlyData = monthly.items.map((i) => ({
    month: monthShortLabel(i.month),
    income: parseFloat(i.income),
    expense: parseFloat(i.expense),
    balance: parseFloat(i.balance),
  }));
  const trendData = trends.points.map((p) => ({
    period: monthShortLabel(p.period),
    income: parseFloat(p.income),
    expense: parseFloat(p.expense),
  }));
  const expenseCats = categories.items.filter((c) => c.type === 'expense');
  const hasData = summary.transaction_count > 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
        <p className="mt-1 text-sm text-slate-500">Analyze your spending patterns and financial health.</p>
      </div>

      {!hasData ? (
        <EmptyState
          title="No data for reports yet"
          description="Add transactions to generate financial reports."
          icon={<Receipt className="h-7 w-7" />}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Total Income" value={summary.income} icon={<TrendingUp className="h-5 w-5" />} accent="green" />
            <StatCard label="Total Expenses" value={summary.expense} icon={<TrendingDown className="h-5 w-5" />} accent="red" />
            <StatCard label="Net Balance" value={summary.balance} icon={<Wallet className="h-5 w-5" />} accent="blue" />
            <StatCard label="Savings Rate" value={`${summary.savings_rate}%`} icon={<Award className="h-5 w-5" />} accent="purple" />
          </div>

          <div className="card p-5">
            <h2 className="mb-4 text-base font-semibold">Monthly Income vs Expenses</h2>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={monthlyData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <Tooltip formatter={(value: number) => formatCurrency(value)} contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="income" name="Income" fill="#16a34a" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expense" name="Expense" fill="#dc2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="card p-5">
              <h2 className="mb-4 text-base font-semibold">Spending Trend</h2>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="period" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <Tooltip formatter={(value: number) => formatCurrency(value)} contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Line type="monotone" dataKey="income" name="Income" stroke="#16a34a" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="expense" name="Expense" stroke="#dc2626" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-5">
              <h2 className="mb-4 text-base font-semibold">Top Expense Categories</h2>
              {expenseCats.length === 0 ? (
                <EmptyState title="No expenses recorded" />
              ) : (
                <div className="space-y-3">
                  {expenseCats.slice(0, 8).map((c) => {
                    const max = parseFloat(expenseCats[0].total);
                    const pct = max > 0 ? (parseFloat(c.total) / max) * 100 : 0;
                    return (
                      <div key={c.category_id ?? c.category_name}>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600 dark:text-slate-300">{c.category_name}</span>
                          <span className="font-medium">{formatCurrency(c.total)}</span>
                        </div>
                        <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                          <div className="h-full rounded-full bg-brand-500" style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="card p-5">
            <h2 className="mb-4 text-base font-semibold">Monthly Breakdown</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium text-slate-500">Month</th>
                    <th className="px-3 py-2 text-right font-medium text-slate-500">Income</th>
                    <th className="px-3 py-2 text-right font-medium text-slate-500">Expense</th>
                    <th className="px-3 py-2 text-right font-medium text-slate-500">Balance</th>
                    <th className="px-3 py-2 text-right font-medium text-slate-500">Savings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {monthly.items.map((i) => (
                    <tr key={i.month}>
                      <td className="px-3 py-2 text-slate-800 dark:text-slate-100">{monthShortLabel(i.month)}</td>
                      <td className="px-3 py-2 text-right text-green-600">{formatCurrency(i.income)}</td>
                      <td className="px-3 py-2 text-right text-red-600">{formatCurrency(i.expense)}</td>
                      <td className="px-3 py-2 text-right font-medium">{formatCurrency(i.balance)}</td>
                      <td className="px-3 py-2 text-right text-slate-500">{i.savings_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
