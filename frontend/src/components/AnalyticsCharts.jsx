import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const AnalyticsCharts = ({ humanCount, smokeLevel }) => {
    const [data, setData] = useState([]);

    useEffect(() => {
        // Add new data point every time counts update
        const newDataPoint = {
            time: new Date().toLocaleTimeString().split(' ')[0],
            humans: humanCount,
            smoke: smokeLevel,
        };

        setData(prev => {
            const updated = [...prev, newDataPoint];
            // Keep only the last 20 data points for a "scrolling" effect
            return updated.slice(-20);
        });
    }, [humanCount, smokeLevel]);

    return (
        <div className="glass-panel p-6 border border-white/5 shadow-2xl h-full flex flex-col">
            <h2 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-6">
                Telemetry History (Real-time)
            </h2>

            <div className="flex-1 w-full min-h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis
                            dataKey="time"
                            stroke="#475569"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                        />
                        <YAxis
                            stroke="#475569"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '10px' }}
                            itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
                        />

                        {/* HUMAN COUNT LINE */}
                        <Line
                            type="monotone"
                            dataKey="humans"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            dot={false}
                            isAnimationActive={false}
                        />

                        {/* SMOKE LEVEL LINE */}
                        <Line
                            type="monotone"
                            dataKey="smoke"
                            stroke="#ef4444"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={false}
                            isAnimationActive={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="flex gap-4 mt-4">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-[2px] bg-blue-500" />
                    <span className="text-[10px] text-slate-500 uppercase font-bold">Human Count</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-[2px] bg-red-500 border-dashed" />
                    <span className="text-[10px] text-slate-500 uppercase font-bold">Smoke Level %</span>
                </div>
            </div>
        </div>
    );
};
