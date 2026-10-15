import type { ReactNode } from 'react';
import { cn } from '../../utils/format';

type Variant = 'green' | 'red' | 'blue' | 'amber' | 'purple' | 'slate';

const variants: Record<Variant, string> = {
  green: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400',
  red: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400',
  blue: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
  purple: 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-400',
  slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
};

export function Badge({
  children,
  variant = 'slate',
  className,
}: {
  children: ReactNode;
  variant?: Variant;
  className?: string;
}) {
  return <span className={cn('badge', variants[variant], className)}>{children}</span>;
}
