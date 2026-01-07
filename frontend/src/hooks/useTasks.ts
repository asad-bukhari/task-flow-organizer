import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Task, TaskCreate, TaskUpdate, Priority, Status } from '@/types/task';
import { taskApi } from '@/lib/api';

export interface TaskFilters {
  status?: Status | null;
  priority?: Priority | null;
  search?: string;
}

export function useTasks() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<TaskFilters>({});

  // Fetch tasks with TanStack Query
  const { data: tasks = [], isLoading, error } = useQuery({
    queryKey: ['tasks', filters.status, filters.priority],
    queryFn: () => taskApi.getTasks({
      skip: 0,
      limit: 100,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
    }),
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => taskApi.getStats(),
  });

  // Filter tasks by search term locally
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      if (filters.search) {
        const search = filters.search.toLowerCase();
        return (
          task.title.toLowerCase().includes(search) ||
          task.description?.toLowerCase().includes(search)
        );
      }
      return true;
    });
  }, [tasks, filters.search]);

  // Create task mutation
  const createMutation = useMutation({
    mutationFn: taskApi.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  // Update task mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: TaskUpdate }) =>
      taskApi.updateTask(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  // Delete task mutation
  const deleteMutation = useMutation({
    mutationFn: taskApi.deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const createTask = useCallback((data: TaskCreate) => {
    return createMutation.mutateAsync(data);
  }, [createMutation]);

  const updateTask = useCallback((id: number, data: TaskUpdate) => {
    return updateMutation.mutateAsync({ id, data });
  }, [updateMutation]);

  const deleteTask = useCallback((id: number) => {
    return deleteMutation.mutateAsync(id);
  }, [deleteMutation]);

  const getTask = useCallback((id: number) => {
    return tasks.find(task => task.id === id);
  }, [tasks]);

  return {
    tasks: filteredTasks,
    allTasks: tasks,
    stats,
    filters,
    setFilters,
    isLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
    getTask,
  };
}
