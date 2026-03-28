import { motion } from 'framer-motion'

export default function AnimatedCard({ 
  children, 
  className = "", 
  delay = 0, 
  hoverEffect = true,
  glowEffect = false 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={hoverEffect ? { scale: 1.02, y: -5 } : {}}
      className={`glass rounded-2xl p-6 transition-all duration-300 ${glowEffect ? 'hover:neon-glow' : ''} ${className}`}
    >
      {children}
    </motion.div>
  )
}
