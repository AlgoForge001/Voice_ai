"use client";

import React, { useEffect, useState } from 'react';
import { TextEditor } from '@/components/tts/TextEditor';
import { SettingsPanel } from '@/components/tts/SettingsPanel';
import { WaveformPlayer } from '@/components/tts/WaveformPlayer';
import { ttsService, Voice } from '@/services/tts.service';
import { useAuth } from '@/context/AuthContext';

export default function TTSPage() {
    const { user } = useAuth();
    const [text, setText] = useState('');
    const [selectedVoice, setSelectedVoice] = useState('');
    const [selectedLanguage, setSelectedLanguage] = useState('en');
    const [selectedVoiceAge, setSelectedVoiceAge] = useState<'adult' | 'child' | 'elder'>('adult');
    const [selectedProsodyPreset, setSelectedProsodyPreset] = useState('neutral');
    const [voices, setVoices] = useState<Voice[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [audioUrl, setAudioUrl] = useState<string | undefined>(undefined);
    const [settings, setSettings] = useState({
        stability: 0.5,
        similarity: 0.75,
    });

    // Fetch voices on mount
    useEffect(() => {
        const loadVoices = async () => {
            try {
                const data = await ttsService.getVoices();
                if (data && data.length > 0) {
                    setVoices(data);
                    setSelectedVoice(data[0].voice_id);
                } else {
                    // Fallback voices if API returns empty
                    const fallbackVoices = [
                        { voice_id: '1', name: 'Rachel', accent: 'American', gender: 'female' as const },
                        { voice_id: '2', name: 'Drew', accent: 'British', gender: 'male' as const },
                        { voice_id: '3', name: 'Clyde', accent: 'American', gender: 'male' as const },
                        { voice_id: '4', name: 'Mimi', accent: 'Australian', gender: 'female' as const },
                    ];
                    setVoices(fallbackVoices);
                    setSelectedVoice('1');
                }
            } catch (err) {
                console.error("Failed to load voices:", err);
                // Use fallback voices on error
                const fallbackVoices = [
                    { voice_id: '1', name: 'Rachel', accent: 'American', gender: 'female' as const },
                    { voice_id: '2', name: 'Drew', accent: 'British', gender: 'male' as const },
                    { voice_id: '3', name: 'Clyde', accent: 'American', gender: 'male' as const },
                    { voice_id: '4', name: 'Mimi', accent: 'Australian', gender: 'female' as const },
                ];
                setVoices(fallbackVoices);
                setSelectedVoice('1');
            }
        };
        loadVoices();
    }, []);

    // Auto-select first voice for language when language or voices change
    useEffect(() => {
        if (voices.length > 0) {
            const validVoices = voices.filter(v => v.language === selectedLanguage);
            if (validVoices.length > 0) {
                // If current selected voice is not valid for this language, pick the first one
                if (!validVoices.find(v => v.voice_id === selectedVoice)) {
                    setSelectedVoice(validVoices[0].voice_id);
                }
            } else if (selectedVoice) {
                // No voices for this language but we have a selected voice? Keep it or clear it.
                // For safety, don't clear it yet, but it won't show in the dropdown.
            }
        }
    }, [selectedLanguage, voices, selectedVoice]);

    const handleGenerate = async () => {
        if (!text.trim()) {
            alert("Please enter some text to generate speech");
            return;
        }

        if (!selectedVoice) {
            alert("Please select a voice");
            return;
        }

        setIsGenerating(true);
        setAudioUrl(undefined);

        try {
            // Call backend to create TTS job
            const job = await ttsService.generate({
                text,
                voice_id: selectedVoice,
                language: selectedLanguage,
                voice_age: selectedVoiceAge,
                prosody_preset: selectedProsodyPreset,
                settings: {
                    stability: settings.stability,
                    similarity_boost: settings.similarity
                }
            });

            // Poll for job completion
            const pollInterval = setInterval(async () => {
                try {
                    const jobStatus = await ttsService.getJobStatus(job.job_id);

                    if (jobStatus.status === 'completed') {
                        clearInterval(pollInterval);
                        setAudioUrl(jobStatus.audio_url);
                        setIsGenerating(false);
                    } else if (jobStatus.status === 'failed') {
                        clearInterval(pollInterval);
                        setIsGenerating(false);
                        alert('TTS generation failed. Please try again.');
                    }
                } catch (error) {
                    clearInterval(pollInterval);
                    setIsGenerating(false);
                    console.error("Polling failed", error);
                    alert("Failed to check job status");
                }
            }, 2000); // Poll every 2 seconds

            // Timeout after 2 minutes
            setTimeout(() => {
                clearInterval(pollInterval);
                if (isGenerating) {
                    setIsGenerating(false);
                    alert("Generation timeout. Please try again.");
                }
            }, 120000);

        } catch (error: any) {
            console.error("Generation failed", error);
            console.error("Error details:", {
                message: error?.message,
                status: error?.response?.status,
                statusText: error?.response?.statusText,
                data: error?.response?.data,
                url: error?.response?.url,
                stack: error?.stack
            });

            let errorMessage = "Failed to generate speech. Please try again.";

            // Handle Standardized Quota Error
            if (error?.response?.status === 403 && error?.response?.data?.error === 'INSUFFICIENT_QUOTA') {
                errorMessage = "Quota exhausted. Please upgrade your plan or wait for your daily/monthly reset.";
            } else if (error?.response?.data?.detail) {
                errorMessage = typeof error.response.data.detail === 'string'
                    ? error.response.data.detail
                    : JSON.stringify(error.response.data.detail);
            } else if (error?.response?.data?.message) {
                errorMessage = error.response.data.message;
            } else if (error?.message) {
                errorMessage = error.message;
            } else if (error?.response?.status) {
                errorMessage = `Server error (${error.response.status}). Please try again.`;
            } else {
                errorMessage = "Unable to connect to the server. Please check your connection.";
            }

            alert(errorMessage);
            setIsGenerating(false);
        }
    };

    return (
        <div className="flex h-full flex-col gap-8 lg:flex-row max-w-[1600px] mx-auto animate-in fade-in duration-700">
            <div className="flex flex-1 flex-col gap-8">
                <div className="flex flex-col gap-1">
                    <h2 className="text-2xl font-bold tracking-widest uppercase text-white italic">Acoustic Architect</h2>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em]">Neural Processing Unit / Inference Mode</p>
                </div>

                <div className="flex-1 min-h-[400px]">
                    <TextEditor
                        value={text}
                        onChange={setText}
                        onGenerate={handleGenerate}
                        isGenerating={isGenerating}
                        isQuotaExhausted={user ? user.credits <= 0 : false}
                    />
                </div>
                <div className="flex-none">
                    <WaveformPlayer audioUrl={audioUrl} />
                </div>
            </div>

            <div className="w-full lg:w-96 flex-none">
                <div className="sticky top-24">
                    <SettingsPanel
                        voices={voices}
                        selectedVoiceId={selectedVoice}
                        onVoiceChange={setSelectedVoice}
                        settings={settings}
                        onSettingsChange={(key, val) => setSettings(prev => ({ ...prev, [key]: val }))}
                        selectedLanguage={selectedLanguage}
                        onLanguageChange={setSelectedLanguage}
                        selectedVoiceAge={selectedVoiceAge}
                        onVoiceAgeChange={setSelectedVoiceAge}
                        selectedProsodyPreset={selectedProsodyPreset}
                        onProsodyPresetChange={setSelectedProsodyPreset}
                    />
                </div>
            </div>
        </div>
    );
}
