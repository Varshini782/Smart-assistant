import { AnimatePresence, motion } from 'framer-motion'

/**
 * @param {{ id: string, label: string }[]} tabs
 * @param {string} activeId
 * @param {(id: string) => void} onChange
 * @param {Record<string, React.ReactNode>} panels
 */
export default function Tabs({ tabs, activeId, onChange, panels }) {
  return (
    <div>
      <div
        className="flex flex-wrap gap-1 rounded-xl border border-slate-200 bg-slate-100/80 p-1 dark:border-slate-700 dark:bg-slate-800/80"
        role="tablist"
      >
        {tabs.map((tab) => {
          const active = tab.id === activeId
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => onChange(tab.id)}
              className={`relative rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                active
                  ? 'text-brand-700 dark:text-brand-300'
                  : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
              }`}
            >
              {active && (
                <motion.span
                  layoutId="tab-pill"
                  className="absolute inset-0 rounded-lg bg-white shadow-sm dark:bg-slate-700"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative z-10">{tab.label}</span>
            </button>
          )
        })}
      </div>

      <div className="mt-4 min-h-[120px]">
        <AnimatePresence mode="wait">
          {tabs.map((tab) =>
            tab.id === activeId ? (
              <motion.div
                key={tab.id}
                role="tabpanel"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                {panels[tab.id]}
              </motion.div>
            ) : null
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
