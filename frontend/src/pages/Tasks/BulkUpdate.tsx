import { useEffect, useState } from 'react';
import { tasksApi } from '../../api/tasks';
import type { Task, TaskStatus } from '../../types';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Calendar, Clock, User, CheckSquare, Square, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../context/AuthContext';

export default function BulkUpdate() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTaskIds, setSelectedTaskIds] = useState<Set<number>>(new Set());
    const [bulkStatus, setBulkStatus] = useState<TaskStatus>('pending');
    const [isUpdating, setIsUpdating] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const [showError, setShowError] = useState(false);
    const { user } = useAuth();

    useEffect(() => {
        loadTasks();
    }, []);

    const loadTasks = async () => {
        try {
            const response = await tasksApi.getTasks();
            setTasks(response.data);
        } catch (error) {
            console.error("Failed to load tasks", error);
        } finally {
            setLoading(false);
        }
    };

    const toggleTaskSelection = (taskId: number) => {
        const newSelection = new Set(selectedTaskIds);
        if (newSelection.has(taskId)) {
            newSelection.delete(taskId);
        } else {
            newSelection.add(taskId);
        }
        setSelectedTaskIds(newSelection);
    };

    const selectAll = () => {
        const allTaskIds = new Set(tasks.map(t => t.id));
        setSelectedTaskIds(allTaskIds);
    };

    const clearSelection = () => {
        setSelectedTaskIds(new Set());
    };

    const handleBulkUpdate = async () => {
        if (selectedTaskIds.size === 0) {
            alert('Please select at least one task');
            return;
        }

        // Check time restrictions for developers
        if (user?.role === 'developer') {
            const now = new Date();
            const hour = now.getHours();
            const isWithinWorkingHours = hour >= 9 && hour < 18;
            
            if (!isWithinWorkingHours) {
                // Check if any selected task is not critical
                const selectedTasks = tasks.filter(t => selectedTaskIds.has(t.id));
                const hasNonCritical = selectedTasks.some(t => t.priority !== 'critical');
                
                if (hasNonCritical) {
                    alert('Developers can only update tasks between 9:00 AM - 6:00 PM (except critical priority tasks)');
                    return;
                }
            }
        }

        setIsUpdating(true);
        setShowSuccess(false);
        setShowError(false);

        try {
            await tasksApi.bulkUpdateStatus({
                task_ids: Array.from(selectedTaskIds),
                status: bulkStatus
            });

            // Update local state optimistically
            setTasks(prev => prev.map(task => 
                selectedTaskIds.has(task.id) 
                    ? { ...task, status: bulkStatus }
                    : task
            ));

            setShowSuccess(true);
            clearSelection();

            // Hide success message after 3 seconds
            setTimeout(() => setShowSuccess(false), 3000);
        } catch (error: any) {
            console.error("Failed to bulk update tasks", error);
            setShowError(true);
            
            // Hide error message after 5 seconds
            setTimeout(() => setShowError(false), 5000);
        } finally {
            setIsUpdating(false);
        }
    };

    const statusOptions: { value: TaskStatus; label: string; color: string }[] = [
        { value: 'pending', label: 'Pending', color: 'bg-yellow-500' },
        { value: 'in_progress', label: 'In Progress', color: 'bg-blue-500' },
        { value: 'blocked', label: 'Blocked', color: 'bg-red-500' },
        { value: 'completed', label: 'Completed', color: 'bg-green-500' },
    ];

    const statusColors: Record<TaskStatus, string> = {
        pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        in_progress: 'bg-blue-100 text-blue-800 border-blue-300',
        blocked: 'bg-red-100 text-red-800 border-red-300',
        completed: 'bg-green-100 text-green-800 border-green-300',
    };

    const priorityColors: Record<string, string> = {
        low: 'text-gray-500',
        medium: 'text-blue-500',
        high: 'text-orange-500',
        critical: 'text-red-500 font-bold',
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Bulk Update Tasks
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        Select multiple tasks and update their status in one go
                    </p>
                </div>
            </div>

            {/* Success/Error Messages */}
            {showSuccess && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3 animate-in slide-in-from-top-2">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <p className="text-green-800 font-medium">
                        Successfully updated {selectedTaskIds.size} task(s)!
                    </p>
                </div>
            )}

            {showError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3 animate-in slide-in-from-top-2">
                    <XCircle className="h-5 w-5 text-red-600" />
                    <p className="text-red-800 font-medium">
                        Failed to update tasks. Please try again.
                    </p>
                </div>
            )}

            {/* Bulk Action Toolbar */}
            <div className={cn(
                "sticky top-0 z-10 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 transition-all duration-300",
                selectedTaskIds.size > 0 ? "shadow-lg scale-100 opacity-100" : "scale-95 opacity-50"
            )}>
                <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <CheckSquare className="h-5 w-5 text-blue-600" />
                            <span className="font-semibold text-gray-900">
                                {selectedTaskIds.size} task(s) selected
                            </span>
                        </div>
                        <div className="flex gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={selectAll}
                                className="text-xs"
                            >
                                Select All ({tasks.length})
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={clearSelection}
                                className="text-xs"
                                disabled={selectedTaskIds.size === 0}
                            >
                                Clear
                            </Button>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <label className="text-sm font-medium text-gray-700">
                            Update Status:
                        </label>
                        <div className="flex gap-2">
                            {statusOptions.map(option => (
                                <button
                                    key={option.value}
                                    onClick={() => setBulkStatus(option.value)}
                                    className={cn(
                                        "px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
                                        bulkStatus === option.value
                                            ? `${option.color} text-white shadow-md scale-105`
                                            : "bg-white text-gray-700 border border-gray-300 hover:border-gray-400"
                                    )}
                                >
                                    {option.label}
                                </button>
                            ))}
                        </div>
                        <Button
                            onClick={handleBulkUpdate}
                            disabled={selectedTaskIds.size === 0 || isUpdating || user?.role === 'auditor'}
                            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md"
                        >
                            {isUpdating ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Updating...
                                </>
                            ) : (
                                'Apply Update'
                            )}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Task Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {tasks.map((task) => {
                    const isSelected = selectedTaskIds.has(task.id);
                    return (
                        <Card
                            key={task.id}
                            className={cn(
                                "hover:shadow-lg transition-all duration-200 cursor-pointer relative group",
                                isSelected && "ring-2 ring-blue-500 shadow-lg scale-105 bg-blue-50/50"
                            )}
                            onClick={() => toggleTaskSelection(task.id)}
                        >
                            {/* Selection Indicator */}
                            <div className="absolute top-3 right-3 z-10">
                                {isSelected ? (
                                    <CheckSquare className="h-6 w-6 text-blue-600 animate-in zoom-in-50" />
                                ) : (
                                    <Square className="h-6 w-6 text-gray-400 group-hover:text-gray-600 transition-colors" />
                                )}
                            </div>

                            <CardHeader className="pb-3">
                                <CardTitle className="text-base font-semibold leading-tight pr-8">
                                    {task.title}
                                </CardTitle>
                                <div className="flex gap-2 text-xs mt-2">
                                    <span className={cn(
                                        "px-2.5 py-1 rounded-full capitalize border",
                                        statusColors[task.status]
                                    )}>
                                        {task.status.replace('_', ' ')}
                                    </span>
                                    <span className={cn("capitalize font-medium", priorityColors[task.priority])}>
                                        {task.priority}
                                    </span>
                                </div>
                            </CardHeader>

                            <CardContent>
                                <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                                    {task.description}
                                </p>
                                <div className="flex items-center justify-between text-xs text-muted-foreground">
                                    <div className="flex items-center gap-1">
                                        <Clock className="h-3 w-3" />
                                        <span>{task.estimated_hours}h</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <User className="h-3 w-3" />
                                        <span>{task.assigned_to_user}</span>
                                    </div>
                                    {task.deadline && (
                                        <div className="flex items-center gap-1">
                                            <Calendar className="h-3 w-3" />
                                            <span>{new Date(task.deadline).toLocaleDateString()}</span>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}

                {tasks.length === 0 && (
                    <div className="col-span-full text-center py-16">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                            <CheckSquare className="h-8 w-8 text-gray-400" />
                        </div>
                        <p className="text-muted-foreground text-lg">
                            No tasks found
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
