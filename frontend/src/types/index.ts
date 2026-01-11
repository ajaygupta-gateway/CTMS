export type UserRole = 'manager' | 'developer' | 'auditor';

export interface User {
    id: number;
    username: string;
    email: string;
    role: UserRole;
    timezone: string;
    email_verified: boolean;
}

export interface AuthResponse {
    refresh: string;
    access: string;
    user: User;
}

export type TaskStatus = 'pending' | 'in_progress' | 'blocked' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

export interface Task {
    id: number;
    title: string;
    description: string;
    assigned_to: number;
    assigned_to_user?: string; // Read-only
    status: TaskStatus;
    priority: TaskPriority;
    estimated_hours: number;
    actual_hours: number | null;
    deadline: string; // ISO string with time
    tags: number[]; // Tag IDs
    created_by: number;
    created_by_user?: string; // Read-only
    parent_task: number | null;
    priority_escalated: boolean;
    created_at: string;
    updated_at: string;
}

export interface TaskCreatePayload {
    title: string;
    description: string;
    assigned_to?: number;
    status?: TaskStatus;
    priority?: TaskPriority;
    estimated_hours?: number;
    actual_hours?: number | null;
    deadline?: string;
    tags?: number[];
    parent_task?: number | null;
    priority_escalated?: boolean;
}

export interface TaskUpdatePayload extends Partial<TaskCreatePayload> {
    actual_hours?: number;
}

export interface BulkUpdatePayload {
    task_ids: number[];
    status: TaskStatus;
}

export interface AnalyticsData {
    my_tasks: {
        total: number;
        completed: number;
        pending: number;
    };
    team_tasks: {
        total: number;
        completed: number;
    };
    efficiency_score: number;
}
