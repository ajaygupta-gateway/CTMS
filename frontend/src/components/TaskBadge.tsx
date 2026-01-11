import { differenceInHours, parseISO } from 'date-fns';
import { cn } from '../lib/utils';
import type { TaskPriority } from '../types';

interface TaskBadgeProps {
    priority: TaskPriority;
    deadline?: string | null;
    className?: string;
}

const priorityColors: Record<TaskPriority, string> = {
    low: 'bg-gray-100 text-gray-800 border-gray-200',
    medium: 'bg-blue-100 text-blue-800 border-blue-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-red-100 text-red-800 border-red-200 font-bold',
};

export function TaskBadge({ priority, deadline, className }: TaskBadgeProps) {
    let isUrgent = false;

    if (deadline) {
        const hoursLeft = differenceInHours(parseISO(deadline), new Date());
        if (hoursLeft < 24 && hoursLeft >= 0) {
            isUrgent = true;
        }
    }

    return (
        <span
            className={cn(
                "px-2 py-0.5 rounded-full text-xs border transition-all duration-500",
                priorityColors[priority],
                isUrgent && "animate-pulse ring-2 ring-red-500 ring-offset-1 border-red-500",
                className
            )}
        >
            {priority}
            {isUrgent && " ⚠️"}
        </span>
    );
}
