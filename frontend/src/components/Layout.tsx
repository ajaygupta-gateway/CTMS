import { useAuth } from '../context/AuthContext';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, LogOut, User } from 'lucide-react';
import { Button } from './ui/button';

export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
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
                    <Link to="/" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
                        <LayoutDashboard size={20} />
                        <span>Dashboard</span>
                    </Link>
                    <Link to="/tasks" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
                        <CheckSquare size={20} />
                        <span>Tasks</span>
                    </Link>
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
            <main className="flex-1 bg-background p-6 overflow-auto">
                <Outlet />
            </main>
        </div>
    );
}
