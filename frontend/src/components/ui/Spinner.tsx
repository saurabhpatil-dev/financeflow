import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/format';

export function Spinner({ className }: { className?: string }) {
  return <Loader2 className={cn('h-5 w-5 animate-spin', className)} aria-hidden />;
}

export function PageSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex h-64 items-center justify-center gap-3 text-slate-500">
      <Spinner />
      <span className="text-sm">{label}</span>
    </div>
  );
}
