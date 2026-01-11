import { useState, useEffect } from 'react';
import {
    DndContext,
    closestCorners,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragOverlay,
} from '@dnd-kit/core';
import type {
    DragStartEvent,
    DragEndEvent,
} from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { tasksApi } from '../api/tasks';
import { useAuth } from '../context/AuthContext';
import type { Task, TaskStatus } from '../types';
import { TaskBadge } from './TaskBadge';
import { Modal } from './ui/modal';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import { format } from 'date-fns';
import { User } from 'lucide-react';

// Simple droppable container
import { useDroppable } from '@dnd-kit/core';
import { useDraggable } from '@dnd-kit/core';

const COLUMNS: TaskStatus[] = ['pending', 'in_progress', 'blocked', 'completed'];

const Column = ({ id, tasks, children }: { id: string, tasks: Task[], children: React.ReactNode }) => {
    const { setNodeRef } = useDroppable({ id });
    return (
        <div ref={setNodeRef} className="flex flex-col gap-4 rounded-lg bg-slate-50 p-4 min-h-[500px] w-full border border-slate-200">
            <h3 className="font-semibold capitalize text-slate-700">{id.replace('_', ' ')} <span className="text-gray-400 text-sm">({tasks.length})</span></h3>
            {children}
        </div>
    );
};

const DraggableTaskCard = ({ task }: { task: Task }) => {
    const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
        id: task.id.toString(),
        data: { task }
    });

    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    } : undefined;

    return (
        <div ref={setNodeRef} style={style} {...listeners} {...attributes} className={cn("cursor-grab active:cursor-grabbing", isDragging && "opacity-50")}>
            <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="p-3 pb-0">
                    <div className="flex justify-between items-start">
                        <span className="font-medium text-sm line-clamp-2">{task.title}</span>
                        <TaskBadge priority={task.priority} deadline={task.deadline} />
                    </div>
                </CardHeader>
                <CardContent className="p-3 pt-2">
                    <div className="flex items-center text-[10px] text-muted-foreground mb-1">
                        <User className="mr-1 h-2.5 w-2.5" />
                        <span className="truncate">{task.assigned_to_user}</span>
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{task.estimated_hours}h</span>
                        {task.deadline && <span>{format(new Date(task.deadline), 'MMM d')}</span>}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default function KanbanBoard() {
    const { user } = useAuth();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [activeTask, setActiveTask] = useState<Task | null>(null);

    // Modal State
    const [showWarning, setShowWarning] = useState(false);

    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
    );

    useEffect(() => {
        loadMyTasks();
    }, []);

    const loadMyTasks = async () => {
        try {
            const response = await tasksApi.getTasks();
            // Show all tasks that the user has access to (backend handles filtering)
            // Managers see all tasks, Developers see only their assigned tasks
            setTasks(response.data);
        } catch (err) {
            console.error("Failed to load tasks", err);
        }
    };

    const handleDragStart = (event: DragStartEvent) => {
        const { active } = event;
        setActiveTask(active.data.current?.task);
    };

    const handleDragEnd = async (event: DragEndEvent) => {
        const { active, over } = event;
        setActiveTask(null);

        if (!over) return;

        const taskId = Number(active.id);
        const newStatus = over.id as TaskStatus;
        const task = tasks.find(t => t.id === taskId);

        if (!task || task.status === newStatus) return;

        // Time Restriction Check for Developers
        if (user?.role === 'developer') {
            const now = new Date();
            const hour = now.getHours();
            // Allowed: 9 (9:00) to 17 (17:59) -> < 18. Adjust as strictly requested: "outside allowed hours". 
            // Previously assumed 9-18.
            if (hour < 9 || hour >= 18) {
                setShowWarning(true);
                return; // Abort drag
            }
        }

        // Optimistic Update
        const oldStatus = task.status;
        setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));

        try {
            await tasksApi.updateTask(taskId, { status: newStatus });
        } catch (error: any) {
            console.error("Update failed", error);
            // Rollback
            setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: oldStatus } : t));

            const backendError = error.response?.data;
            let message = 'Failed to update task status';

            if (backendError && typeof backendError === 'object') {
                if (backendError.detail) {
                    message = backendError.detail;
                } else if (Array.isArray(backendError)) {
                    message = backendError.join(' ');
                } else if (backendError.non_field_errors) {
                    message = backendError.non_field_errors.join(' ');
                } else {
                    const firstError = Object.values(backendError)[0];
                    if (Array.isArray(firstError)) {
                        message = firstError.join(' ');
                    }
                }
            }

            alert(message);
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">Tasks Board</h2>
            </div>

            <DndContext
                sensors={sensors}
                collisionDetection={closestCorners}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {COLUMNS.map(colId => (
                        <Column key={colId} id={colId} tasks={tasks.filter(t => t.status === colId)}>
                            {tasks.filter(t => t.status === colId).map(task => (
                                <DraggableTaskCard key={task.id} task={task} />
                            ))}
                        </Column>
                    ))}
                </div>

                <DragOverlay>
                    {activeTask ? <DraggableTaskCard task={activeTask} /> : null}
                </DragOverlay>
            </DndContext>

            <Modal
                isOpen={showWarning}
                onClose={() => setShowWarning(false)}
                title="Operation Restricted"
            >
                <div className="space-y-4">
                    <p className="text-red-600">
                        ⚠️ You cannot update tasks outside of working hours (9:00 AM - 6:00 PM).
                    </p>
                    <div className="flex justify-end">
                        <Button onClick={() => setShowWarning(false)}>Understood</Button>
                    </div>
                </div>
            </Modal>
        </div>
    );
}
