import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { wsService, WebSocketService, type Notification } from '../lib/websocket';
import { notificationsApi } from '../api/notifications';
import { useAuth } from './AuthContext';



interface NotificationContextType {
    notifications: Notification[];
    unreadCount: number;
    addNotification: (notification: Notification) => void;
    markAsRead: (id: number) => void;
    markAllAsRead: () => void;
    clearNotifications: () => void;
    isConnected: boolean;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, user } = useAuth();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isConnected, setIsConnected] = useState(false);

    /**
     * Load initial notifications from API
     */
    const loadNotifications = useCallback(async () => {
        try {
            const response = await notificationsApi.getNotifications();
            setNotifications(response.data);

            // Update unread count
            const unread = response.data.filter(n => !n.read).length;
            setUnreadCount(unread);
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }, []);

    /**
     * Load unread count
     */
    const loadUnreadCount = useCallback(async () => {
        try {
            const response = await notificationsApi.getUnreadCount();
            setUnreadCount(response.data.count);
        } catch (error) {
            console.error('Failed to load unread count:', error);
        }
    }, []);

    /**
     * Connect to WebSocket when authenticated
     */
    useEffect(() => {
        if (isAuthenticated && user) {
            const token = localStorage.getItem('access_token');
            if (token) {
                // Connect to WebSocket
                wsService.connect(token);
                setIsConnected(true);

                // Request browser notification permission
                WebSocketService.requestNotificationPermission();


                // Load initial notifications
                loadNotifications();
                loadUnreadCount();

                // Subscribe to new notifications
                const unsubscribe = wsService.subscribe((notification) => {
                    addNotification(notification);
                });

                return () => {
                    unsubscribe();
                    wsService.disconnect();
                    setIsConnected(false);
                };
            }
        }
    }, [isAuthenticated, user, loadNotifications, loadUnreadCount]);

    /**
     * Add a new notification
     */
    const addNotification = useCallback((notification: Notification) => {
        setNotifications(prev => {
            // Deduplicate to avoid showing same notification twice
            if (prev.some(n => n.id === notification.id)) return prev;
            return [notification, ...prev];
        });
        if (!notification.read) {
            setUnreadCount(prev => prev + 1);
        }
    }, []);

    /**
     * Mark notification as read
     */
    const markAsRead = useCallback(async (id: number) => {
        try {
            // Optimistic update
            setNotifications(prev =>
                prev.map(n => (n.id === id ? { ...n, read: true } : n))
            );
            setUnreadCount(prev => Math.max(0, prev - 1));

            // Send to API
            await notificationsApi.markAsRead(id);

            // Send to WebSocket
            wsService.markAsRead(id);
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
            // Reload notifications on error
            loadNotifications();
        }
    }, [loadNotifications]);

    /**
     * Mark all notifications as read
     */
    const markAllAsRead = useCallback(async () => {
        try {
            // Optimistic update
            setNotifications(prev =>
                prev.map(n => ({ ...n, read: true }))
            );
            setUnreadCount(0);

            // Send to API
            await notificationsApi.markAllAsRead();

            // Send to WebSocket
            wsService.markAllAsRead();
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
            // Reload notifications on error
            loadNotifications();
        }
    }, [loadNotifications]);

    /**
     * Clear all notifications
     */
    const clearNotifications = useCallback(() => {
        setNotifications([]);
        setUnreadCount(0);
    }, []);

    const value: NotificationContextType = {
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        markAllAsRead,
        clearNotifications,
        isConnected,
    };

    return (
        <NotificationContext.Provider value={value}>
            {children}
        </NotificationContext.Provider>
    );
}

export function useNotifications() {
    const context = useContext(NotificationContext);
    if (context === undefined) {
        throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
}
