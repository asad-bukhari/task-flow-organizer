import { Priority } from '@/types/task';
import { cn } from '@/lib/utils';

interface PriorityBadgeProps {
  priority: Priority;
  className?: string;
}

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  const config = {
    high: {
      label: 'High',
      dotClass: 'priority-high-dot',
      textClass: 'text-priority-high',
    },
    medium: {
      label: 'Medium',
      dotClass: 'priority-medium-dot',
      textClass: 'text-priority-medium',
    },
    low: {
      label: 'Low',
      dotClass: 'priority-low-dot',
      textClass: 'text-priority-low',
    },
  };

  const { label, dotClass, textClass } = config[priority];

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-muted text-xs font-medium',
        className
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full', dotClass)} />
      <span className={textClass}>{label}</span>
    </div>
  );
}
