"use client";

import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Button } from '@/components/ui/Button';
import { Play, Pause, Download, Mic2 } from 'lucide-react';

interface WaveformPlayerProps {
    audioUrl?: string; // If undefined, show placeholder
    height?: number;
}

export function WaveformPlayer({ audioUrl, height = 60 }: WaveformPlayerProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const wavesurfer = useRef<WaveSurfer | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        if (!containerRef.current || !audioUrl) return;

        if (wavesurfer.current) {
            wavesurfer.current.destroy();
        }

        wavesurfer.current = WaveSurfer.create({
            container: containerRef.current,
            waveColor: '#94a3b8',
            progressColor: '#2563eb',
            cursorColor: '#2563eb',
            barWidth: 2,
            barGap: 3,
            height: height,
            normalize: true,
            url: audioUrl,
        });

        wavesurfer.current.on('ready', () => {
            setIsReady(true);
        });

        wavesurfer.current.on('finish', () => {
            setIsPlaying(false);
        });

        return () => {
            wavesurfer.current?.destroy();
        };
    }, [audioUrl, height]);

    const togglePlay = () => {
        if (wavesurfer.current) {
            if (isPlaying) {
                wavesurfer.current.pause();
            } else {
                wavesurfer.current.play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    const handleDownload = () => {
        if (audioUrl) {
            const a = document.createElement('a');
            a.href = audioUrl;
            a.download = `generated-${Date.now()}.mp3`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    }

    if (!audioUrl) {
        return (
            <div className="flex h-32 items-center justify-center rounded-xl border border-dashed border-white/5 bg-white/[0.02] text-slate-600">
                <div className="flex flex-col items-center gap-3">
                    <div className="h-10 w-10 rounded-full border border-white/5 flex items-center justify-center">
                        <Mic2 className="h-4 w-4 opacity-20" />
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-widest">Awaiting Generation Signal</span>
                </div>
            </div>
        )
    }

    return (
        <div className="glass-card border-none p-6">
            <div className="mb-6 flex items-center justify-between">
                <div className="flex flex-col">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Audio Waveform</span>
                    <span className="text-xs font-mono text-accent-lime uppercase mt-1">Ready for Broadcast</span>
                </div>
                <div className="h-2 w-2 rounded-full bg-accent-lime glow-lime" />
            </div>

            <div ref={containerRef} className="mb-6 w-full opacity-80" />

            <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <Button
                    size="sm"
                    variant="default"
                    className="gap-3 min-w-[120px]"
                    onClick={togglePlay}
                    disabled={!isReady}
                >
                    {isPlaying ? <Pause className="h-4 w-4 fill-current" /> : <Play className="h-4 w-4 fill-current" />}
                    {isPlaying ? "HALT" : "PLAY"}
                </Button>

                <Button size="icon" variant="outline" onClick={handleDownload} className="rounded-full">
                    <Download className="h-4 w-4" />
                </Button>
            </div>
        </div>
    );
}
