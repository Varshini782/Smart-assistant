import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { AlertTriangle, Copy, ExternalLink, Lightbulb, CheckCircle2, AlertCircle, BookOpen } from 'lucide-react'
import AnimatedCard from '../components/UI/AnimatedCard.jsx'
import Loader from '../components/Loader.jsx'
import Tabs from '../components/UI/Tabs.jsx'
import { getRecommendations, getSimilarErrors } from '../services/api.js'

export default function Results() {
  const navigate = useNavigate()
  const { state } = useLocation()
  const [rec, setRec] = useState(null)
  const [similar, setSimilar] = useState(null)
  const [loadingExtra, setLoadingExtra] = useState(true)
  const [tab, setTab] = useState('beginner')

  const extractedCode = state?.extractedCode
  const errorMessage = state?.errorMessage
  const errorType = state?.errorType
  const userId = state?.userId || 'guest'
  const explanations = state?.explanations

  useEffect(() => {
    if (!extractedCode || !errorMessage || !explanations) {
      navigate('/', { replace: true })
      return
    }

    let cancelled = false
    ;(async () => {
      setLoadingExtra(true)
      try {
        const [r, s] = await Promise.all([
          getRecommendations(userId, errorType || 'Error'),
          getSimilarErrors(errorMessage.slice(0, 2000)),
        ])
        if (!cancelled) {
          setRec(r)
          setSimilar(s)
        }
      } catch (e) {
        if (!cancelled) {
          toast.error('Could not load recommendations or similar errors.')
          console.error(e)
        }
      } finally {
        if (!cancelled) setLoadingExtra(false)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [extractedCode, errorMessage, errorType, userId, explanations, navigate])

  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(extractedCode || '')
      toast.success('Code copied')
    } catch {
      toast.error('Copy failed')
    }
  }

  if (!extractedCode || !explanations) {
    return null
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  }

  const tabContent = {
    beginner: explanations.beginner?.explanation,
    intermediate: explanations.intermediate?.explanation,
    advanced: explanations.advanced?.explanation,
  }

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-8 max-w-5xl mx-auto">
      <motion.div variants={itemVariants} className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between py-6 border-b border-white/10">
        <div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">Analysis Results</h1>
          <p className="text-slate-400 font-medium">
            Identified Error: <span className="px-2 py-0.5 rounded-md bg-red-500/20 text-red-400 font-mono text-sm shadow-inner shadow-red-500/20">{errorType || 'Unknown Syntax'}</span>
          </p>
        </div>
        <Link
          to="/"
          className="text-sm font-semibold text-indigo-400 hover:text-cyan-300 transition-colors flex items-center gap-2"
        >
          ← New session
        </Link>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div className="lg:col-span-2 space-y-8">
          
          <motion.div variants={itemVariants}>
            <AnimatedCard className="!p-0 overflow-hidden">
              <div className="flex justify-between items-center px-6 py-4 bg-black/40 border-b border-white/10">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span>
                  Analyzed Code
                </h2>
                <button
                  onClick={copyCode}
                  className="flex items-center gap-2 p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition-colors text-sm font-medium"
                >
                  <Copy className="w-4 h-4" /> Copy
                </button>
              </div>
              <pre className="p-6 text-sm font-mono text-slate-300 overflow-x-auto min-h-[150px]">
                {extractedCode}
              </pre>
            </AnimatedCard>
          </motion.div>

          
          <motion.div variants={itemVariants}>
            <AnimatedCard glowEffect className="relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl" />
              <div className="relative z-10 flex flex-col gap-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">Error Explanation</h2>
                  <p className="text-slate-400 text-sm">Choose your preferred depth of technical detail.</p>
                </div>
                
                <Tabs
                  tabs={[
                    { id: 'beginner', label: 'Beginner' },
                    { id: 'intermediate', label: 'Intermediate' },
                    { id: 'advanced', label: 'Advanced' },
                  ]}
                  activeTab={tab}
                  onChange={setTab}
                />
                
                <div className="glass rounded-xl p-6 border-white/10 bg-black/20 text-slate-200 leading-relaxed font-medium min-h-[120px]">
                  <AnimatePresence mode="wait">
                    <motion.p
                      key={tab}
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      transition={{ duration: 0.2 }}
                      className="whitespace-pre-wrap"
                    >
                      {tabContent[tab]}
                    </motion.p>
                  </AnimatePresence>
                </div>
              </div>
            </AnimatedCard>
          </motion.div>

          <motion.div variants={itemVariants}>
            <AnimatedCard className="border-l-4 border-l-cyan-400">
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 flex flex-shrink-0 items-center justify-center">
                  <Lightbulb className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white mb-2">Fix Suggestions</h2>
                  <p className="text-slate-300 leading-relaxed text-sm">
                    {explanations.beginner?.explanation.split('.')[0]}. Review the code above and ensure all blocks are properly aligned and syntax is correct based on the highlighted errors.
                  </p>
                </div>
              </div>
            </AnimatedCard>
          </motion.div>

        </div>

        
        <div className="lg:col-span-1 space-y-8">
          <motion.div variants={itemVariants}>
            <AnimatedCard className="h-full">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-indigo-400" /> Recommendations
              </h3>
              
              {loadingExtra && !rec ? (
                <div className="py-8"><Loader /></div>
              ) : rec ? (
                <div className="space-y-6">
                  {rec.debugging_tips?.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Tips</h4>
                      <ul className="space-y-2">
                        {rec.debugging_tips.slice(0,3).map((t, i) => (
                          <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                            <span className="text-indigo-500 mt-1">•</span>
                            <span className="leading-tight">{t}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {rec.concepts_to_revise?.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Revise</h4>
                      <div className="flex flex-wrap gap-2">
                        {rec.concepts_to_revise.map((t, i) => (
                          <span key={i} className="px-2.5 py-1 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-medium">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No specific recommendations.</p>
              )}
            </AnimatedCard>
          </motion.div>

          <motion.div variants={itemVariants}>
            <AnimatedCard>
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-400" /> Similar Errors
              </h3>
              
              {loadingExtra && !similar ? (
                <div className="py-8"><Loader /></div>
              ) : similar ? (
                <div className="space-y-3 pb-2">
                  {similar.common_mistake && (
                    <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/20 text-orange-300 text-sm mb-4">
                      {similar.common_mistake}
                    </div>
                  )}
                  <ul className="space-y-2">
                    {(similar.similar_errors || []).slice(0, 3).map((item, i) => (
                      <li key={i} className="text-xs font-mono p-2 rounded-lg bg-black/40 text-slate-400 border border-white/5 truncate">
                        {typeof item === 'string' ? item : item?.message || JSON.stringify(item)}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="text-sm text-slate-500">No similar anomalies found.</p>
              )}
            </AnimatedCard>
          </motion.div>
          
          <motion.div variants={itemVariants} className="text-center pt-4">
             <a
              href="https://docs.python.org/3/tutorial/errors.html"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-white transition-colors"
            >
              <BookOpen className="w-4 h-4" /> Docs & Resources
            </a>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
