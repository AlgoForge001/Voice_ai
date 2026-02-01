"use client";

import React from 'react';
import { cn } from '@/utils/cn';
import { Button } from '@/components/ui/Button';

interface TextEditorProps {
    value: string;
    onChange: (value: string) => void;
    maxLength?: number;
    onGenerate: () => void;
    isGenerating?: boolean;
    isQuotaExhausted?: boolean;
}

export function TextEditor({
    value,
    onChange,
    maxLength = 5000,
    onGenerate,
    isGenerating,
    isQuotaExhausted
}: TextEditorProps) {

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
            if (value.trim()) onGenerate();
        }
    };

    return (
        <div className="flex h-full flex-col glass-card border-none accent-border-orange">
            <div className="flex-1 p-8">
                <textarea
                    className="h-full w-full resize-none border-0 bg-transparent text-lg leading-relaxed text-slate-200 placeholder:text-slate-600 focus:ring-0 font-sans selection:bg-accent-orange/30"
                    placeholder="Type or paste text here to generate speech..."
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    maxLength={maxLength}
                    onKeyDown={handleKeyDown}
                />
            </div>
            <div className="flex items-center justify-between border-t border-white/5 bg-white/[0.02] px-8 py-4">
                <div className="flex flex-col">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Resource Utilization</span>
                    <span className="text-xs font-mono text-slate-400 mt-1">
                        {value.length.toLocaleString()} / {maxLength.toLocaleString()} CHARS
                    </span>
                </div>
                <div className="flex items-center gap-6">
                    {isQuotaExhausted && (
                        <div className="flex items-center gap-2">
                            <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
                            <span className="text-[10px] font-bold uppercase tracking-widest text-red-500">
                                Quota Depleted
                            </span>
                        </div>
                    )}
                    <Button
                        onClick={onGenerate}
                        disabled={!value.trim() || isGenerating || isQuotaExhausted}
                        isLoading={isGenerating}
                        variant="default"
                        className="min-w-[180px]"
                    >
                        Generate Audio
                    </Button>
                </div>
            </div>
        </div>
    );
}
