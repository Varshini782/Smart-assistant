import { motion } from 'framer-motion'

export default function GlowButton({ 
  children, 
  onClick, 
  className = "", 
  variant = 'primary', // primary | outline
  ...props 
}) {
  const baseClasses = "relative inline-flex items-center justify-center font-medium rounded-xl transition-all overflow-hidden px-8 py-3"
  
  const variants = {
    primary: "bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 text-white shadow-lg hover:shadow-indigo-500/25",
    outline: "border border-white/20 bg-white/5 text-slate-200 hover:bg-white/10 hover:border-white/30"
  }

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={`${baseClasses} ${variants[variant]} ${variant === 'primary' ? 'hover:neon-glow' : ''} ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  )
}
