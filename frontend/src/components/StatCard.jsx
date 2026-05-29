import React from 'react';

export const StatCard = ({ icon, label, value, sub, color }) => {
    return (
        <div className="flex items-center gap-5 mr-10">
            <div className="p-3 bg-white/5 rounded-xl border border-white/10 text-slate-400">{icon}</div>
            <div className="flex flex-col gap-1">
                <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest">{label}</p>
                <p className={`text-base font-bold tracking-tight leading-none ${color}`}>{value}</p>
                <p className="text-[10px] text-slate-400 font-medium">{sub} </p>
            </div>
        </div>
    );
};