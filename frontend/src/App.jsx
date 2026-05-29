import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, ShieldAlert, BarChart3 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Import our atoms and molecules
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { VideoFeed } from './components/VideoFeed';
import { AnalyticsCharts } from './components/AnalyticsCharts';
import './index.css';

function App() {
  const [stats, setStats] = useState({
    is_smoke_detected: false,
    smoke_level: 0,
    human_count: 0,
    total_detections: 0,
    fps: 0,
    cpu_usage: 0,
    memory_usage: 0,
    emergency_mode: false
  });

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await axios.get('http://localhost:8000/status');
        setStats(response.data);
      } catch (err) {
        console.error("Backend offline");
      }
    };
    const interval = setInterval(checkStatus, 1000); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen w-screen bg-black flex flex-col overflow-hidden relative text-white">
      
      {/* EMERGENCY OVERLAY */}
      <AnimatePresence>
        {stats.emergency_mode && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[100] bg-red-900/90 backdrop-blur-xl flex flex-col items-center justify-center text-center p-20"
          >
            <ShieldAlert size={120} className="text-white animate-bounce mb-8" />
            <h1 className="text-7xl font-black mb-4 tracking-tighter italic">CRITICAL EMERGENCY</h1>
            <p className="text-2xl font-mono opacity-80 uppercase tracking-widest text-white">
              Smoke levels at {stats.smoke_level}% // Evacuate Immediately
            </p>
            <div className="mt-12 p-6 border-4 border-white animate-pulse text-4xl font-black italic tracking-widest text-white">
              SYSTEM SHUTDOWN INITIATED
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <Header isSmoke={stats.is_smoke_detected} />

      <main className="flex-1 px-16 pb-12 overflow-hidden">
        <div className="grid grid-cols-12 gap-8 h-full overflow-hidden">
          
          {/* LEFT: TELEMETRY & SYSTEM HEALTH */}
          <Sidebar stats={stats} />
          
          {/* RIGHT: VIDEO & CHARTS */}
          <div className="col-span-9 flex flex-col gap-6 overflow-hidden">
            
            {/* LIVE FEED (Top 60%) */}
            <div className="flex-[3]">
              <VideoFeed isSmoke={stats.is_smoke_detected} />
            </div>

            {/* LIVE CHARTS (Bottom 40%) */}
            <div className="flex-[2]">
              <AnalyticsCharts 
                humanCount={stats.human_count} 
                smokeLevel={stats.smoke_level} 
              />
            </div>

          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
