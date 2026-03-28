import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { BookOpen, ChevronDown, ExternalLink, GraduationCap, Zap } from 'lucide-react'
import AnimatedCard from '../components/UI/AnimatedCard.jsx'
import GlowButton from '../components/UI/GlowButton.jsx'
import CodeEditor from '../components/UI/CodeEditor.jsx'
import Loader from '../components/Loader.jsx'
import { postLearningMode } from '../services/api.js'

const sections = [
  { id: 'quick', title: 'Quick fix', key: 'quick_fix', icon: Zap, color: 'text-amber-400' },
  { id: 'steps', title: 'Step-by-step debugging', key: 'step_by_step_debugging', list: true, icon: GraduationCap, color: 'text-indigo-400' },
  { id: 'why', title: 'Why this error happened', key: 'why_error_occurred', icon: BookOpen, color: 'text-fuchsia-400' },
  { id: 'concept', title: 'Concept to learn', key: 'concept_to_learn', link: true, icon: ExternalLink, color: 'text-cyan-400' },
]

export default function Learning() {
  const [code, setCode] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [openId, setOpenId] = useState('quick')

  useEffect(() => {
    if (data) setOpenId('quick')
  }, [data])

  const onAnalyze = async (e) => {
    e.preventDefault()
    if (!code.trim() || !errorMessage.trim()) {
      toast.error('Provide both code and an error message.')
      return
    }
    setLoading(true)
    setData(null)
    try {
      const res = await postLearningMode({
        code: code.trim(),
        error_message: errorMessage.trim(),
      })
      setData(res)
      toast.success('Learning guide ready')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Request failed')
    } finally {
      setLoading(false)
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
    <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-12 max-w-4xl mx-auto py-8">
      <motion.div variants={itemVariants} className="text-center relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-purple-500/20 rounded-full blur-[60px] animate-pulse-glow" />
        <div className="relative z-10 mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-purple-500 to-indigo-500 text-white shadow-2xl shadow-purple-500/30">
          <GraduationCap className="h-10 w-10" />
        </div>
        <h1 className="text-4xl font-extrabold text-white tracking-tight relative z-10">Academy Mode</h1>
        <p className="mt-3 text-lg text-slate-400 font-medium relative z-10">
          Deep dive into errors. Generate structured educational modules.
        </p>
      </motion.div>

      <motion.div variants={itemVariants}>
        <AnimatedCard glowEffect className="p-1">
          <form onSubmit={onAnalyze} className="bg-black/20 p-8 rounded-[14px]">
            <div className="space-y-8">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-300">
                  Target Code Snippet
                </label>
                <div className="h-[200px]">
                  <CodeEditor
                    value={code}
                    onChange={setCode}
                    className="h-full border border-white/10"
                  />
                </div>
              </div>
              
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-300">
                  Error Message
                </label>
                <textarea
                  value={errorMessage}
                  onChange={(e) => setErrorMessage(e.target.value)}
                  rows={4}
                  className="w-full resize-y rounded-xl glass border-white/10 bg-black/40 px-5 py-4 text-sm text-slate-200 shadow-inner outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/50 transition-all font-mono"
                  placeholder="Paste the stack trace or output..."
                />
              </div>
            </div>
            
            <div className="mt-8 flex justify-center">
              <GlowButton
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto text-lg tracking-wide group"
              >
                <BookOpen className="h-5 w-5 mr-3 group-hover:scale-110 transition-transform" />
                Initialize Learning Module
              </GlowButton>
            </div>
          </form>
        </AnimatedCard>
      </motion.div>

      {loading && <Loader label="Compiling syllabus…" />}

      {data && !loading && (
        <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-4">
          <h2 className="text-2xl font-bold text-white mb-6 pl-2">Structured Analysis</h2>
          {sections.map((s) => {
            const isOpen = openId === s.id
            const Icon = s.icon

            const content = s.list
              ? (data.step_by_step_debugging || []).map((step, i) => (
                  <motion.li 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    key={i} 
                    className="flex gap-4 p-4 rounded-xl bg-white/5 border border-white/5 items-start"
                  >
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500/20 text-sm font-bold text-indigo-300 border border-indigo-500/20 shadow-inner">
                      {i + 1}
                    </span>
                    <span className="text-sm font-medium leading-relaxed text-slate-300 mt-1">{step}</span>
                  </motion.li>
                ))
              : s.link ? (
                  <div className="space-y-4 text-sm bg-cyan-500/5 p-6 rounded-xl border border-cyan-500/10">
                    <p className="font-semibold text-white text-base">{data.concept_to_learn}</p>
                    <a
                      href={data.concept_link}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-2 rounded-lg bg-cyan-500/20 px-5 py-2.5 text-cyan-300 font-bold tracking-wide transition hover:bg-cyan-500/30 border border-cyan-500/30"
                    >
                      Access External Knowledgebase
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300 bg-black/40 p-6 rounded-xl border border-white/5 font-medium">
                    {data[s.key]}
                  </p>
                )

            return (
              <motion.div
                variants={itemVariants}
                key={s.id}
                layout
                className="overflow-hidden rounded-2xl border border-white/10 bg-[#161f36] shadow-lg relative"
              >
                <button
                  type="button"
                  onClick={() => setOpenId(isOpen ? '' : s.id)}
                  className="w-full relative z-10 flex items-center justify-between gap-4 px-6 py-5 text-left transition hover:bg-white/5"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg bg-black/40 border border-white/5 ${s.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-lg font-bold text-white tracking-wide">{s.title}</span>
                  </div>
                  <ChevronDown
                    className={`h-5 w-5 shrink-0 text-slate-400 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
                  />
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="relative z-0"
                    >
                      <div className="border-t border-white/5 px-6 pb-6 pt-4">
                        {s.list ? <ol className="list-none space-y-3">{content}</ol> : content}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </motion.div>
      )}
    </motion.div>
  )
}
