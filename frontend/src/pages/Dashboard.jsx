import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Activity, TrendingUp, User, Target } from 'lucide-react'
import AnimatedCard from '../components/UI/AnimatedCard.jsx'
import Loader from '../components/Loader.jsx'
import { getDashboard } from '../services/api.js'

const USER_KEY = 'sda_user_id'
const DAY_LABELS = ['−6d', '−5d', '−4d', '−3d', '−2d', '−1d', 'Today']

export default function Dashboard() {
  const [userId, setUserId] = useState(() => localStorage.getItem(USER_KEY) || 'guest')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const uid = userId.trim() || 'guest'
        const d = await getDashboard(uid)
        if (!cancelled) setData(d)
      } catch (e) {
        if (!cancelled) {
          toast.error('Could not load dashboard.')
          console.error(e)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [userId])

  const weekly = (data?.weekly_errors || []).map((v, i) => ({
    day: DAY_LABELS[i] ?? `D${i}`,
    errors: v,
  }))

  const progress = (data?.progress || []).map((v, i) => ({
    day: DAY_LABELS[i] ?? `D${i}`,
    cumulative: v,
  }))

  const topErrors = (data?.top_errors || []).map((name, i) => ({
    name: name.length > 20 ? `${name.slice(0, 20)}…` : name,
    full: name,
    weight: Math.max(1, 4 - i),
  }))

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  }

  const chartTheme = {
    grid: "stroke-white/5",
    text: "#94a3b8",
    tooltipConfig: {
      contentStyle: {
        borderRadius: '12px',
        border: '1px solid rgba(255,255,255,0.1)',
        background: 'rgba(0,0,0,0.8)',
        backdropFilter: 'blur(8px)',
        color: '#fff',
      },
      itemStyle: { color: '#22d3ee' }
    }
  }

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-8 max-w-6xl mx-auto">
      <motion.div variants={itemVariants} className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between mb-8 py-4 border-b border-white/10">
        <div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Activity className="w-8 h-8 text-cyan-400" />
            Analytics Deck
          </h1>
          <p className="text-slate-400 mt-2 font-medium">
            Track your coding habits, identify weak points, and monitor progress.
          </p>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-black/40 px-5 py-3 shadow-inner">
          <User className="h-5 w-5 text-indigo-400" />
          <input
            value={userId}
            onChange={(e) => {
              setUserId(e.target.value)
              localStorage.setItem(USER_KEY, e.target.value)
            }}
            className="min-w-[12rem] bg-transparent text-sm outline-none text-white font-mono placeholder:text-slate-600"
            placeholder="user_id"
          />
        </div>
      </motion.div>

      {loading ? (
        <Loader label="Initiating telemetry scan…" fullPage={false} />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          
          <motion.div variants={itemVariants}>
            <AnimatedCard className="h-full">
              <h2 className="text-xl font-bold text-white mb-1">Error Frequency</h2>
              <p className="text-slate-400 text-sm mb-6">Last 7 days timeframe</p>
              
              <div className="h-[280px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weekly}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} className={chartTheme.grid} />
                    <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: chartTheme.text }} />
                    <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: chartTheme.text }} />
                    <Tooltip {...chartTheme.tooltipConfig} cursor={{ stroke: 'rgba(255,255,255,0.1)' }} />
                    <Line
                      type="monotone"
                      dataKey="errors"
                      stroke="#22d3ee"
                      strokeWidth={3}
                      dot={{ r: 4, fill: '#0f172a', stroke: '#22d3ee', strokeWidth: 2 }}
                      activeDot={{ r: 6, fill: '#22d3ee', stroke: '#fff' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </AnimatedCard>
          </motion.div>

          <motion.div variants={itemVariants}>
            <AnimatedCard className="h-full">
              <h2 className="text-xl font-bold text-white mb-1">System Overloads</h2>
              <p className="text-slate-400 text-sm mb-6">Top repeated errors</p>
              
              <div className="h-[280px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topErrors} layout="vertical" margin={{ left: 8, right: 16 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} className={chartTheme.grid} />
                    <XAxis type="number" allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: chartTheme.text }} />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={120}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: chartTheme.text }}
                    />
                    <Tooltip
                      formatter={(value, _n, props) => [value, props.payload.full]}
                      {...chartTheme.tooltipConfig}
                      cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    />
                    <Bar dataKey="weight" fill="url(#colorUv)" radius={[0, 4, 4, 0]}>
                      {topErrors.map((entry, index) => (
                        <cell key={`cell-${index}`} fill={`#a855f7`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {topErrors.length === 0 && (
                <p className="text-center text-sm text-slate-500 mt-4">Telemetry clean. No errors logged.</p>
              )}
            </AnimatedCard>
          </motion.div>

          <motion.div variants={itemVariants}>
            <AnimatedCard className="h-full">
              <h2 className="text-xl font-bold text-white mb-1">Cumulative Workload</h2>
              <p className="text-slate-400 text-sm mb-6">Total errors encountered this week</p>
              
              <div className="h-[260px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={progress}>
                    <defs>
                      <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.5} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} className={chartTheme.grid} />
                    <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: chartTheme.text }} />
                    <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: chartTheme.text }} />
                    <Tooltip {...chartTheme.tooltipConfig} />
                    <Area
                      type="monotone"
                      dataKey="cumulative"
                      stroke="#6366f1"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#pg)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </AnimatedCard>
          </motion.div>

          <motion.div variants={itemVariants}>
            <AnimatedCard glowEffect className="h-full border border-indigo-500/20 bg-indigo-500/5">
              <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                <Target className="w-5 h-5 text-indigo-400" /> Focus Areas
              </h2>
              <p className="text-slate-400 text-sm mb-6">Identified conceptual weaknesses</p>
              
              <ul className="space-y-4 pr-2">
                {(data?.weak_topics || []).length === 0 ? (
                  <li className="text-sm text-slate-500 font-mono">No vulnerabilities detected.</li>
                ) : (
                  (data.weak_topics || []).map((t, i) => (
                    <motion.li
                      whileHover={{ x: 5 }}
                      key={i}
                      className="flex items-center gap-4 rounded-xl border border-white/5 bg-black/40 px-4 py-3 shadow-inner"
                    >
                      <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-400/20 text-cyan-300 font-bold border border-cyan-500/20 shadow-[0_0_15px_rgba(34,211,238,0.15)]">
                        {i + 1}
                      </div>
                      <span className="text-sm font-semibold text-slate-200">{t}</span>
                    </motion.li>
                  ))
                )}
              </ul>
              <div className="mt-8 flex items-center gap-3 text-sm text-indigo-300 bg-indigo-500/10 p-4 rounded-xl border border-indigo-500/20">
                <TrendingUp className="h-5 w-5 animate-pulse" />
                <span className="font-medium">System recommends running Drills in Practice Mode.</span>
              </div>
            </AnimatedCard>
          </motion.div>
          
        </div>
      )}
    </motion.div>
  )
}
