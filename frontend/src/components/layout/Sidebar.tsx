"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/utils/cn';
import { Mic2, LayoutDashboard, Settings, User, CreditCard } from 'lucide-react';

const navItems = [
    { name: 'Text to Speech', href: '/dashboard/tts', icon: Mic2 },
    { name: 'Voice Library', href: '/dashboard/voices', icon: User }, // Placeholder
    { name: 'History', href: '/dashboard/history', icon: LayoutDashboard },
    { name: 'Billing', href: '/dashboard/billing', icon: CreditCard },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="hidden h-screen w-64 flex-col glass-panel border-r-0 md:flex">
            <div className="flex h-16 items-center px-6 border-b border-white/5">
                <span className="text-xl font-bold tracking-widest text-accent-orange uppercase italic">VoiceAI</span>
            </div>
            <nav className="flex-1 space-y-1 p-4">
                {navItems.map((item) => {
                    const isActive = pathname.startsWith(item.href);
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "group relative flex items-center rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200",
                                isActive
                                    ? "bg-white/5 text-white shadow-lg shadow-black/20 accent-border-l-orange"
                                    : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                            )}
                        >
                            {isActive && (
                                <div className="absolute left-0 h-4 w-1 bg-accent-orange rounded-r-full" />
                            )}
                            <item.icon className={cn(
                                "mr-3 h-5 w-5 flex-shrink-0 transition-colors",
                                isActive ? "text-accent-orange" : "text-slate-500 group-hover:text-slate-300"
                            )} />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>
            <div className="p-4 border-t border-white/5">
                <div className="rounded-lg bg-accent-orange/5 border border-accent-orange/10 border-l-accent-orange/50 p-4 accent-border-l-orange">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-accent-orange">Free Plan</span>
                        <div className="h-1.5 w-1.5 rounded-full bg-accent-orange glow-orange" />
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full w-2/3 bg-accent-orange" />
                    </div>
                    <p className="mt-2 text-[10px] text-slate-500 font-medium">10,000 / 15,000 chars</p>
                </div>
            </div>
        </aside>
    );
}
