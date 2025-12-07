import React, { useState, useRef, useEffect } from 'react';

export default function ChatInterface({ history, onSendMessage, loading }) {
    const [input, setInput] = useState("");
    const endRef = useRef(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [history]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;
        onSendMessage(input);
        setInput("");
    };

    return (
        <div className="flex flex-col h-full bg-slate-900 rounded-lg overflow-hidden border border-slate-700 shadow-xl">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {history.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div
                            className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-slate-700 text-slate-200'
                                }`}
                        >
                            <div className="whitespace-pre-wrap">{msg.content}</div>
                            {msg.out_of_character && (
                                <div className="mt-2 text-xs text-slate-400 border-t border-slate-600 pt-1 italic">
                                    DM Note: {msg.out_of_character}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-slate-700 text-slate-400 rounded-lg p-3 animate-pulse">
                            The DM is thinking...
                        </div>
                    </div>
                )}
                <div ref={endRef} />
            </div>

            <form onSubmit={handleSubmit} className="p-4 bg-slate-800 border-t border-slate-700">
                <div className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                        placeholder="What do you do?"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium disabled:opacity-50"
                    >
                        Send
                    </button>
                </div>
            </form>
        </div>
    );
}
