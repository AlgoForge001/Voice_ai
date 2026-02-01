import { apiClient } from './apiClient';

export interface User {
    id: string;
    email: string;
    name?: string;
    role: 'user' | 'admin';
    plan: 'free' | 'pro' | 'enterprise';
    credits: number; // For TTS usage
}

export interface AuthResponse {
    token: string;
    user: User;
}

export const authService = {
    login: async (email: string, password: string): Promise<User> => {
        // In a real app, this returns { token, user }. We simulate saving token here.
        const response = await apiClient.post<AuthResponse>('/auth/login', { email, password });
        if (response.token) {
            if (typeof window !== 'undefined') {
                localStorage.setItem('auth_token', response.token);
            }
        }
        return response.user;
    },

    signup: async (email: string, password: string, name?: string): Promise<User> => {
        const response = await apiClient.post<AuthResponse>('/auth/signup', { email, password, name });
        if (response.token) {
            if (typeof window !== 'undefined') {
                localStorage.setItem('auth_token', response.token);
            }
        }
        return response.user;
    },

    me: async (): Promise<User> => {
        try {
            return await apiClient.get<User>('/auth/me');
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    },

    logout: () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
            // Force reload or redirect could handle state clearing
            window.location.href = '/login';
        }
    }
};
