import { apiClient } from './apiClient';

export interface Voice {
    voice_id: string;
    name: string;
    accent: string;
    gender: 'male' | 'female';
    language?: string;
    preview_url?: string;
    labels?: Record<string, string>; // e.g. { age: 'young', description: 'neutral' }
}

export interface TTSRequest {
    text: string;
    voice_id: string;
    model_id?: string; // 'eleven_monolingual_v1'
    language?: string; // e.g. 'en', 'hi', 'ta'
    voice_age?: 'adult' | 'child' | 'elder';
    prosody_preset?: string;
    settings?: {
        stability: number;
        similarity_boost: number;
    };
}

export interface TTSJob {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    audio_url?: string;
    created_at: string;
    text_snippet: string;
    voice_name?: string;
}

export const ttsService = {
    // Get available voices
    getVoices: async (): Promise<Voice[]> => {
        try {
            return await apiClient.get<Voice[]>('/tts/voices');
        } catch (error) {
            console.error('Error fetching voices:', error);
            throw error;
        }
    },

    // Synthesize text
    generate: async (payload: TTSRequest): Promise<TTSJob> => {
        try {
            return await apiClient.post<TTSJob>('/tts/generate', payload);
        } catch (error) {
            console.error('Error generating TTS:', error);
            throw error;
        }
    },

    // Poll for job status (or get single job)
    getJobStatus: async (jobId: string): Promise<TTSJob> => {
        try {
            return await apiClient.get<TTSJob>(`/tts/jobs/${jobId}`);
        } catch (error) {
            console.error('Error getting job status:', error);
            throw error;
        }
    },

    // Get user's generation history
    getHistory: async (page: number = 1, limit: number = 20): Promise<{ data: TTSJob[], total: number }> => {
        try {
            return await apiClient.get<{ data: TTSJob[], total: number }>(`/tts/history?page=${page}&limit=${limit}`);
        } catch (error) {
            console.error('Error fetching history:', error);
            throw error;
        }
    }
};
