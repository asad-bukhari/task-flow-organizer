import { useState } from 'react';
import { Task, TaskCreate, TaskUpdate, Status } from '@/types/task';
import { useTasks } from '@/hooks/useTasks';
import { Header } from '@/components/Header';
import { TaskStats } from '@/components/TaskStats';
import { TaskFilters } from '@/components/TaskFilters';
import { TaskList } from '@/components/TaskList';
import { TaskForm } from '@/components/TaskForm';
import { DeleteConfirmDialog } from '@/components/DeleteConfirmDialog';
import { toast } from 'sonner';

const Index = () => {
  const { tasks, stats, filters, setFilters, createTask, updateTask, deleteTask, isLoading, error } = useTasks();
  
  const [formOpen, setFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);

  const handleCreateTask = () => {
    setEditingTask(null);
    setFormOpen(true);
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setFormOpen(true);
  };

  const handleFormSubmit = (data: TaskCreate | TaskUpdate) => {
    if (editingTask) {
      updateTask(editingTask.id, data as TaskUpdate);
      toast.success('Task updated successfully');
    } else {
      createTask(data as TaskCreate);
      toast.success('Task created successfully');
    }
  };

  const handleDeleteClick = (id: number) => {
    const task = tasks.find(t => t.id === id);
    if (task) {
      setTaskToDelete(task);
      setDeleteDialogOpen(true);
    }
  };

  const handleDeleteConfirm = () => {
    if (taskToDelete) {
      deleteTask(taskToDelete.id);
      toast.success('Task deleted successfully');
      setTaskToDelete(null);
    }
  };

  const handleStatusChange = (id: number, status: Status) => {
    updateTask(id, { status });
    toast.success(`Task moved to ${status.replace('_', ' ')}`);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header onCreateTask={handleCreateTask} />

      <main className="container mx-auto px-4 py-6 space-y-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-muted-foreground">Loading tasks...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-destructive">Error loading tasks. Please check if the backend is running.</div>
          </div>
        ) : (
          <>
            <TaskStats stats={stats} />

            <div className="space-y-4">
              <TaskFilters filters={filters} onFiltersChange={setFilters} />
              <TaskList
                tasks={tasks}
                onEdit={handleEditTask}
                onDelete={handleDeleteClick}
                onStatusChange={handleStatusChange}
              />
            </div>
          </>
        )}
      </main>

      <TaskForm
        open={formOpen}
        onOpenChange={setFormOpen}
        task={editingTask}
        onSubmit={handleFormSubmit}
      />

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleDeleteConfirm}
        taskTitle={taskToDelete?.title}
      />
    </div>
  );
};

export default Index;
