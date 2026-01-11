import api from '../lib/axios';
import type { AuthResponse, User } from '../types';

export const authApi = {
    register: async (data: any) => {
        return api.post<User>('/auth/register/', data);
    },
    verifyEmail: async (data: { token: string }) => {
        return api.post('/auth/verify-email/', data);
    },
    login: async (data: any) => {
        const response = await api.post<AuthResponse>('/auth/login/', data);
        // Only access token in response, refresh_token is in HTTP-only cookie
        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
        }
        return response;
    },
    logout: async () => {
        // Call backend logout to clear cookies
        try {
            await api.post('/auth/logout/', {});
        } catch (error) {
            console.error('Logout API call failed', error);
        }
        // Clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    },
    getCurrentUser: async () => {
        return api.get<User>('/auth/users/me/');
    }
};
