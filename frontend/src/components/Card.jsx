export default function Card({ children, className = '', title, subtitle, actions }) {
  return (
    <div
      className={`glass rounded-2xl p-6 transition-shadow hover:shadow-xl dark:shadow-slate-900/40 ${className}`}
    >
      {(title || subtitle || actions) && (
        <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
          <div>
            {title && (
              <h2 className="text-lg font-semibold tracking-tight text-slate-900 dark:text-white">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex shrink-0 gap-2">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  )
}
