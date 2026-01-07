import { TaskStats as TaskStatsType } from '@/types/task';
import { CheckCircle2, Circle, Clock, XCircle, ListTodo } from 'lucide-react';

interface TaskStatsProps {
  stats: TaskStatsType;
}

export function TaskStats({ stats }: TaskStatsProps) {
  const statItems = [
    {
      label: 'Total',
      value: stats.total,
      icon: ListTodo,
      className: 'text-foreground',
    },
    {
      label: 'To Do',
      value: stats.todo,
      icon: Circle,
      className: 'status-todo',
    },
    {
      label: 'In Progress',
      value: stats.in_progress,
      icon: Clock,
      className: 'status-in-progress',
    },
    {
      label: 'Done',
      value: stats.done,
      icon: CheckCircle2,
      className: 'status-done',
    },
    {
      label: 'Cancelled',
      value: stats.cancelled,
      icon: XCircle,
      className: 'status-cancelled',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      {statItems.map((item) => (
        <div
          key={item.label}
          className="glass rounded-lg p-4 animate-fade-in transition-all hover:scale-[1.02]"
        >
          <div className="flex items-center gap-2 mb-2">
            <item.icon className={`w-4 h-4 ${item.className}`} />
            <span className="text-xs text-muted-foreground font-medium">
              {item.label}
            </span>
          </div>
          <p className="text-2xl font-semibold tracking-tight">{item.value}</p>
        </div>
      ))}
    </div>
  );
}
