import api from '../lib/axios';
import type { Task, TaskCreatePayload, TaskUpdatePayload, BulkUpdatePayload, AnalyticsData } from '../types';

export const tasksApi = {
    getTasks: async () => {
        return api.get<Task[]>('/tasks/');
    },
    createTask: async (data: TaskCreatePayload) => {
        return api.post<Task>('/tasks/', data);
    },
    updateTask: async (id: number, data: TaskUpdatePayload) => {
        return api.patch<Task>(`/tasks/${id}/`, data);
    },
    bulkUpdateStatus: async (data: BulkUpdatePayload) => {
        return api.post('/tasks/bulk-update/', data);
    },
    getAnalytics: async () => {
        return api.get<AnalyticsData>('/tasks/analytics/');
    },
    getTask: async (id: number) => {
        return api.get<Task>(`/tasks/${id}/`);
    },
    deleteTask: async (id: number) => {
        return api.delete(`/tasks/${id}/`);
    },
    getUsers: async () => {
        return api.get<any[]>('/auth/users/');
    }
};
