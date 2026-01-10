'use client';

import React, { useState } from 'react';
import { Message, ChatResponse } from '../types';
import ThesysRenderer from './ThesysRenderer';

export default function ChatInterface() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!query.trim()) return;

        const userMsg: Message = { role: 'user', content: query };
        setMessages(prev => [...prev, userMsg]);
        setLoading(true);
        setQuery('');

        try {
            const res = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMsg.content, user_id: 'user_1' }),
            });
            const data: ChatResponse = await res.json();

            const aiMsg: Message = {
                role: 'ai',
                content: data.response,
                data: data.data,
                agent_used: data.agent_used
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I couldn't reach the server." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-900 text-white p-4">
            <header className="mb-4">
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                    Movie Fan GenUI
                </h1>
            </header>

            <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-xl p-4 rounded-2xl ${msg.role === 'user'
                            ? 'bg-blue-600'
                            : 'bg-gray-800 border border-gray-700'
                            }`}>
                            <p>{msg.content}</p>

                            {/* Thesys Generative UI Rendering */}
                            {msg.data && msg.data.ui_schema && (
                                <div className="mt-4">
                                    <ThesysRenderer schema={msg.data.ui_schema} />
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && <div className="text-gray-500 animate-pulse">Thinking...</div>}
            </div>

            <div className="flex gap-2">
                <input
                    type="text"
                    className="flex-1 bg-gray-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Ask about a movie..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                />
                <button
                    onClick={handleSend}
                    className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-xl transition-colors font-semibold"
                >
                    Send
                </button>
            </div>
        </div>
    );
}
