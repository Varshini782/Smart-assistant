import axios from 'axios'

/**
 * Axios instance for the Smart Debugging FastAPI backend.
 */
const api = axios.create({
  baseURL: 'https://smart-assistant-yi82.onrender.com',
  timeout: 120000,
})

export default api

/** @param {FormData} formData */
export async function processInput(formData) {
  // Let Axios set multipart boundary automatically (do not set Content-Type manually).
  const { data } = await api.post('/process-input', formData)
  return data
}

/**
 * @param {string} code
 * @param {string} errorMessage
 * @param {'beginner'|'intermediate'|'advanced'} level
 */
export async function explainError(code, errorMessage, level) {
  const { data } = await api.post('/explain-error', {
    code,
    error_message: errorMessage,
    level,
  })
  return data
}

/** Fetch all three explanation levels in parallel. */
export async function explainErrorAllLevels(code, errorMessage) {
  const levels = ['beginner', 'intermediate', 'advanced']
  const results = await Promise.all(
    levels.map((level) => explainError(code, errorMessage, level))
  )
  return {
    beginner: results[0],
    intermediate: results[1],
    advanced: results[2],
  }
}

/**
 * @param {string} userId
 * @param {string} errorType
 */
export async function getRecommendations(userId, errorType) {
  const { data } = await api.get('/recommendations', {
    params: { user_id: userId, error_type: errorType },
  })
  return data
}

/** @param {string} errorSnippet */
export async function getSimilarErrors(errorSnippet) {
  const { data } = await api.get('/similar-errors', {
    params: { error: errorSnippet },
  })
  return data
}

/** @param {string} userId */
export async function getDashboard(userId) {
  const { data } = await api.get('/dashboard', { params: { user_id: userId } })
  return data
}

export async function getDailyChallenge() {
  const { data } = await api.get('/daily-challenge')
  return data
}

/** @param {{ user_id: string, code: string }} payload */
export async function submitSolution(payload) {
  const { data } = await api.post('/submit-solution', payload)
  return data
}

/** @param {string} userId */
export async function getStreak(userId) {
  const { data } = await api.get('/streak', { params: { user_id: userId } })
  return data
}

/** @param {{ code: string, error_message: string }} payload */
export async function postLearningMode(payload) {
  const { data } = await api.post('/learning-mode', payload)
  return data
}
