export type Priority = 'low' | 'medium' | 'high';
export type Status = 'todo' | 'in_progress' | 'done' | 'cancelled';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: Priority;
  status: Status;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: Priority;
  status?: Status;
  due_date?: string | null;
}

export interface TaskUpdate {
  title?: string | null;
  description?: string | null;
  priority?: Priority | null;
  status?: Status | null;
  due_date?: string | null;
}

export interface TaskStats {
  total: number;
  todo: number;
  in_progress: number;
  done: number;
  cancelled: number;
  by_priority: {
    low: number;
    medium: number;
    high: number;
  };
}
