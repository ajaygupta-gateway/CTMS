import { useEffect, useState } from 'react';
import { tasksApi } from '../../api/tasks';
import type { Task, TaskStatus, TaskPriority } from '../../types';
import { useNavigate } from 'react-router-dom'; // Removed Link from imports if replaced by card click, but might keep for Create button
import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Plus, Calendar, Clock, Trash2, User } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../context/AuthContext';

export default function TasksList() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();
    const navigate = useNavigate();

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

    const handleDelete = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation(); // Prevent card click
        if (window.confirm('Are you sure you want to delete this task?')) {
            try {
                await tasksApi.deleteTask(id);
                setTasks(prev => prev.filter(t => t.id !== id));
            } catch (error) {
                console.error("Failed to delete task", error);
                alert('Failed to delete task');
            }
        }
    };

    const statusColors: Record<TaskStatus, string> = {
        pending: 'bg-yellow-100 text-yellow-800',
        in_progress: 'bg-blue-100 text-blue-800',
        blocked: 'bg-red-100 text-red-800',
        completed: 'bg-green-100 text-green-800',
    };

    const priorityColors: Record<TaskPriority, string> = {
        low: 'text-gray-500',
        medium: 'text-blue-500',
        high: 'text-orange-500',
        critical: 'text-red-500 font-bold',
    };

    // Check if current time is within working hours (9 AM - 6 PM)
    const isWithinWorkingHours = () => {
        const now = new Date();
        const hour = now.getHours();
        return hour >= 9 && hour < 18;
    };

    const canCreateTask = user?.role !== 'auditor' && (user?.role === 'manager' || isWithinWorkingHours());
    const createButtonTooltip = user?.role === 'developer' && !isWithinWorkingHours()
        ? 'Task creation is only allowed between 9:00 AM - 6:00 PM'
        : '';

    if (loading) return <div>Loading tasks...</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">Tasks</h2>
                {user?.role !== 'auditor' && (
                    <div className="relative group">
                        <Link to="/tasks/new" className={!canCreateTask ? 'pointer-events-none' : ''}>
                            <Button disabled={!canCreateTask}>
                                <Plus className="mr-2 h-4 w-4" /> Create Task
                            </Button>
                        </Link>
                        {createButtonTooltip && (
                            <div className="absolute bottom-full mb-2 right-0 hidden group-hover:block bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap z-10">
                                {createButtonTooltip}
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {tasks.map((task) => (
                    <Card
                        key={task.id}
                        className="hover:shadow-md transition-shadow cursor-pointer relative group"
                        onClick={() => navigate(`/tasks/${task.id}`)}
                    >
                        <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                            <div className="space-y-1">
                                <CardTitle className="text-base font-semibold leading-none">
                                    {task.title}
                                </CardTitle>
                                <div className="flex gap-2 text-xs">
                                    <span className={cn("px-2 py-0.5 rounded-full capitalize", statusColors[task.status])}>
                                        {task.status.replace('_', ' ')}
                                    </span>
                                    <span className={cn("capitalize", priorityColors[task.priority])}>
                                        {task.priority}
                                    </span>
                                </div>
                            </div>

                            {user?.role !== 'auditor' && (
                                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                                    {/* Edit is implied by card click, but keeping icon for clarity or removing as per preference. 
                                         User said "in case of auditor remove the title Edit". 
                                         I will remove the specific Edit button since the whole card is clickable.
                                         But wait, keeping Delete button.
                                     */}
                                    {/* Optional: explicit edit button */}
                                    {/* <Button variant="ghost" size="icon" className="h-8 w-8 text-blue-500" onClick={() => navigate(`/tasks/${task.id}`)}>
                                        <Edit className="h-4 w-4" />
                                    </Button> */}

                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-8 w-8 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                        onClick={(e) => handleDelete(e, task.id)}
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            )}
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                                {task.description}
                            </p>
                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                                <div className="flex items-center">
                                    <Clock className="mr-1 h-3 w-3" />
                                    {task.estimated_hours}h est.
                                </div>
                                <div className="flex items-center">
                                    <User className="mr-1 h-3 w-3" />
                                    {task.assigned_to_user}
                                </div>
                                {task.deadline && (
                                    <div className="flex items-center">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        {new Date(task.deadline).toLocaleDateString()}
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {tasks.length === 0 && (
                    <div className="col-span-full text-center py-10 text-muted-foreground">
                        No tasks found. Create one to get started.
                    </div>
                )}
            </div>
        </div>
    );
}
