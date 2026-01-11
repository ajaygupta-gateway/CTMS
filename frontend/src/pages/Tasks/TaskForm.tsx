import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { tasksApi } from '../../api/tasks';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { useAuth } from '../../context/AuthContext';
import type { Task, TaskPriority, TaskStatus } from '../../types';

export default function TaskForm() {
    const { id } = useParams();
    const isEditMode = !!id;
    const navigate = useNavigate();
    const { user } = useAuth();
    const isAuditor = user?.role === 'auditor';

    // Form State
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        status: 'pending' as TaskStatus,
        priority: 'medium' as TaskPriority,
        estimated_hours: '',
        actual_hours: '',
        deadline: '',
        assigned_to: '',
        parent_task: '',
        priority_escalated: false
    });

    // Data Lists
    const [users, setUsers] = useState<any[]>([]);
    const [tasks, setTasks] = useState<Task[]>([]); // For parent task selection

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                // Fetch Users for Assignment (Managers only or if public list allowed)
                // If developer, maybe only fetch self or just rely on current user
                if (user?.role === 'manager') {
                    const usersRes = await tasksApi.getUsers();
                    setUsers(usersRes.data);
                } else if (user) {
                    // Start with just the current user if not manager
                    setUsers([user]);
                }

                // Fetch Tasks for Parent Task Dropdown
                const tasksRes = await tasksApi.getTasks();
                setTasks(tasksRes.data);

                if (isEditMode) {
                    const taskRes = await tasksApi.getTask(Number(id));
                    const task = taskRes.data;
                    if (task) {
                        setFormData({
                            title: task.title,
                            description: task.description,
                            status: task.status,
                            priority: task.priority,
                            estimated_hours: task.estimated_hours.toString(),
                            actual_hours: task.actual_hours ? task.actual_hours.toString() : '',
                            deadline: task.deadline ? task.deadline.slice(0, 16) : '', // Format for datetime-local
                            assigned_to: task.assigned_to.toString(),
                            parent_task: task.parent_task ? task.parent_task.toString() : '',
                            priority_escalated: task.priority_escalated
                        });
                    }
                } else {
                    // Default values for new task
                    setFormData(prev => ({
                        ...prev,
                        assigned_to: user ? user.id.toString() : ''
                    }));
                }
            } catch (err) {
                console.error(err);
                setError('Failed to load data');
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [id, isEditMode, user]); // Added user dependency to ensure defaults are set

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { id, value, type } = e.target;

        if (type === 'checkbox') {
            setFormData(prev => ({ ...prev, [id]: (e.target as HTMLInputElement).checked }));
        } else {
            setFormData(prev => ({ ...prev, [id]: value }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const payload: any = {
            title: formData.title,
            description: formData.description,
            status: formData.status,
            priority: formData.priority,
            estimated_hours: parseFloat(formData.estimated_hours),
            deadline: new Date(formData.deadline).toISOString(),
            assigned_to: parseInt(formData.assigned_to),
            priority_escalated: formData.priority_escalated,
            actual_hours: formData.actual_hours ? parseFloat(formData.actual_hours) : null,
            parent_task: formData.parent_task ? parseInt(formData.parent_task) : null
        };

        // Developer restriction: force assigned_to self if not manager
        if (user?.role !== 'manager') {
            payload.assigned_to = user?.id;
        }

        try {
            if (isEditMode) {
                await tasksApi.updateTask(Number(id), payload);
            } else {
                await tasksApi.createTask(payload);
            }
            navigate('/tasks');
        } catch (err: any) {
            console.error(err);
            const backendError = err.response?.data;
            if (backendError && typeof backendError === 'object') {
                // If the backend returns a detail string or a list of errors
                if (backendError.detail) {
                    setError(backendError.detail);
                } else if (Array.isArray(backendError)) {
                    setError(backendError.join(' '));
                } else if (backendError.non_field_errors) {
                    setError(backendError.non_field_errors.join(' '));
                } else {
                    // Try to extract field-specific errors
                    const firstError = Object.values(backendError)[0];
                    if (Array.isArray(firstError)) {
                        setError(firstError.join(' '));
                    } else {
                        setError('Failed to save task: Validation error');
                    }
                }
            } else {
                setError('Failed to save task');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading && !users.length && !tasks.length) return <div className="p-8 text-center">Loading...</div>;

    return (
        <div className="flex justify-center p-4">
            <Card className="w-full max-w-2xl">
                <CardHeader>
                    <CardTitle>{isEditMode ? (isAuditor ? 'Task Details' : 'Edit Task') : 'Create New Task'}</CardTitle>
                    <CardDescription>{isAuditor ? 'View task details.' : 'Fill in the details for your task.'}</CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <fieldset disabled={isAuditor} className="contents">
                            {error && <div className="text-sm text-red-500">{error}</div>}

                            {/* Title */}
                            <div className="space-y-2">
                                <Label htmlFor="title">Title</Label>
                                <Input id="title" value={formData.title} onChange={handleChange} required />
                            </div>

                            {/* Description */}
                            <div className="space-y-2">
                                <Label htmlFor="description">Description</Label>
                                <textarea
                                    id="description"
                                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    value={formData.description}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Status */}
                                <div className="space-y-2">
                                    <Label htmlFor="status">Status</Label>
                                    <select
                                        id="status"
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        value={formData.status}
                                        onChange={handleChange}
                                    >
                                        <option value="pending">Pending</option>
                                        <option value="in_progress">In Progress</option>
                                        <option value="blocked">Blocked</option>
                                        <option value="completed">Completed</option>
                                    </select>
                                </div>

                                {/* Priority */}
                                <div className="space-y-2">
                                    <Label htmlFor="priority">Priority</Label>
                                    <select
                                        id="priority"
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        value={formData.priority}
                                        onChange={handleChange}
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>

                                {/* Estimated Hours */}
                                <div className="space-y-2">
                                    <Label htmlFor="estimated_hours">Estimated Hours</Label>
                                    <Input
                                        id="estimated_hours"
                                        type="number"
                                        step="0.01"
                                        value={formData.estimated_hours}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                {/* Actual Hours */}
                                <div className="space-y-2">
                                    <Label htmlFor="actual_hours">Actual Hours</Label>
                                    <Input
                                        id="actual_hours"
                                        type="number"
                                        step="0.01"
                                        value={formData.actual_hours}
                                        onChange={handleChange}
                                        placeholder="Optional"
                                    />
                                </div>

                                {/* Deadline */}
                                <div className="space-y-2">
                                    <Label htmlFor="deadline">Deadline</Label>
                                    <Input
                                        id="deadline"
                                        type="datetime-local"
                                        value={formData.deadline}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                {/* Assigned To */}
                                <div className="space-y-2">
                                    <Label htmlFor="assigned_to">Assigned To</Label>
                                    <select
                                        id="assigned_to"
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        value={formData.assigned_to}
                                        onChange={handleChange}
                                        disabled={user?.role !== 'manager'}
                                    >
                                        {users.map(u => (
                                            <option key={u.id} value={u.id}>
                                                {u.username} ({u.role})
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Parent Task */}
                                <div className="space-y-2">
                                    <Label htmlFor="parent_task">Parent Task</Label>
                                    <select
                                        id="parent_task"
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        value={formData.parent_task}
                                        onChange={handleChange}
                                    >
                                        <option value="">None</option>
                                        {tasks
                                            .filter(t => t.id !== Number(id)) // Prevent self-parenting
                                            .map(t => (
                                                <option key={t.id} value={t.id}>
                                                    {t.title}
                                                </option>
                                            ))}
                                    </select>
                                </div>

                                {/* Escalated Checkbox */}
                                <div className="flex items-center space-x-2 pt-8">
                                    <input
                                        type="checkbox"
                                        id="priority_escalated"
                                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                        checked={formData.priority_escalated}
                                        onChange={handleChange}
                                    />
                                    <Label htmlFor="priority_escalated">Escalated Priority</Label>
                                </div>
                            </div>
                        </fieldset>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button type="button" variant="ghost" onClick={() => navigate('/tasks')}>
                            {isAuditor ? 'Back' : 'Cancel'}
                        </Button>
                        {!isAuditor && (
                            <Button type="submit">
                                {isEditMode ? 'Update Task' : 'Create Task'}
                            </Button>
                        )}
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
