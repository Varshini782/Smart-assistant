import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

export default function Loader({ label = 'Loading…', fullPage = false }) {
  const inner = (
    <div className="flex flex-col items-center gap-3">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      >
        <Loader2 className="h-10 w-10 text-brand-500" aria-hidden />
      </motion.div>
      {label && (
        <p className="text-sm font-medium text-slate-600 dark:text-slate-300">{label}</p>
      )}
    </div>
  )

  if (fullPage) {
    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-white/70 backdrop-blur-sm dark:bg-slate-950/70"
        role="status"
        aria-live="polite"
      >
        {inner}
      </div>
    )
  }

  return <div className="flex justify-center py-12">{inner}</div>
}
