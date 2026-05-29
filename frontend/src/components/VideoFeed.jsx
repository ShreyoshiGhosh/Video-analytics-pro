import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const VideoFeed = ({ isSmoke }) => {
    return (
        <div className="col-span-9 flex flex-col relative h-full">
            <motion.div
                animate={{
                    // The border glows red when smoke is detected!
                    borderColor: isSmoke ? 'rgba(239, 68, 68, 0.6)' : 'rgba(59, 130, 246, 0.2)',
                    scale: isSmoke ? 0.98 : 1
                }}
                transition={{ duration: 0.5 }}
                className={`glass-panel flex-1 overflow-hidden relative border-2 ${isSmoke ? 'shadow-[0_0_40px_rgba(239,68,68,0.3)]' : 'shadow-xl'}`}
            >
                {/* THE STREAM: Tapping into our FastAPI Backend */}
                <img
                    src="http://localhost:8000/video_feed"
                    alt="Live AI Stream"
                    className="w-full h-full object-cover opacity-90"
                />

                {/* VISUAL OVERLAYS (Making it look "Hi-Tech") */}
                <div className="absolute top-4 left-4 p-2 bg-black/40 backdrop-blur-md rounded text-[9px] font-mono border border-white/10 tracking-widest uppercase">
                    Signal: feed_01
                </div>

                {/* ALARM OVERLAY */}
                <AnimatePresence>
                    {isSmoke && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 flex items-center justify-center bg-red-500/10 pointer-events-none"
                        >
                            <div className="bg-red-600 text-white px-6 py-2 font-black text-xs tracking-[0.3em] rounded shadow-2xl uppercase italic animate-pulse">
                                Adaptive Vision Active
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
};
