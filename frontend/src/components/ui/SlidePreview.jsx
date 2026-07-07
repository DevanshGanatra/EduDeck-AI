import React from 'react';
import { motion } from 'framer-motion';

const SlidePreview = ({ title, bullets = [], slideNumber }) => {
  return (
    <div className="w-full aspect-video rounded-xl overflow-hidden shadow-2xl relative flex flex-col border border-white/10"
         style={{
           background: 'linear-gradient(135deg, #111118 0%, #1a1a2e 100%)',
         }}>
      
      {/* Decorative background elements */}
      <div className="absolute -top-32 -right-32 w-64 h-64 bg-primary/20 rounded-full blur-[80px]"></div>
      <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-blue-500/10 rounded-full blur-[60px]"></div>
      
      {/* Slide number badge */}
      <div className="absolute top-4 right-6 text-white/30 text-xs font-mono font-bold tracking-widest uppercase">
        {slideNumber}
      </div>
      
      {/* EduDeck Watermark/Branding */}
      <div className="absolute bottom-4 right-6 flex items-center gap-2 opacity-30">
        <div className="w-4 h-4 rounded-md flex items-center justify-center text-[8px] text-white font-bold"
             style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)' }}>
          E
        </div>
        <span className="text-[10px] font-bold text-white tracking-widest">EduDeck AI</span>
      </div>

      <div className="flex-1 flex flex-col p-8 md:p-12 z-10 relative h-full">
        {/* Title area */}
        <div className="mb-6 md:mb-10 pb-4 border-b border-white/10 shrink-0">
          <motion.h2 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            key={title}
            className="text-2xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70 leading-tight font-heading"
          >
            {title || 'Untitled Slide'}
          </motion.h2>
        </div>

        {/* Content area */}
        <div className="flex-1 overflow-hidden flex flex-col justify-center">
          <ul className="space-y-4 md:space-y-6">
            {bullets.length === 0 ? (
              <li className="text-white/30 text-sm md:text-lg italic">No content available...</li>
            ) : (
              bullets.map((bullet, idx) => (
                <motion.li 
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="flex items-start gap-4 text-white/80 text-sm md:text-xl leading-relaxed"
                >
                  <span className="shrink-0 w-2 h-2 md:w-2.5 md:h-2.5 rounded-full bg-primary mt-2 shadow-[0_0_8px_rgba(139,92,246,0.8)]"></span>
                  <span>{bullet}</span>
                </motion.li>
              ))
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SlidePreview;
