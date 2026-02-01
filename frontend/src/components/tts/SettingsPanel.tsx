"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
// In a real app, this would use a Select component. Using native select for MVP.
import { Voice } from '@/services/tts.service';
import { INDIAN_LANGUAGES } from '@/constants/languages';

interface SettingsPanelProps {
    voices: Voice[];
    selectedVoiceId: string;
    onVoiceChange: (id: string) => void;
    settings: {
        stability: number;
        similarity: number;
    };
    onSettingsChange: (key: 'stability' | 'similarity', val: number) => void;
    selectedLanguage: string;
    onLanguageChange: (code: string) => void;
    selectedVoiceAge: 'adult' | 'child' | 'elder';
    onVoiceAgeChange: (age: 'adult' | 'child' | 'elder') => void;
    selectedProsodyPreset: string;
    onProsodyPresetChange: (preset: string) => void;
}

export function SettingsPanel({
    voices,
    selectedVoiceId,
    onVoiceChange,
    settings,
    onSettingsChange,
    selectedLanguage = 'en',
    onLanguageChange,
    selectedVoiceAge = 'adult',
    onVoiceAgeChange,
    selectedProsodyPreset = 'neutral',
    onProsodyPresetChange
}: SettingsPanelProps) {
    return (
        <div className="space-y-6">
            <Card accent="orange">
                <CardHeader>
                    <CardTitle className="text-lg">Voice</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div>
                            <label className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                Language
                            </label>
                            <select
                                className="w-full rounded-lg border border-white/10 bg-black/50 px-4 py-2.5 text-sm transition-all focus-visible:outline-none focus-visible:border-accent-orange/50 focus-visible:ring-1 focus-visible:ring-accent-orange/20 text-slate-200"
                                value={selectedLanguage}
                                onChange={(e) => onLanguageChange(e.target.value)}
                                suppressHydrationWarning
                            >
                                {INDIAN_LANGUAGES.map((lang) => (
                                    <option key={lang.code} value={lang.code} className="bg-[#0b0f14] text-slate-200">
                                        {lang.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                Engine Voice
                            </label>
                            <select
                                className="w-full rounded-lg border border-white/10 bg-black/50 px-4 py-2.5 text-sm transition-all focus-visible:outline-none focus-visible:border-accent-orange/50 focus-visible:ring-1 focus-visible:ring-accent-orange/20 text-slate-200"
                                value={selectedVoiceId}
                                onChange={(e) => onVoiceChange(e.target.value)}
                                suppressHydrationWarning
                            >
                                <option value="" className="bg-[#0b0f14] text-slate-200">System Choice...</option>
                                {voices
                                    .filter(v => v.language === selectedLanguage)
                                    .map((voice) => (
                                        <option key={voice.voice_id} value={voice.voice_id} className="bg-[#0b0f14] text-slate-200">
                                            {voice.name} [{voice.accent}]
                                        </option>
                                    ))}
                            </select>
                        </div>
                        <div>
                            <label className="mb-3 block text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                Age Profile
                            </label>
                            <div className="grid grid-cols-3 gap-2">
                                <button
                                    type="button"
                                    onClick={() => onVoiceAgeChange('adult')}
                                    suppressHydrationWarning
                                    className={`rounded-lg border py-2.5 text-[10px] font-bold tracking-widest uppercase transition-all duration-200 ${selectedVoiceAge === 'adult'
                                        ? 'border-accent-orange bg-accent-orange/10 text-accent-orange glow-orange'
                                        : 'border-white/5 bg-white/5 text-slate-500 hover:text-slate-300'
                                        }`}
                                >
                                    Adult
                                </button>
                                <button
                                    type="button"
                                    onClick={() => onVoiceAgeChange('child')}
                                    suppressHydrationWarning
                                    className={`rounded-lg border py-2.5 text-[10px] font-bold tracking-widest uppercase transition-all duration-200 ${selectedVoiceAge === 'child'
                                        ? 'border-accent-orange bg-accent-orange/10 text-accent-orange glow-orange'
                                        : 'border-white/5 bg-white/5 text-slate-500 hover:text-slate-300'
                                        }`}
                                >
                                    Child
                                </button>
                                <button
                                    type="button"
                                    onClick={() => onVoiceAgeChange('elder')}
                                    suppressHydrationWarning
                                    className={`rounded-lg border py-2.5 text-[10px] font-bold tracking-widest uppercase transition-all duration-200 ${selectedVoiceAge === 'elder'
                                        ? 'border-accent-orange bg-accent-orange/10 text-accent-orange glow-orange'
                                        : 'border-white/5 bg-white/5 text-slate-500 hover:text-slate-300'
                                        }`}
                                >
                                    Elder
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                Narrative Style
                            </label>
                            <select
                                value={selectedProsodyPreset}
                                onChange={(e) => onProsodyPresetChange(e.target.value)}
                                className="w-full rounded-lg border border-white/10 bg-black/50 px-4 py-2.5 text-sm transition-all focus-visible:outline-none focus-visible:border-accent-orange/50 focus-visible:ring-1 focus-visible:ring-accent-orange/20 text-slate-200"
                            >
                                <option value="neutral" className="bg-[#0b0f14]">Storyteller (Default)</option>
                                <option value="storytelling" className="bg-[#0b0f14]">Deep Narrative</option>
                                <option value="calm" className="bg-[#0b0f14]">Whisper / Calm</option>
                                <option value="news" className="bg-[#0b0f14]">Broadcast / News</option>
                            </select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card accent="purple">
                <CardHeader>
                    <CardTitle className="text-lg">Settings</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-6">
                        <div>
                            <div className="mb-4 flex items-center justify-between">
                                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Stability</label>
                                <span className="text-[10px] font-mono text-accent-orange font-bold px-2 py-0.5 rounded bg-accent-orange/10">{(settings.stability * 100).toFixed(0)}%</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.05"
                                value={settings.stability}
                                onChange={(e) => onSettingsChange('stability', parseFloat(e.target.value))}
                                className="h-1.5 w-full appearance-none rounded-full bg-white/5 accent-accent-orange cursor-pointer"
                            />
                            <p className="mt-3 text-[10px] text-slate-600 font-medium italic">Adjust for emotional variance.</p>
                        </div>

                        <div>
                            <div className="mb-4 flex items-center justify-between">
                                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Clarity</label>
                                <span className="text-[10px] font-mono text-accent-lime font-bold px-2 py-0.5 rounded bg-accent-lime/10">{(settings.similarity * 100).toFixed(0)}%</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.05"
                                value={settings.similarity}
                                onChange={(e) => onSettingsChange('similarity', parseFloat(e.target.value))}
                                className="h-1.5 w-full appearance-none rounded-full bg-white/5 accent-accent-lime cursor-pointer"
                            />
                            <p className="mt-3 text-[10px] text-slate-600 font-medium italic">Higher values ensure voice consistency.</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
