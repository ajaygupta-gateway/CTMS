import { useAuth } from '../context/AuthContext';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, LogOut, User, ListChecks } from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import NotificationBell from './NotificationBell';


export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Helper function to check if a route is active
    const isActive = (path: string) => {
        if (path === '/') {
            return location.pathname === '/';
        }
        return location.pathname.startsWith(path);
    };

    return (
        <div className="flex min-h-screen flex-col md:flex-row">
            {/* Sidebar */}
            <aside className="w-full bg-slate-900 text-white md:w-64 md:min-h-screen flex-shrink-0">
                <div className="p-4 border-b border-slate-800">
                    <h1 className="text-xl font-bold">CTMS</h1>
                    <p className="text-sm text-slate-400">Task Management</p>
                </div>
                <nav className="p-4 space-y-2">
                    {/* Dashboard Link */}
                    <Link
                        to="/"
                        className={cn(
                            "flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 relative group",
                            isActive('/')
                                ? "bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/50 font-semibold"
                                : "hover:bg-slate-800 text-slate-300 hover:text-white"
                        )}
                    >
                        {isActive('/') && (
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                        )}
                        <LayoutDashboard size={20} className={cn(isActive('/') && "animate-pulse")} />
                        <span>Dashboard</span>
                    </Link>

                    {/* Tasks Link */}
                    <Link
                        to="/tasks"
                        className={cn(
                            "flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 relative group",
                            isActive('/tasks') && !location.pathname.includes('bulk-update')
                                ? "bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/50 font-semibold"
                                : "hover:bg-slate-800 text-slate-300 hover:text-white"
                        )}
                    >
                        {isActive('/tasks') && !location.pathname.includes('bulk-update') && (
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                        )}
                        <CheckSquare size={20} className={cn(isActive('/tasks') && !location.pathname.includes('bulk-update') && "animate-pulse")} />
                        <span>Tasks</span>
                    </Link>

                    {/* Bulk Update Link */}
                    {user?.role !== 'auditor' && (
                        <Link
                            to="/tasks/bulk-update"
                            className={cn(
                                "flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 relative group",
                                location.pathname.includes('bulk-update')
                                    ? "bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/50 font-semibold"
                                    : "hover:bg-slate-800 text-slate-300 hover:text-white"
                            )}
                        >
                            {location.pathname.includes('bulk-update') && (
                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" />
                            )}
                            <ListChecks size={20} className={cn(location.pathname.includes('bulk-update') && "animate-pulse")} />
                            <span>Bulk Update</span>
                        </Link>
                    )}
                </nav>
                <div className="p-4 border-t border-slate-800 mt-auto">
                    <div className="flex items-center space-x-2 mb-2">
                        <User size={20} />
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{user?.username}</p>
                            <p className="text-xs text-slate-400 capitalize">{user?.role}</p>
                        </div>
                    </div>
                    <Button variant="destructive" className="w-full justify-start" onClick={handleLogout}>
                        <LogOut size={20} className="mr-2" />
                        Logout
                    </Button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 bg-background overflow-auto">
                {/* Header with Notification Bell */}
                <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4">
                    <div className="flex items-center justify-end">
                        <NotificationBell />
                    </div>
                </div>

                {/* Page Content */}
                <div className="p-6">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
