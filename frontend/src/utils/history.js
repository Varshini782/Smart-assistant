const KEY = 'sda_debug_history'
const MAX = 12

/**
 * @typedef {{ at: string, errorMessage: string, codePreview: string }} HistoryItem
 */

/** @returns {HistoryItem[]} */
export function loadHistory() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

/** @param {Omit<HistoryItem, 'at'>} item */
export function saveHistoryEntry(item) {
  const prev = loadHistory()
  const next = [
    {
      at: new Date().toISOString(),
      errorMessage: item.errorMessage.slice(0, 500),
      codePreview: item.codePreview.slice(0, 400),
    },
    ...prev.filter(
      (x) =>
        x.errorMessage !== item.errorMessage || x.codePreview !== item.codePreview
    ),
  ].slice(0, MAX)
  localStorage.setItem(KEY, JSON.stringify(next))
}
