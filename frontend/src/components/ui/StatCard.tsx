import type { ReactNode } from 'react';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { cn, formatCurrency } from '../../utils/format';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  accent?: 'green' | 'red' | 'blue' | 'purple' | 'slate';
  change?: number | null;
  hint?: string;
}

const accentMap: Record<NonNullable<StatCardProps['accent']>, string> = {
  green: 'bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400',
  red: 'bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400',
  blue: 'bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400',
  purple: 'bg-purple-50 text-purple-600 dark:bg-purple-950 dark:text-purple-400',
  slate: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
};

export function StatCard({ label, value, icon, accent = 'slate', change, hint }: StatCardProps) {
  const isPositive = (change ?? 0) >= 0;
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-slate-50">
            {formatCurrency(value)}
          </p>
        </div>
        <div className={cn('flex h-11 w-11 items-center justify-center rounded-lg', accentMap[accent])}>
          {icon}
        </div>
      </div>
      {(change !== undefined || hint) && (
        <div className="mt-3 flex items-center gap-2 text-xs">
          {change !== undefined && change !== null && (
            <span
              className={cn(
                'inline-flex items-center gap-0.5 font-medium',
                isPositive ? 'text-green-600' : 'text-red-600',
              )}
            >
              {isPositive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
              {Math.abs(change).toFixed(1)}%
            </span>
          )}
          {hint && <span className="text-slate-400">{hint}</span>}
        </div>
      )}
    </div>
  );
}
