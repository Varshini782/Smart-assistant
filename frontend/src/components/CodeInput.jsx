import { motion } from 'framer-motion'

export default function CodeInput({ value, onChange, placeholder, label, id = 'code-input' }) {
  return (
    <div>
      {label && (
        <label htmlFor={id} className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
          {label}
        </label>
      )}
      <motion.textarea
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={12}
        spellCheck={false}
        className="font-mono w-full resize-y rounded-xl border border-slate-200 bg-white/90 px-4 py-3 text-sm leading-relaxed text-slate-900 shadow-inner outline-none ring-brand-500/0 transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-600 dark:bg-slate-900/90 dark:text-slate-100 dark:placeholder:text-slate-500"
      />
    </div>
  )
}
