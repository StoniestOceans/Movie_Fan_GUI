'use client';

import React, { useState, useEffect, useRef } from 'react';
import ThesysRenderer from './ThesysRenderer';
import ChatInterface from './ChatInterface';

export default function DashboardInterface() {
    const [currentTime, setCurrentTime] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [contextData, setContextData] = useState<any>(null);
    const [subtitleText, setSubtitleText] = useState<string>("");
    // Themes: neutral, action, suspense, emotional
    const [sceneTheme, setSceneTheme] = useState<string>("neutral");

    // Karaoke & Logs State
    const [subtitleHistory, setSubtitleHistory] = useState<string[]>([]);
    const [systemLogs, setSystemLogs] = useState<string[]>([]);

    // Theme Styles Implementation
    const getThemeStyles = () => {
        switch (sceneTheme) {
            case 'action': return 'bg-red-900/20 border-red-500/50 shadow-[0_0_50px_rgba(220,38,38,0.3)]';
            case 'suspense': return 'bg-indigo-900/20 border-indigo-500/50 shadow-[0_0_50px_rgba(99,102,241,0.3)]';
            case 'emotional': return 'bg-amber-900/20 border-amber-500/50 shadow-[0_0_50px_rgba(245,158,11,0.3)]';
            default: return 'bg-black/50 border-gray-700 shadow-2xl';
        }
    };

    // Polling / Simulation Loop
    useEffect(() => {
        let interval: any;
        if (isPlaying) {
            interval = setInterval(() => {
                setCurrentTime(prev => prev + 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isPlaying]);

    // Sync with Backend
    useEffect(() => {
        const fetchContext = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ timestamp_seconds: currentTime }),
                });
                const data = await res.json();

                if (data.subtitle) {
                    // Update Karaoke History
                    setSubtitleHistory(prev => {
                        const last = prev[prev.length - 1];
                        if (last !== data.subtitle.text) {
                            return [...prev.slice(-4), data.subtitle.text]; // Keep last 5 lines
                        }
                        return prev;
                    });
                } else {
                    // Optionally clear or maintain history
                }

                if (data.logs) {
                    setSystemLogs(data.logs);
                }

                if (data.ui_schema && data.ui_schema.length > 0) {
                    setContextData(data.ui_schema);
                }

                if (data.theme) {
                    setSceneTheme(data.theme);
                }
            } catch (err) {
                console.error("Sync error:", err);
            }
        };

        fetchContext();
    }, [currentTime]);

    const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCurrentTime(parseFloat(e.target.value));
        setSubtitleHistory([]); // Clear history on scrub
    };

    const togglePlay = () => setIsPlaying(!isPlaying);

    const formatTime = (secs: number) => {
        const m = Math.floor(secs / 60);
        const s = Math.floor(secs % 60);
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    };

    return (
        <div className="flex flex-col h-screen bg-gray-900 text-white font-sans">
            <header className="p-6 border-b border-gray-800 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">
                        Movie Fan Context Deck
                    </h1>
                </div>
                <div className="text-sm text-gray-400">
                    Now Playing: <span className="text-white">Avengers: Infinity War</span>
                </div>
            </header>

            <main className="flex-1 overflow-hidden flex flex-row relative">
                {/* Main Stage: Context Canvas / Simulation View */}
                <div className="flex-1 p-8 flex flex-col justify-center items-center bg-black/50 relative border-r border-gray-800 transition-colors duration-1000">

                    <div className={`w-full max-w-4xl aspect-video rounded-xl border flex flex-col items-center justify-center relative overflow-hidden pb-12 transition-all duration-1000 ${getThemeStyles()}`}>
                        {/* Fake Video Player Placeholder / Ambient Background */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black z-0 opacity-50"></div>

                        {/* MAIN STAGE: Generative UI Canvas */}
                        <div className="absolute inset-0 z-10 flex items-center justify-center p-12 pointer-events-none">
                            {contextData ? (
                                <div className="scale-110 transition-transform duration-700 ease-out opacity-100 w-full flex justify-center">
                                    <ThesysRenderer schema={contextData} />
                                </div>
                            ) : (
                                <div className="text-gray-800 text-6xl font-bold opacity-20 select-none">
                                    NO SIGNAL
                                </div>
                            )}
                        </div>


                    </div>
                </div>

                {/* Right Sidebar: Chat Interface */}
                <aside className="w-[400px] h-full bg-gray-900 border-l border-gray-800 flex flex-col shadow-2xl z-30">
                    <ChatInterface />
                </aside>
            </main>

            {/* Bottom: Controls */}
            <footer className="bg-gray-900 border-t border-gray-800 p-4 pb-8 relative">
                {/* Repositioned Karaoke Subtitles (Above Timeline) */}
                <div className="absolute bottom-full left-0 w-full pb-4 bg-gradient-to-t from-gray-900 to-transparent pointer-events-none flex flex-col items-center justify-end h-32 z-10">
                    {subtitleHistory.slice(0, -1).map((line, i) => (
                        <p key={i} className="text-gray-400/60 text-sm font-medium transition-all duration-300 blur-[0.5px]">
                            {line}
                        </p>
                    ))}
                    {/* Active Line */}
                    {subtitleHistory.length > 0 && (
                        <p className="text-white text-xl font-bold drop-shadow-lg scale-105 transition-all duration-100 text-center mt-1">
                            {subtitleHistory[subtitleHistory.length - 1]}
                        </p>
                    )}
                </div>

                <div className="max-w-4xl mx-auto flex items-center gap-4 relative z-20">
                    <button
                        onClick={togglePlay}
                        className="w-12 h-12 rounded-full bg-white text-black flex items-center justify-center hover:bg-gray-200 transition"
                    >
                        {isPlaying ? '⏸' : '▶'}
                    </button>

                    <div className="flex-1 flex flex-col gap-1">
                        <input
                            type="range"
                            min="0"
                            max="300"
                            step="1"
                            value={currentTime}
                            onChange={handleScrub}
                            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                        />
                        <div className="flex justify-between text-xs text-gray-400">
                            <span>{formatTime(currentTime)}</span>
                            <span>05:00</span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
