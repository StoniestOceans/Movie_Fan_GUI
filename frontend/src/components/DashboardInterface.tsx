'use client';

import React, { useState, useEffect, useRef } from 'react';
import ThesysRenderer from './ThesysRenderer';
import ChatInterface from './ChatInterface';

export default function DashboardInterface() {
    const [currentTime, setCurrentTime] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [contextData, setContextData] = useState<any>(null);
    const [subtitleText, setSubtitleText] = useState<string>("");
    const [showChat, setShowChat] = useState(false);

    // Karaoke & Logs State
    const [subtitleHistory, setSubtitleHistory] = useState<string[]>([]);
    const [systemLogs, setSystemLogs] = useState<string[]>([]);

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
                    <button
                        onClick={() => setShowChat(!showChat)}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors"
                    >
                        {showChat ? 'Close Chat' : 'Open Chat'}
                    </button>
                </div>
                <div className="text-sm text-gray-400">
                    Now Playing: <span className="text-white">The Matrix</span>
                </div>
            </header>

            {/* Chat Overlay */}
            {showChat && (
                <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
                    <div className="bg-gray-900 w-full max-w-2xl h-[80vh] rounded-2xl shadow-2xl overflow-hidden border border-gray-700 relative">
                        <button
                            onClick={() => setShowChat(false)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-white"
                        >
                            ✕
                        </button>
                        <ChatInterface />
                    </div>
                </div>
            )}

            <main className="flex-1 overflow-hidden flex flex-col md:flex-row">
                {/* Left: Simulation / Subtitle View */}
                <div className="flex-1 p-8 flex flex-col justify-center items-center border-r border-gray-800 bg-black/50 relative">



                    <div className="w-full max-w-2xl bg-black aspect-video rounded-xl border border-gray-700 flex flex-col items-center justify-end relative shadow-2xl overflow-hidden pb-12">
                        {/* Fake Video Player Placeholder */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent z-0"></div>



                        <div className="absolute top-4 right-4 text-xs text-gray-500 z-20">
                            simulation mode
                        </div>
                    </div>
                </div>

                {/* Right: Dynamic Context (Thesys) */}
                <div className="w-full md:w-1/3 p-6 bg-gray-800/30 overflow-y-auto">
                    <h2 className="text-sm uppercase tracking-wider text-gray-500 mb-4 font-semibold">Live Context</h2>
                    <div className="space-y-4">
                        {contextData ? (
                            <ThesysRenderer schema={contextData} />
                        ) : (
                            <div className="text-gray-500 text-sm italic">Waiting for identifiable context...</div>
                        )}
                    </div>
                </div>
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
