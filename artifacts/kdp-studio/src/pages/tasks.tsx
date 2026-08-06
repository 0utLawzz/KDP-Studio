import { useState } from "react";
import { 
  useListTasks, 
  useCreateTask, 
  useUpdateTask, 
  useDeleteTask,
  getListTasksQueryKey
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, GripVertical, CheckSquare, Clock, AlertCircle, Loader2 } from "lucide-react";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose
} from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Task, TaskStatus } from "@workspace/api-client-react/src/generated/api.schemas";

export function Tasks() {
  const { data: tasks, isLoading } = useListTasks();
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [isNewTaskOpen, setIsNewTaskOpen] = useState(false);
  const [newTask, setNewTask] = useState({ title: "", category: "", notes: "" });

  const columns: { id: TaskStatus; label: string; icon: any }[] = [
    { id: 'not_started', label: 'To Do', icon: AlertCircle },
    { id: 'in_progress', label: 'In Progress', icon: Clock },
    { id: 'done', label: 'Done', icon: CheckSquare }
  ];

  const handleCreate = async () => {
    if (!newTask.title.trim()) return;
    try {
      await createTask.mutateAsync({
        data: {
          title: newTask.title,
          category: newTask.category || undefined,
          notes: newTask.notes || undefined,
          status: 'not_started'
        }
      });
      setIsNewTaskOpen(false);
      setNewTask({ title: "", category: "", notes: "" });
      queryClient.invalidateQueries({ queryKey: getListTasksQueryKey() });
      toast({ title: "Task created" });
    } catch (e) {
      toast({ title: "Failed to create task", variant: "destructive" });
    }
  };

  const handleStatusChange = async (task: Task, newStatus: TaskStatus) => {
    if (task.status === newStatus) return;
    
    // Optimistic update
    queryClient.setQueryData(getListTasksQueryKey(), (old: Task[] | undefined) => {
      if (!old) return old;
      return old.map(t => t.id === task.id ? { ...t, status: newStatus } : t);
    });

    try {
      await updateTask.mutateAsync({ id: task.id, data: { status: newStatus } });
      toast({ title: "Task moved" });
    } catch (e) {
      // Revert on failure
      queryClient.invalidateQueries({ queryKey: getListTasksQueryKey() });
      toast({ title: "Failed to move task", variant: "destructive" });
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteTask.mutateAsync({ id });
      queryClient.invalidateQueries({ queryKey: getListTasksQueryKey() });
      toast({ title: "Task deleted" });
    } catch (e) {
      toast({ title: "Failed to delete task", variant: "destructive" });
    }
  };

  if (isLoading) {
    return <div className="p-12 text-center animate-pulse">Loading board...</div>;
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-in fade-in duration-500">
      <div className="flex justify-between items-center mb-6 shrink-0">
        <div>
          <h1 className="text-3xl font-serif text-foreground">Production Board</h1>
          <p className="text-muted-foreground mt-1">Track tasks and studio progress.</p>
        </div>
        
        <Dialog open={isNewTaskOpen} onOpenChange={setIsNewTaskOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" /> Add Task
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="font-serif text-xl">New Task</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Title</label>
                <Input 
                  placeholder="e.g. Design cover for Sobriety Journal" 
                  value={newTask.title}
                  onChange={e => setNewTask({...newTask, title: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Category</label>
                <Input 
                  placeholder="e.g. Design, Metadata, Research" 
                  value={newTask.category}
                  onChange={e => setNewTask({...newTask, category: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Notes</label>
                <Textarea 
                  placeholder="Optional details..." 
                  value={newTask.notes}
                  onChange={e => setNewTask({...newTask, notes: e.target.value})}
                  className="resize-none h-24"
                />
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="ghost">Cancel</Button>
              </DialogClose>
              <Button onClick={handleCreate} disabled={!newTask.title.trim() || createTask.isPending}>
                {createTask.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Create Task
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6 overflow-hidden pb-4">
        {columns.map(col => {
          const columnTasks = tasks?.filter(t => t.status === col.id) || [];
          const Icon = col.icon;
          
          return (
            <div key={col.id} className="flex flex-col bg-muted/30 rounded-xl border border-border overflow-hidden">
              <div className="p-4 border-b border-border bg-card/50 flex justify-between items-center">
                <div className="flex items-center gap-2 font-medium">
                  <Icon className="w-4 h-4 text-muted-foreground" />
                  {col.label}
                </div>
                <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full font-bold">
                  {columnTasks.length}
                </span>
              </div>
              
              <div className="flex-1 p-3 overflow-y-auto space-y-3">
                {columnTasks.map(task => (
                  <Card key={task.id} className="shadow-sm hover:shadow-md transition-shadow group relative cursor-default border-border/60 bg-card">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start gap-2 mb-2">
                        {task.category && (
                          <span className="text-[10px] uppercase font-bold tracking-wider text-primary bg-primary/10 px-2 py-0.5 rounded">
                            {task.category}
                          </span>
                        )}
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="w-6 h-6 opacity-0 group-hover:opacity-100 absolute top-2 right-2 text-destructive hover:bg-destructive hover:text-destructive-foreground transition-all"
                          onClick={() => handleDelete(task.id)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                      
                      <h4 className="font-medium text-foreground leading-tight pr-6">{task.title}</h4>
                      
                      {task.notes && (
                        <p className="text-xs text-muted-foreground mt-2 line-clamp-2">{task.notes}</p>
                      )}
                      
                      <div className="mt-4 pt-3 border-t border-border flex justify-between items-center">
                        <span className="text-[10px] text-muted-foreground font-mono">
                          {format(new Date(task.createdAt), 'MMM d')}
                        </span>
                        
                        <Select 
                          value={task.status} 
                          onValueChange={(val) => handleStatusChange(task, val as TaskStatus)}
                        >
                          <SelectTrigger className="w-[110px] h-7 text-xs bg-secondary border-none">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="not_started">To Do</SelectItem>
                            <SelectItem value="in_progress">In Progress</SelectItem>
                            <SelectItem value="done">Done</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                {columnTasks.length === 0 && (
                  <div className="h-24 border-2 border-dashed border-border/50 rounded-lg flex items-center justify-center text-sm text-muted-foreground/50 italic">
                    Drop tasks here
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
