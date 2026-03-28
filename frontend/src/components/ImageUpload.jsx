import { useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { ImageIcon, Upload } from 'lucide-react'

const ACCEPT = 'image/png,image/jpeg,image/webp,image/gif,.png,.jpg,.jpeg,.webp,.gif'

export default function ImageUpload({ file, onFileChange, disabled }) {
  const [drag, setDrag] = useState(false)

  const onDrop = useCallback(
    (e) => {
      e.preventDefault()
      setDrag(false)
      const f = e.dataTransfer?.files?.[0]
      if (f && f.type.startsWith('image/') && onFileChange) onFileChange(f)
    },
    [onFileChange]
  )

  return (
    <div>
      <p className="mb-2 text-sm font-medium text-slate-700 dark:text-slate-300">Screenshot (OCR)</p>
      <motion.label
        htmlFor="image-file"
        onDragOver={(e) => {
          e.preventDefault()
          setDrag(true)
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        animate={{ scale: drag ? 1.02 : 1 }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-8 transition-colors ${
          drag
            ? 'border-violet-500 bg-violet-50/80 dark:bg-violet-950/40'
            : 'border-slate-300 bg-slate-50/50 hover:border-violet-400 dark:border-slate-600 dark:bg-slate-900/50'
        } ${disabled ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input
          id="image-file"
          type="file"
          accept={ACCEPT}
          className="sr-only"
          disabled={disabled}
          onChange={(e) => {
            const f = e.target.files?.[0]
            if (f) onFileChange?.(f)
          }}
        />
        <Upload className="mb-2 h-7 w-7 text-violet-500" />
        <span className="text-center text-sm font-medium text-slate-700 dark:text-slate-200">
          Drop an image of your code
        </span>
        {file && (
          <span className="mt-3 flex items-center gap-2 rounded-lg bg-white px-3 py-1.5 text-xs font-medium text-violet-700 shadow dark:bg-slate-800 dark:text-violet-300">
            <ImageIcon className="h-4 w-4" />
            {file.name}
          </span>
        )}
      </motion.label>
    </div>
  )
}
