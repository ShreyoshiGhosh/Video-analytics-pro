import { Cpu, Camera, ShieldAlert, BarChart3, Activity, HardDrive, Zap, Upload, Video, Play, Square, Settings2 } from 'lucide-react';
import { StatCard } from './StatCard';
import axios from 'axios';
import React, { useState } from 'react';

export const Sidebar = ({ stats }) => {
    const [sourceType, setSourceType] = useState('Webcam');
    const [rtspUrl, setRtspUrl] = useState('http://192.168.29.102:8080/video');
    const [confThres, setConfThres] = useState(0.25);
    const [isTracking, setIsTracking] = useState(false);

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        try {
            await axios.post('http://localhost:8000/upload', formData);
            setSourceType('Local Video');
        } catch (error) { console.error("Upload failed", error); }
    };

    const handleStartTracking = async () => {
        const source = sourceType === 'RTSP' ? rtspUrl : (sourceType === 'Webcam' ? 0 : 'latest_upload');
        try {
            console.log("Configuring system...", { source, confThres, isTracking: !isTracking });
            await axios.post('http://127.0.0.1:8000/configure', {
                source: source,
                conf_thres: confThres,
                is_tracking: !isTracking
            });
            setIsTracking(!isTracking);
        } catch (error) { 
            console.error("Config failed", error);
            alert("Backend connection failed. Is the server running?");
        }
    };

    return (
        <div className="col-span-3 flex flex-col gap-6 h-full overflow-y-auto no-scrollbar pb-10 text-white">
            
            {/* SYSTEM CONTROLS */}
            <div className="glass-panel p-6 border border-white/10 bg-gradient-to-br from-blue-500/10 to-purple-500/10 shadow-2xl">
                <div className="flex items-center gap-2 mb-6">
                    <Settings2 size={16} className="text-blue-400" />
                    <h2 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Configuration</h2>
                </div>

                <div className="space-y-4">
                    {/* SOURCE SELECTION */}
                    <div className="grid grid-cols-3 gap-2">
                        {['Webcam', 'RTSP', 'Upload'].map(s => (
                            <button 
                                key={s}
                                onClick={() => setSourceType(s)}
                                className={`py-2 text-[9px] uppercase font-bold rounded-md border transition-all ${sourceType === s ? 'bg-blue-600 border-blue-400 text-white' : 'bg-white/5 border-white/5 text-slate-500 hover:border-white/20'}`}
                            >
                                {s}
                            </button>
                        ))}
                    </div>

                    {sourceType === 'RTSP' && (
                        <input 
                            type="text" 
                            value={rtspUrl}
                            onChange={(e) => setRtspUrl(e.target.value)}
                            placeholder="RTSP URL..."
                            className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-[10px] font-mono text-blue-300 focus:outline-none focus:border-blue-500"
                        />
                    )}

                    {sourceType === 'Upload' && (
                        <label className="flex flex-col items-center justify-center w-full h-20 border-2 border-dashed border-white/10 rounded-xl cursor-pointer hover:bg-white/5 transition-all">
                            <Upload size={16} className="text-slate-500 mb-1" />
                            <p className="text-[9px] text-slate-500 uppercase font-bold">Drop Video File</p>
                            <input type="file" className="hidden" onChange={handleFileUpload} accept="video/*" />
                        </label>
                    )}

                    <div className="space-y-2">
                        <div className="flex justify-between text-[10px] uppercase font-bold text-slate-500">
                            <span>Confidence Threshold</span>
                            <span className="text-blue-400">{confThres}</span>
                        </div>
                        <input 
                            type="range" min="0.1" max="0.9" step="0.05" 
                            value={confThres}
                            onChange={(e) => setConfThres(parseFloat(e.target.value))}
                            className="w-full accent-blue-500"
                        />
                    </div>

                    <button 
                        onClick={handleStartTracking}
                        className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 text-xs font-black uppercase tracking-widest transition-all ${isTracking ? 'bg-red-600 shadow-red-900/20' : 'bg-blue-600 shadow-blue-900/20 hover:scale-[1.02] active:scale-95'}`}
                    >
                        {isTracking ? <><Square size={16} fill="white"/> Stop Tracking</> : <><Play size={16} fill="white"/> Start Tracking</>}
                    </button>
                </div>
            </div>

            {/* INFERENCE STATS */}
            <div className="glass-panel p-6 border border-white/5 shadow-2xl">
                <div className="flex items-center gap-2 mb-6">
                    <Activity size={16} className="text-blue-400" />
                    <h2 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
                        Inference Pipeline
                    </h2>
                </div>
                
                <div className="space-y-6">
                    <StatCard 
                        icon={<Zap size={18}/>} 
                        label="Frame Rate" 
                        value={`${stats.fps} FPS`} 
                        sub={`Min: ${stats.min_fps} | Max: ${stats.max_fps}`} 
                        color="text-yellow-400" 
                    />
                    <StatCard 
                        icon={<Activity size={18}/>} 
                        label="Object Density" 
                        value={stats.human_count} 
                        sub="Humans detected" 
                        color="text-blue-400" 
                    />
                    <StatCard 
                        icon={<BarChart3 size={18}/>} 
                        label="Total Event Count" 
                        value={stats.total_detections} 
                        sub="Session history" 
                        color="text-slate-300" 
                    />
                </div>
            </div>

            {/* SYSTEM STATS */}
            <div className="glass-panel p-6 border border-white/5 shadow-2xl">
                <div className="flex items-center gap-2 mb-6">
                    <HardDrive size={16} className="text-green-400" />
                    <h2 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
                        System Resources
                    </h2>
                </div>
                
                <div className="space-y-6">
                    <div className="flex justify-between items-center text-[10px] uppercase font-bold text-slate-500">
                        <span>CPU Usage</span>
                        <span className="text-white">{stats.cpu_usage}%</span>
                    </div>
                    <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                        <div className="bg-green-500 h-full transition-all duration-500" style={{ width: `${stats.cpu_usage}%` }} />
                    </div>

                    <div className="flex justify-between items-center text-[10px] uppercase font-bold text-slate-500 mt-4">
                        <span>Memory (RAM)</span>
                        <span className="text-white">{stats.memory_usage}%</span>
                    </div>
                    <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-full transition-all duration-500" style={{ width: `${stats.memory_usage}%` }} />
                    </div>
                </div>
            </div>

            {/* DATA QUALITY & DRIFT */}
            <div className="glass-panel p-6 border border-white/5 shadow-2xl bg-blue-500/5">
                <div className="flex items-center gap-2 mb-4">
                    <BarChart3 size={16} className="text-blue-300" />
                    <h2 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
                        Drift Monitoring
                    </h2>
                </div>
                <div className="space-y-4">
                    <div className="flex justify-between items-center text-[10px] uppercase font-bold text-slate-500">
                        <span>Low Conf Frames</span>
                        <span className="text-yellow-500 font-mono">12</span>
                    </div>
                    <div className="flex justify-between items-center text-[10px] uppercase font-bold text-slate-500">
                        <span>Performance Drift</span>
                        <span className="text-green-500 font-mono">NEGligible</span>
                    </div>
                </div>
            </div>

            {/* ENVIRONMENTAL STATUS */}
            <div className="glass-panel p-6 border border-white/5 shadow-2xl bg-red-500/5">
                <StatCard 
                    icon={<ShieldAlert size={20}/>} 
                    label="Environment" 
                    value={stats.is_smoke_detected ? "SMOKE DETECTED" : "AIR CLEAR"} 
                    sub={stats.is_smoke_detected ? `Level: ${stats.smoke_level}%` : "Monitoring..."} 
                    color={stats.is_smoke_detected ? "text-red-500 animate-pulse" : "text-green-500"} 
                />
            </div>
        </div>
    );
};
