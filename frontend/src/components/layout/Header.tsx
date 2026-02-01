"use client";

import React from 'react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/context/AuthContext';
import { Loader2, Bell, HelpCircle } from 'lucide-react';

export function Header() {
    const { user, logout, loading } = useAuth();

    return (
        <header className="flex h-16 items-center justify-between glass-panel border-b border-white/5 border-l-0 px-8 sticky top-0 z-50">
            <div className="flex items-center">
                <h1 className="text-sm font-bold tracking-widest text-slate-400 uppercase">
                    System / <span className="text-white">Dashboard</span>
                </h1>
            </div>
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-3 pr-6 border-r border-white/5">
                    <button className="text-slate-500 hover:text-white transition-colors">
                        <Bell className="h-4 w-4" />
                    </button>
                    <button className="text-slate-500 hover:text-white transition-colors">
                        <HelpCircle className="h-4 w-4" />
                    </button>
                </div>

                <div className="flex items-center gap-4">
                    {loading ? (
                        <Loader2 className="h-4 w-4 animate-spin text-accent-orange" />
                    ) : user ? (
                        <div className="flex items-center gap-3">
                            <div className="flex flex-col items-end">
                                <span className="text-xs font-bold text-white leading-none">
                                    {user.email?.split('@')[0]}
                                </span>
                                <span className="text-[10px] text-accent-lime font-medium mt-1">PRO ACCOUNT</span>
                            </div>
                            <div className="h-8 w-8 rounded-full border border-accent-lime/20 bg-accent-lime/5 flex items-center justify-center text-accent-lime text-xs font-bold">
                                {user.email?.[0].toUpperCase()}
                            </div>
                            <Button variant="ghost" size="sm" onClick={logout} className="text-slate-500 hover:text-white ml-2">
                                Sign out
                            </Button>
                        </div>
                    ) : (
                        <Button variant="default" size="sm" className="bg-accent-orange hover:bg-accent-orange/80 text-black font-bold">Log in</Button>
                    )}
                </div>
            </div>
        </header>
    );
}
