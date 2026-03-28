import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { CheckCircle2, Flame, Skull, Sparkles, RefreshCw, TerminalSquare } from 'lucide-react'
import AnimatedCard from '../components/UI/AnimatedCard.jsx'
import GlowButton from '../components/UI/GlowButton.jsx'
import CodeEditor from '../components/UI/CodeEditor.jsx'
import Loader from '../components/Loader.jsx'
import { getDailyChallenge, getStreak, submitSolution } from '../services/api.js'

const USER_KEY = 'sda_user_id'

export default function Practice() {
  const [userId, setUserId] = useState(() => localStorage.getItem(USER_KEY) || 'guest')
  const [challenge, setChallenge] = useState(null)
  const [code, setCode] = useState('')
  const [streak, setStreak] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const [c, s] = await Promise.all([
        getDailyChallenge(),
        getStreak((userId || 'guest').trim()),
      ])
      setChallenge(c)
      setCode(c.code || '')
      setStreak(s.current_streak ?? 0)
      setResult(null)
    } catch (e) {
      toast.error('Failed to load challenge or streak.')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setResult(null)
    try {
      const uid = (userId || 'guest').trim()
      localStorage.setItem(USER_KEY, uid)
      const res = await submitSolution({ user_id: uid, code })
      setResult(res)
      const s = await getStreak(uid)
      setStreak(s.current_streak ?? 0)
      if (res.correct) toast.success('Fix validated successfully!')
      else toast.error('Anomalies detected in fix.')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Submit failed')
    } finally {
      setSubmitting(false)
    }
  }

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

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-6 max-w-7xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <motion.div variants={itemVariants} className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between py-2 border-b border-white/10 shrink-0">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <TerminalSquare className="w-6 h-6 text-fuchsia-400" />
            Training Ground
          </h1>
          <p className="text-sm text-slate-400 font-medium mt-1">
            Resolve daily anomalies, maintain your streak.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-3 rounded-2xl border border-orange-500/30 bg-orange-500/10 px-5 py-2">
            <Flame className="h-6 w-6 text-orange-500 animate-pulse" />
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-orange-200/70">Streak</p>
              <p className="text-xl font-black tabular-nums text-orange-400 leading-none">{streak}</p>
            </div>
          </div>
          <input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm font-mono text-white outline-none w-32"
            placeholder="user_id"
          />
        </div>
      </motion.div>

      {loading ? (
        <Loader label="Spawning anomalous environment…" />
      ) : (
        <form onSubmit={onSubmit} className="flex-1 min-h-0 flex flex-col md:flex-row gap-6 pb-8">
          
          <motion.div variants={itemVariants} className="flex-1 flex flex-col w-full md:w-1/2 min-h-0">
            <AnimatedCard className="h-full flex flex-col flex-1 border-fuchsia-500/20 bg-fuchsia-500/5">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">Anomaly Briefing</h2>
                  <p className="text-slate-400 text-sm">Target bug class: <span className="text-fuchsia-300 font-mono bg-fuchsia-500/20 px-2 py-0.5 rounded-md">{challenge?.bug || 'Unknown'}</span></p>
                </div>
                <span className="rounded-lg bg-white/5 border border-white/10 px-3 py-1 text-xs font-mono text-slate-400">
                  ID: {challenge?.id}
                </span>
              </div>
              
              <div className="flex-1 bg-black/60 rounded-xl border border-white/10 p-4 font-mono text-sm text-slate-300 overflow-auto relative">
                <div className="absolute top-2 right-4 text-[10px] text-slate-600 uppercase tracking-widest font-bold">Original Buggy Code</div>
                <pre className="mt-4">{challenge?.code}</pre>
              </div>

              {result && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`mt-4 rounded-xl border p-5 ${
                    result.correct
                      ? 'border-emerald-500/30 bg-emerald-500/10'
                      : 'border-rose-500/30 bg-rose-500/10'
                  }`}
                >
                  <div className="mb-2 flex items-center gap-2 font-bold">
                    {result.correct ? (
                      <>
                        <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                        <span className="text-emerald-300 tracking-wide uppercase text-sm">Fix Validated</span>
                      </>
                    ) : (
                      <>
                        <Skull className="h-5 w-5 text-rose-400" />
                        <span className="text-rose-300 tracking-wide uppercase text-sm">Anomalies Remain</span>
                      </>
                    )}
                  </div>
                  <p className="text-sm font-medium leading-relaxed text-slate-300">{result.feedback}</p>
                </motion.div>
              )}
            </AnimatedCard>
          </motion.div>

          <motion.div variants={itemVariants} className="flex-1 flex flex-col w-full md:w-1/2 min-h-[400px]">
            <AnimatedCard className="h-full flex flex-col flex-1 p-0 overflow-hidden relative border-cyan-500/20">
              <div className="flex justify-between items-center px-6 py-4 bg-black/40 border-b border-white/10 shrink-0">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
                  Editor Workspace
                </h2>
                <button
                  type="button"
                  onClick={load}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-white/5 text-xs font-medium text-slate-300 hover:bg-white/10 hover:text-white transition-colors"
                >
                  <RefreshCw className="h-3.5 w-3.5" /> Skip / Reload
                </button>
              </div>
              
              <div className="flex-1 min-h-0 bg-black/20">
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  spellCheck={false}
                  className="w-full h-full resize-none bg-transparent p-6 text-sm font-mono text-slate-200 focus:outline-none"
                  placeholder="Inject fixed code here..."
                />
              </div>

              <div className="shrink-0 p-4 border-t border-white/10 bg-black/40 flex justify-end">
                <GlowButton 
                  type="submit" 
                  disabled={submitting}
                  className="px-8 py-3 w-full sm:w-auto"
                >
                  <Sparkles className="h-5 w-5 mr-2" />
                  {submitting ? 'Verifying...' : 'Deploy Fix'}
                </GlowButton>
              </div>
            </AnimatedCard>
          </motion.div>

        </form>
      )}
    </motion.div>
  )
}
