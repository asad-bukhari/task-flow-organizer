import { Task, TaskCreate, TaskUpdate, TaskStats } from '@/types/task';

const API_BASE = 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'An error occurred');
  }
  return response.json();
}

export const taskApi = {
  // Get all tasks with filters
  async getTasks(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    priority?: string;
  }): Promise<Task[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params?.status) searchParams.set('status', params.status);
    if (params?.priority) searchParams.set('priority', params.priority);

    const response = await fetch(`${API_BASE}/tasks/?${searchParams}`);
    return handleResponse<Task[]>(response);
  },

  // Get task by ID
  async getTask(id: number): Promise<Task> {
    const response = await fetch(`${API_BASE}/tasks/${id}`);
    return handleResponse<Task>(response);
  },

  // Create task
  async createTask(task: TaskCreate): Promise<Task> {
    const response = await fetch(`${API_BASE}/tasks/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    return handleResponse<Task>(response);
  },

  // Update task
  async updateTask(id: number, task: TaskUpdate): Promise<Task> {
    const response = await fetch(`${API_BASE}/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    return handleResponse<Task>(response);
  },

  // Delete task
  async deleteTask(id: number): Promise<void> {
    const response = await fetch(`${API_BASE}/tasks/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to delete task');
    }
  },

  // Get statistics
  async getStats(): Promise<TaskStats> {
    const response = await fetch(`${API_BASE}/tasks/stats`);
    const data = await handleResponse<{
      total: number;
      by_status: Record<string, number>;
      by_priority: Record<string, number>;
    }>(response);

    // Transform backend stats format to frontend format
    return {
      total: data.total,
      todo: data.by_status.todo || 0,
      in_progress: data.by_status.in_progress || 0,
      done: data.by_status.done || 0,
      cancelled: data.by_status.cancelled || 0,
      by_priority: {
        low: data.by_priority.low || 0,
        medium: data.by_priority.medium || 0,
        high: data.by_priority.high || 0,
      },
    };
  },
};
