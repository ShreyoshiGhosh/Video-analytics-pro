import React, { useState, useEffect } from 'react';
import { Activity, Clock } from 'lucide-react';

export const Header = ({ isSmoke }) => {
    // 1. STATE: This is how React "remembers" things that change.
    // We initialize the time and a function to update it.
    const [time, setTime] = useState(new Date().toLocaleTimeString());

    // 2. EFFECT: This runs when the component first appears.
    useEffect(() => {
        // We set a timer to update the time EVERY second.
        const timer = setInterval(() => {
            setTime(new Date().toLocaleTimeString());
        }, 1000);

        // This is a "Cleanup". It stops the timer if the user leaves the page.
        return () => clearInterval(timer);
    }, []); // The empty [] means "Only run this once when the page loads."

    return (
        <header className="flex justify-between items-center m-5">

            {/* LEFT SIDE: LOGO */}
            <div className="flex items-center gap-4 " >
                <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
                    <Activity className="text-blue-500" size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-black tracking-tighter italic uppercase">
                        V-ANALYTICS <span className="text-blue-500">PRO</span>
                    </h1>
                    <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase">
                        Autonomous Edge Monitoring
                    </p>
                </div>
            </div>

            {/* RIGHT SIDE: STATUS & TIME */}
            <div className="flex items-center gap-8 font-mono text-sm" >
                <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-500 uppercase">System Time</span>
                    <span className="text-slate-300 flex items-center gap-2">
                        <Clock size={14} /> {time}
                    </span>
                </div>

                {/* The Vertical Line separator */}
                <div className="h-8 w-[1px] bg-white/10" />

                <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-500 uppercase">Network Status</span>
                    <span className="flex items-center gap-2 text-green-500 font-bold">
                        {/* The Green/Red dot logic */}
                        <div className={`w-2 h-2 rounded-full ${isSmoke ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
                        127.0.0.1:8000
                    </span>
                </div>
            </div>
        </header>
    );
};
