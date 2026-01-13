import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';
import VerifyEmailPage from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import TasksList from './pages/Tasks/TasksList';
import TaskForm from './pages/Tasks/TaskForm';
import BulkUpdate from './pages/Tasks/BulkUpdate';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import CaptchaModal from './components/CaptchaModal';
import { NotificationProvider } from './context/NotificationContext';

function App() {
    return (
        <BrowserRouter>
            <NotificationProvider>
                <CaptchaModal />
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/verify-email" element={<VerifyEmailPage />} />

                    <Route element={<ProtectedRoute />}>
                        <Route element={<Layout />}>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/tasks" element={<TasksList />} />
                            <Route path="/tasks/new" element={<TaskForm />} />
                            <Route path="/tasks/bulk-update" element={<BulkUpdate />} />
                            <Route path="/tasks/:id" element={<TaskForm />} />
                        </Route>
                    </Route>

                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </NotificationProvider>
        </BrowserRouter>
    );
}

export default App;
