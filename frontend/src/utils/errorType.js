/**
 * Best-effort extraction of an error type string for recommendation APIs.
 * @param {string} message
 */
export function guessErrorType(message) {
  const s = String(message || '').trim()
  if (!s) return 'Error'

  const line = s.split('\n')[0]
  const m =
    line.match(/^(\w+Error)\b/) ||
    line.match(/^(\w+Exception)\b/) ||
    line.match(/\b(\w+Error)\b/) ||
    line.match(/\b(\w+Exception)\b/)

  return m ? m[1] : 'Error'
}
