import { useState } from 'react';
import { Bell } from 'lucide-react';
import { useNotifications } from '../context/NotificationContext';
import NotificationPanel from './NotificationPanel';


/**
 * Notification bell icon with badge showing unread count
 */
export default function NotificationBell() {
    const { unreadCount } = useNotifications();
    const [showPanel, setShowPanel] = useState(false);

    return (
        <div className="relative">
            <button
                onClick={() => setShowPanel(!showPanel)}
                className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Notifications"
            >
                <Bell className="w-6 h-6" />
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full animate-pulse">
                        {unreadCount > 99 ? '99+' : unreadCount}
                    </span>
                )}
            </button>

            {showPanel && (
                <NotificationPanel onClose={() => setShowPanel(false)} />
            )}
        </div>
    );
}
