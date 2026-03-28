import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Sparkles, UploadCloud, Code, Image as ImageIcon } from 'lucide-react'
import AnimatedCard from '../components/UI/AnimatedCard.jsx'
import GlowButton from '../components/UI/GlowButton.jsx'
import CodeEditor from '../components/UI/CodeEditor.jsx'
import Loader from '../components/Loader.jsx'
import FileUpload from '../components/FileUpload.jsx'
import ImageUpload from '../components/ImageUpload.jsx'
import { explainErrorAllLevels, processInput } from '../services/api.js'
import { guessErrorType } from '../utils/errorType.js'
import { loadHistory, saveHistoryEntry } from '../utils/history.js'

const USER_KEY = 'sda_user_id'

export default function Home() {
  const navigate = useNavigate()
  const [codeText, setCodeText] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [codeFile, setCodeFile] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [userId, setUserId] = useState(() => localStorage.getItem(USER_KEY) || 'guest')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState(() => loadHistory())

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!errorMessage.trim()) {
      toast.error('Please paste the error message from your compiler or runtime.')
      return
    }

    const hasInput = imageFile || codeFile || codeText.trim().length > 0
    if (!hasInput) {
      toast.error('Add code as text, upload a code file, or upload a screenshot.')
      return
    }

    localStorage.setItem(USER_KEY, userId.trim() || 'guest')
    setLoading(true)

    const run = async () => {
      const fd = new FormData()
      if (imageFile) {
        fd.append('file', imageFile)
      } else if (codeFile) {
        fd.append('file', codeFile)
      } else {
        fd.append('text', codeText)
      }

      const processed = await processInput(fd)
      const extracted = processed.extracted_code || ''
      if (!extracted.trim()) {
        throw new Error('No code extracted. Try clearer input or paste code manually.')
      }

      const explanations = await explainErrorAllLevels(extracted, errorMessage.trim())
      const errorType = guessErrorType(errorMessage)

      saveHistoryEntry({
        errorMessage: errorMessage.trim(),
        codePreview: extracted.slice(0, 400),
      })
      setHistory(loadHistory())

      navigate('/results', {
        state: {
          extractedCode: extracted,
          errorMessage: errorMessage.trim(),
          errorType,
          userId: (userId || 'guest').trim(),
          explanations,
        },
      })
    }

    try {
      await toast.promise(run(), {
        loading: 'Interrogating the mainframe...',
        success: 'Done! Opening results.',
        error: (err) => {
          const d = err?.response?.data?.detail
          if (Array.isArray(d)) return d.map((x) => x.msg || x).join(' ')
          if (typeof d === 'string') return d
          return err?.message || 'Something went wrong. Is the API running?'
        },
      })
    } catch {
      /* toast handles */
    } finally {
      setLoading(false)
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  }

  return (
    <>
      {loading && <Loader fullPage label="Analyzing your code..." />}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="mx-auto max-w-6xl space-y-12"
      >
        <motion.div variants={itemVariants} className="text-center relative">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-indigo-500/20 rounded-full blur-3xl animate-pulse-glow" />
          <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-7xl mb-6 relative">
            <span className="text-gradient">Debug Smarter,</span> <br/> Learn Faster
          </h1>
          <p className="mx-auto max-w-3xl text-lg text-slate-400 font-medium">
            Paste your code, upload a file, or drop a screenshot. We'll analyze the error and guide you to the solution with AI.
          </p>
        </motion.div>

        <form onSubmit={onSubmit}>
          <div className="grid gap-8 lg:grid-cols-2">
            <motion.div variants={itemVariants} className="animate-anti-gravity h-full flex flex-col">
              <AnimatedCard glowEffect className="flex-1 flex flex-col h-full space-y-6 !p-8">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400">
                    <Code className="w-5 h-5" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">Code & Error</h2>
                </div>
                
                <div className="flex-1 min-h-[300px]">
                  <CodeEditor 
                    value={codeText} 
                    onChange={setCodeText} 
                    className="h-full border border-white/10" 
                  />
                </div>

                <div className="mt-4">
                  <label className="mb-2 block text-sm font-semibold text-indigo-200">
                    Error Message (Required)
                  </label>
                  <textarea
                    value={errorMessage}
                    onChange={(e) => setErrorMessage(e.target.value)}
                    rows={4}
                    placeholder="Paste the traceback or error text here..."
                    className="w-full resize-y rounded-xl glass border-white/10 bg-black/40 px-5 py-4 text-sm text-slate-200 shadow-inner outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all font-mono"
                  />
                </div>
              </AnimatedCard>
            </motion.div>

            <motion.div variants={itemVariants} className="space-y-8 flex flex-col">
              <AnimatedCard className="!p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400">
                    <UploadCloud className="w-5 h-5" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">Upload Files</h2>
                </div>
                
                <div className="space-y-6">
                  <div className="glass rounded-xl p-4 border-white/10">
                    <ImageUpload
                      file={imageFile}
                      disabled={!!codeFile}
                      onFileChange={(f) => {
                        setImageFile(f)
                        setCodeFile(null)
                      }}
                    />
                  </div>
                  <div className="glass rounded-xl p-4 border-white/10">
                    <FileUpload
                      file={codeFile}
                      disabled={!!imageFile}
                      onFileChange={(f) => {
                        setCodeFile(f)
                        setImageFile(null)
                      }}
                    />
                  </div>
                </div>
              </AnimatedCard>
              
              <div className="flex justify-center flex-1 items-end">
                <motion.div variants={itemVariants} className="w-full">
                  <GlowButton 
                    type="submit" 
                    disabled={loading} 
                    className="w-full py-5 text-lg font-bold tracking-wide group"
                  >
                    <Sparkles className="h-6 w-6 mr-3 group-hover:animate-spin-slow" />
                    {loading ? 'Analyzing...' : 'Analyze Error'}
                  </GlowButton>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </form>

        {history.length > 0 && (
          <motion.div variants={itemVariants}>
            <AnimatedCard className="mt-12 !p-8">
              <h2 className="text-xl font-bold text-white mb-6">Recent Sessions</h2>
              <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {history.slice(0, 6).map((h, i) => (
                  <motion.li
                    whileHover={{ scale: 1.05 }}
                    key={`${h.at}-${i}`}
                    className="rounded-2xl border border-white/10 bg-white/5 p-5 transition-all hover:bg-white/10 cursor-pointer"
                  >
                    <p className="font-mono text-xs text-indigo-300 mb-2">
                      {new Date(h.at).toLocaleString()}
                    </p>
                    <p className="line-clamp-2 text-sm text-slate-300 font-medium leading-relaxed">{h.errorMessage}</p>
                  </motion.li>
                ))}
              </ul>
            </AnimatedCard>
          </motion.div>
        )}
      </motion.div>
    </>
  )
}
