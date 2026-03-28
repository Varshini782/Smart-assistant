import { useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { FileCode, Upload } from 'lucide-react'

const ACCEPT = '.py,.java,.c'

export default function FileUpload({ file, onFileChange, disabled }) {
  const [drag, setDrag] = useState(false)

  const onDrop = useCallback(
    (e) => {
      e.preventDefault()
      setDrag(false)
      const f = e.dataTransfer?.files?.[0]
      if (f && onFileChange) onFileChange(f)
    },
    [onFileChange]
  )

  return (
    <div>
      <p className="mb-2 text-sm font-medium text-slate-700 dark:text-slate-300">Code file</p>
      <motion.label
        htmlFor="code-file"
        onDragOver={(e) => {
          e.preventDefault()
          setDrag(true)
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        animate={{ scale: drag ? 1.02 : 1 }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 transition-colors ${
          drag
            ? 'border-brand-500 bg-brand-50/80 dark:bg-brand-950/40'
            : 'border-slate-300 bg-slate-50/50 hover:border-brand-400 dark:border-slate-600 dark:bg-slate-900/50'
        } ${disabled ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input
          id="code-file"
          type="file"
          accept={ACCEPT}
          className="sr-only"
          disabled={disabled}
          onChange={(e) => {
            const f = e.target.files?.[0]
            if (f) onFileChange?.(f)
          }}
        />
        <Upload className="mb-2 h-8 w-8 text-brand-500" />
        <span className="text-center text-sm font-medium text-slate-700 dark:text-slate-200">
          Drop .py, .java, or .c here
        </span>
        <span className="mt-1 text-xs text-slate-500">or click to browse</span>
        {file && (
          <span className="mt-3 flex items-center gap-2 rounded-lg bg-white px-3 py-1.5 text-xs font-mono text-brand-700 shadow dark:bg-slate-800 dark:text-brand-300">
            <FileCode className="h-4 w-4" />
            {file.name}
          </span>
        )}
      </motion.label>
    </div>
  )
}
