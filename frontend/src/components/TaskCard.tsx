import { Task, Status } from '@/types/task';
import { PriorityBadge } from './PriorityBadge';
import { StatusBadge } from './StatusBadge';
import { Button } from '@/components/ui/button';
import { Calendar, MoreHorizontal, Pencil, Trash2 } from 'lucide-react';
import { format, isPast, isToday } from 'date-fns';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => void;
  onStatusChange: (id: number, status: Status) => void;
}

export function TaskCard({ task, onEdit, onDelete, onStatusChange }: TaskCardProps) {
  const dueDate = task.due_date ? new Date(task.due_date) : null;
  const isOverdue = dueDate && isPast(dueDate) && task.status !== 'done' && task.status !== 'cancelled';
  const isDueToday = dueDate && isToday(dueDate);

  const statusOptions: { value: Status; label: string }[] = [
    { value: 'todo', label: 'To Do' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'done', label: 'Done' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  return (
    <div className="glass rounded-lg p-4 animate-fade-in transition-all hover:border-primary/30 group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-2">
            <StatusBadge status={task.status} />
            <PriorityBadge priority={task.priority} />
          </div>
          
          <h3 className="font-semibold text-foreground mb-1 line-clamp-2">
            {task.title}
          </h3>
          
          {task.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
              {task.description}
            </p>
          )}

          {dueDate && (
            <div
              className={cn(
                'inline-flex items-center gap-1.5 text-xs',
                isOverdue
                  ? 'text-destructive'
                  : isDueToday
                  ? 'text-primary'
                  : 'text-muted-foreground'
              )}
            >
              <Calendar className="w-3 h-3" />
              <span>
                {isOverdue ? 'Overdue: ' : isDueToday ? 'Due today: ' : ''}
                {format(dueDate, 'MMM d, yyyy')}
              </span>
            </div>
          )}
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={() => onEdit(task)}>
              <Pencil className="w-4 h-4 mr-2" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {statusOptions
              .filter((s) => s.value !== task.status)
              .map((option) => (
                <DropdownMenuItem
                  key={option.value}
                  onClick={() => onStatusChange(task.id, option.value)}
                >
                  Move to {option.label}
                </DropdownMenuItem>
              ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => onDelete(task.id)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
