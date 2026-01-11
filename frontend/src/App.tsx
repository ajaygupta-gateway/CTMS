import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';
import VerifyEmailPage from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import TasksList from './pages/Tasks/TasksList';
import TaskForm from './pages/Tasks/TaskForm';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/verify-email" element={<VerifyEmailPage />} />

                <Route element={<ProtectedRoute />}>
                    <Route element={<Layout />}>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/tasks" element={<TasksList />} />
                        <Route path="/tasks/new" element={<TaskForm />} />
                        <Route path="/tasks/:id" element={<TaskForm />} />
                    </Route>
                </Route>

                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
