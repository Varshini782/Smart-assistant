import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BookOpen, Bug, Home, LayoutDashboard, Sparkles, Target } from 'lucide-react'

const links = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/results', label: 'Results', icon: Sparkles },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/practice', label: 'Practice', icon: Target },
  { to: '/learning', label: 'Learning', icon: BookOpen },
]

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#0f172a]/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2 font-semibold text-white">
          <motion.span
            className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 text-white shadow-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
          >
            <Bug className="h-5 w-5" />
          </motion.span>
          <span className="hidden sm:inline bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-300 font-bold tracking-tight">
            Smart Debug
          </span>
        </Link>

        <nav className="flex flex-1 flex-wrap items-center justify-end gap-1 sm:gap-2">
          {links.map(({ to, label, icon: Icon }) => {
            const active = pathname === to
            return (
              <Link
                key={to}
                to={to}
                className={`relative flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? 'text-cyan-300'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {active && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-0 rounded-lg bg-indigo-500/20"
                    transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                  />
                )}
                <Icon className="relative z-10 h-4 w-4" />
                <span className="relative z-10 hidden md:inline">{label}</span>
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
