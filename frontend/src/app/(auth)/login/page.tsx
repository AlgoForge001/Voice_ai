"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';

export default function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            // Import authService
            const { authService } = await import('@/services/auth.service');

            // Call real login API
            const user = await authService.login(email, password);

            // Get the token from localStorage (authService saves it)
            const token = localStorage.getItem('auth_token');

            if (token && user) {
                // Login with real token and user
                login(token, user);
            }
        } catch (error: any) {
            console.error('Login failed:', error);
            alert(error?.message || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle className="text-center">Welcome Back</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Email</label>
                            <Input
                                type="email"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Password</label>
                            <Input
                                type="password"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <Button className="w-full" type="submit" isLoading={loading}>
                            Log in
                        </Button>
                        <p className="text-center text-sm text-slate-500">
                            Don't have an account? <Link href="/signup" className="text-blue-600 hover:underline">Sign up</Link>
                        </p>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
