import { motion } from 'framer-motion'

export default function Tabs({ 
  tabs, 
  activeTab, 
  onChange,
  className = ""
}) {
  return (
    <div className={`flex space-x-2 bg-black/20 p-1 rounded-xl w-fit border border-white/10 ${className}`}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`relative px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              isActive ? 'text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {isActive && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-white/10 rounded-lg"
                initial={false}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            )}
            <span className="relative z-10">{tab.label}</span>
          </button>
        )
      })}
    </div>
  )
}
