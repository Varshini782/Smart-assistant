import { motion } from 'framer-motion'
import { useState } from 'react'

export default function CodeEditor({ 
  value, 
  onChange, 
  language = "python",
  className = "" 
}) {
  const [isFocused, setIsFocused] = useState(false)

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`relative w-full rounded-2xl overflow-hidden glass transition-all duration-300 ${isFocused ? 'neon-glow' : ''} ${className}`}
    >
      <div className="flex items-center px-4 py-2 border-b border-white/10 bg-black/20">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
        </div>
        <div className="ml-4 text-xs font-mono text-slate-400">
          main.{language === 'python' ? 'py' : language === 'javascript' ? 'js' : language}
        </div>
      </div>
      
      <div className="p-4 bg-black/40 h-full min-h-[300px]">
        <textarea
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          spellCheck="false"
          className="w-full h-full min-h-[250px] bg-transparent text-slate-200 font-mono text-sm focus:outline-none resize-none"
          placeholder="// Paste your buggy code here..."
        />
      </div>
    </motion.div>
  )
}
