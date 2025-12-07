import React from 'react';

export default function GameStatus({ state }) {
    if (!state) return <div className="p-4 text-slate-500">Loading status...</div>;

    return (
        <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg h-full overflow-y-auto">
            <h2 className="text-xl font-bold text-blue-400 mb-4 border-b border-slate-600 pb-2">
                {state.name || "Unknown Hero"}
            </h2>

            <div className="space-y-6">
                {/* Vitals */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-900 p-3 rounded text-center">
                        <div className="text-xs text-slate-400 uppercase">HP</div>
                        <div className={`text-2xl font-bold ${state.hp < state.max_hp / 2 ? 'text-red-500' : 'text-green-500'}`}>
                            {state.hp} <span className="text-sm text-slate-500">/ {state.max_hp}</span>
                        </div>
                    </div>
                    <div className="bg-slate-900 p-3 rounded text-center">
                        <div className="text-xs text-slate-400 uppercase">Level</div>
                        <div className="text-2xl font-bold text-white">{state.level}</div>
                    </div>
                </div>

                {/* Location */}
                <div>
                    <h3 className="text-sm font-semibold text-slate-300 mb-1">Current Location</h3>
                    <div className="bg-slate-900 p-3 rounded text-indigo-300">
                        {state.location_title || "Unknown"}
                    </div>
                </div>

                {/* Stats */}
                {state.abilities && (
                    <div>
                        <h3 className="text-sm font-semibold text-slate-300 mb-1">Abilities</h3>
                        <div className="grid grid-cols-3 gap-2 text-center text-xs">
                            {Object.entries(state.abilities).map(([key, val]) => (
                                <div key={key} className="bg-slate-700 p-1 rounded">
                                    <span className="uppercase text-slate-400 block">{key}</span>
                                    <span className="text-white font-mono">{val}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Inventory */}
                {state.inventory && state.inventory.length > 0 && (
                    <div>
                        <h3 className="text-sm font-semibold text-slate-300 mb-1">Inventory</h3>
                        <ul className="space-y-1">
                            {state.inventory.map((item, idx) => (
                                <li key={idx} className="flex justify-between bg-slate-900 p-2 rounded text-sm">
                                    <span>{item.name}</span>
                                    <span className="text-slate-500">x{item.qty}</span>
                                </li>
                            ))}
                        </ul>
                        <div className="mt-2 text-right text-yellow-500 text-sm">
                            Gold: {state.gold} gp
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
