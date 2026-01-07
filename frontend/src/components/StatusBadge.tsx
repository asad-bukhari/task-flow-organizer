import { Status } from '@/types/task';
import { cn } from '@/lib/utils';
import { CheckCircle2, Circle, Clock, XCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = {
    todo: {
      label: 'To Do',
      icon: Circle,
      colorClass: 'status-todo',
      bgClass: 'bg-status-todo/10',
    },
    in_progress: {
      label: 'In Progress',
      icon: Clock,
      colorClass: 'status-in-progress',
      bgClass: 'bg-status-in-progress/10',
    },
    done: {
      label: 'Done',
      icon: CheckCircle2,
      colorClass: 'status-done',
      bgClass: 'bg-status-done/10',
    },
    cancelled: {
      label: 'Cancelled',
      icon: XCircle,
      colorClass: 'status-cancelled',
      bgClass: 'bg-status-cancelled/10',
    },
  };

  const { label, icon: Icon, colorClass, bgClass } = config[status];

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
        bgClass,
        className
      )}
    >
      <Icon className={cn('w-3 h-3', colorClass)} />
      <span className={colorClass}>{label}</span>
    </div>
  );
}
