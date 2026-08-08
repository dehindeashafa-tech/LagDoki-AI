'use client';

import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Mic, Square, Send, AlertTriangle, ShieldCheck, Activity, Languages, RefreshCw } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LagDokiDashboard() {
  const [language, setLanguage] = useState<string>('Nigerian Pidgin');
  const [textInput, setTextInput] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [assessment, setAssessment] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Start Mic Recording with explicit Browser MIME Type support
  const startRecording = async () => {
    setError(null);
    audioChunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true }
      });

      // Detect natively supported audio mime type
      let options: MediaRecorderOptions | undefined = undefined;
      if (typeof MediaRecorder !== 'undefined') {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          options = { mimeType: 'audio/webm;codecs=opus' };
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
          options = { mimeType: 'audio/webm' };
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          options = { mimeType: 'audio/mp4' };
        }
      }

      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Emit audio chunks every 250ms to ensure complete buffers
      mediaRecorder.start(250);
      setIsRecording(true);
    } catch (err) {
      setError('Microphone access denied or unavailable.');
    }
  };

  // Stop Mic Recording and Send to API
  const stopRecordingAndSend = () => {
    if (!mediaRecorderRef.current) return;

    const mediaRecorder = mediaRecorderRef.current;

    mediaRecorder.onstop = async () => {
      const mimeType = mediaRecorder.mimeType || 'audio/webm';
      const ext = mimeType.includes('mp4') ? 'mp4' : 'webm';
      
      const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });

      // Clean up microphone tracks
      if (mediaRecorder.stream) {
        mediaRecorder.stream.getTracks().forEach((track) => track.stop());
      }

      if (audioBlob.size < 1000) {
        setError('Recorded audio was too short or empty. Please speak clearly into the microphone.');
        return;
      }

      const formData = new FormData();
      formData.append('file', audioBlob, `voice_input.${ext}`);
      formData.append('language', language);

      setLoading(true);
      setError(null);

      try {
        const response = await axios.post(`${API_BASE_URL}/api/triage/voice`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setAssessment(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error processing audio note.');
      } finally {
        setLoading(false);
      }
    };

    mediaRecorder.stop();
    setIsRecording(false);
  };

  // Submit Text Input
  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/triage`, {
        text_input: textInput,
        language: language,
      });
      setAssessment(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error processing symptom description.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      {/* Header Bar */}
      <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-emerald-500/20 text-emerald-400 p-2 rounded-xl">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wide text-white">LagDoki-AI</h1>
            <p className="text-xs text-slate-400">Multilingual Voice & Text Triage Engine</p>
          </div>
        </div>

        {/* Language Selector */}
        <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
          <Languages className="h-4 w-4 text-emerald-400" />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-transparent text-sm font-medium focus:outline-none text-slate-200 cursor-pointer"
          >
            <option value="Nigerian Pidgin" className="bg-slate-800">Nigerian Pidgin</option>
            <option value="Yoruba" className="bg-slate-800">Yorùbá</option>
            <option value="English" className="bg-slate-800">English</option>
          </select>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-6 grid gap-6">
        {/* Input Interface */}
        <section className="bg-slate-800/50 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur">
          <h2 className="text-lg font-semibold mb-2 text-slate-200">Describe Symptoms</h2>
          <p className="text-sm text-slate-400 mb-6">
            Speak using the voice recorder or type below in your preferred language.
          </p>

          {/* Voice Input Section */}
          <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-700 rounded-xl bg-slate-900/40 mb-6">
            {!isRecording ? (
              <button
                onClick={startRecording}
                disabled={loading}
                className="group flex flex-col items-center space-y-2 text-emerald-400 hover:text-emerald-300 transition"
              >
                <div className="h-16 w-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center group-hover:scale-105 transition">
                  <Mic className="h-8 w-8" />
                </div>
                <span className="text-sm font-medium">Click to Start Voice Recording</span>
              </button>
            ) : (
              <button
                onClick={stopRecordingAndSend}
                className="flex flex-col items-center space-y-2 text-red-400 hover:text-red-300 animate-pulse"
              >
                <div className="h-16 w-16 rounded-full bg-red-500/20 border border-red-500/50 flex items-center justify-center">
                  <Square className="h-8 w-8" />
                </div>
                <span className="text-sm font-medium">Recording... Click to Stop & Send</span>
              </button>
            )}
          </div>

          {/* Text Input Section */}
          <form onSubmit={handleTextSubmit} className="flex gap-2">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="e.g. My head dey split and body dey hot scatter..."
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 text-slate-200"
            />
            <button
              type="submit"
              disabled={loading || !textInput.trim()}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-5 rounded-xl flex items-center justify-center transition font-medium"
            >
              {loading ? <RefreshCw className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-700/50 text-red-300 text-xs rounded-lg">
              {error}
            </div>
          )}
        </section>

        {/* Assessment & Safety Display */}
        {assessment && (
          <section className="bg-slate-800/50 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur">
            {/* Emergency Alert Banner */}
            {assessment.status === 'emergency_alert' ? (
              <div className="bg-red-950/80 border-2 border-red-600 rounded-xl p-5 mb-4 text-red-200 flex items-start space-x-4">
                <AlertTriangle className="h-8 w-8 text-red-500 shrink-0 mt-1" />
                <div>
                  <h3 className="text-lg font-bold text-red-400 mb-1">EMERGENCY RED FLAG DETECTED</h3>
                  <p className="text-sm whitespace-pre-line leading-relaxed">{assessment.assessment}</p>
                </div>
              </div>
            ) : (
              <div className="bg-emerald-950/60 border border-emerald-600/40 rounded-xl p-4 mb-4 text-emerald-200 flex items-center space-x-3">
                <ShieldCheck className="h-6 w-6 text-emerald-400 shrink-0" />
                <div>
                  <h3 className="text-sm font-semibold text-emerald-300">Non-Emergency Assessment Complete</h3>
                  <p className="text-xs text-emerald-400/80">Follow clinical guidance provided below.</p>
                </div>
              </div>
            )}

            {/* Display Transcribed Text if Voice Input */}
            {assessment.transcribed_text && (
              <div className="mb-4 p-3 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Transcribed Voice Note ({assessment.detected_language})
                </span>
                <p className="text-sm italic text-slate-300">"{assessment.transcribed_text}"</p>
              </div>
            )}

            {/* AI Assessment Result */}
            {assessment.status !== 'emergency_alert' && (
              <div className="prose prose-invert max-w-none text-sm text-slate-300 leading-relaxed bg-slate-900/40 p-4 rounded-xl border border-slate-800 whitespace-pre-line">
                {assessment.assessment}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}