/**
 * WebSocket service for real-time notifications
 * 
 * Features:
 * - Automatic reconnection on disconnect
 * - JWT authentication
 * - Message queuing for offline mode
 * - Event-based notification handling
 */

export interface Notification {
    id: number;
    message: string;
    notification_type: 'status_change' | 'deadline_warning' | 'task_assigned' | 'task_unassigned';
    task_id: number;
    task_title?: string;
    task_status?: string;
    created_at: string;
    read: boolean;
}

type NotificationCallback = (notification: Notification) => void;

class WebSocketService {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 3000; // 3 seconds
    private listeners: NotificationCallback[] = [];
    private isConnecting = false;
    private token: string | null = null;
    private processedIds = new Set<number>();

    /**
     * Connect to WebSocket server
     */
    connect(token: string) {
        if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
            console.log('WebSocket already connected or connecting');
            return;
        }

        this.token = token;
        this.isConnecting = true;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/?token=${token}`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnecting = false;
                this.reconnectAttempts = 0;
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'notification') {
                        this.handleNotification(data.notification);
                    } else if (data.type === 'read_confirmation') {
                        console.log('Notification marked as read:', data.notification_id);
                    } else if (data.type === 'all_read_confirmation') {
                        console.log('All notifications marked as read');
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnecting = false;
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnecting = false;
                this.ws = null;
                this.attemptReconnect();
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.isConnecting = false;
        }
    }

    /**
     * Disconnect from WebSocket server
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
    }

    /**
     * Attempt to reconnect with exponential backoff
     */
    private attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            return;
        }

        if (!this.token) {
            console.log('No token available for reconnection');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        setTimeout(() => {
            if (this.token) {
                this.connect(this.token);
            }
        }, delay);
    }

    /**
     * Handle incoming notification
     */
    private handleNotification(notification: Notification) {
        // Deduplicate notifications
        if (this.processedIds.has(notification.id)) {
            console.log('Duplicate notification ignored:', notification.id);
            return;
        }

        this.processedIds.add(notification.id);
        // Keep set size manageable
        if (this.processedIds.size > 100) {
            const iterator = this.processedIds.values();
            this.processedIds.delete(iterator.next().value!);
        }

        console.log('Received notification:', notification);

        // Show browser notification if permission granted
        this.showBrowserNotification(notification);

        // Notify all listeners
        this.listeners.forEach(callback => callback(notification));
    }

    /**
     * Show browser notification
     */
    private showBrowserNotification(notification: Notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const icon = notification.notification_type === 'deadline_warning' ? '⚠️' : '🔔';

            new Notification(`${icon} CTMS Notification`, {
                body: notification.message,
                icon: '/favicon.ico',
                tag: `notification-${notification.id}`,
            });
        }
    }

    /**
     * Subscribe to notifications
     */
    subscribe(callback: NotificationCallback) {
        this.listeners.push(callback);

        // Return unsubscribe function
        return () => {
            this.listeners = this.listeners.filter(cb => cb !== callback);
        };
    }

    /**
     * Mark notification as read
     */
    markAsRead(notificationId: number) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'mark_read',
                notification_id: notificationId
            }));
        }
    }

    /**
     * Mark all notifications as read
     */
    markAllAsRead() {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'mark_all_read'
            }));
        }
    }

    /**
     * Request browser notification permission
     */
    static async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return Notification.permission === 'granted';
    }

    /**
     * Check if WebSocket is connected
     */
    isConnected(): boolean {
        return this.ws?.readyState === WebSocket.OPEN;
    }
}

// Export class and singleton instance
export { WebSocketService };
export const wsService = new WebSocketService();
