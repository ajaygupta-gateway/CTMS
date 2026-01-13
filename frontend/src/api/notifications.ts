import api from '../lib/axios';
import type { Notification } from '../lib/websocket';

export const notificationsApi = {
    /**
     * Get all notifications for current user
     */
    getNotifications: () => api.get<Notification[]>('/notifications/'),

    /**
     * Get a specific notification
     */
    getNotification: (id: number) => api.get<Notification>(`/notifications/${id}/`),

    /**
     * Mark a notification as read
     */
    markAsRead: (id: number) => api.post(`/notifications/${id}/mark_read/`),

    /**
     * Mark all notifications as read
     */
    markAllAsRead: () => api.post('/notifications/mark_all_read/'),

    /**
     * Get count of unread notifications
     */
    getUnreadCount: () => api.get<{ count: number }>('/notifications/unread_count/'),
};
