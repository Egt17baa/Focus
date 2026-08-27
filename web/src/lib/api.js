const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const ACCESS_KEY = 'focus.access_token'
const REFRESH_KEY = 'focus.refresh_token'

export const tokens = {
  get access() {
    return localStorage.getItem(ACCESS_KEY)
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY)
  },
  save({ access_token, refresh_token }) {
    if (access_token) localStorage.setItem(ACCESS_KEY, access_token)
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token)
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function parse(response) {
  const text = await response.text()
  return text ? JSON.parse(text) : {}
}

async function refreshAccessToken() {
  if (!tokens.refresh) return false
  const response = await fetch(`${BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${tokens.refresh}` },
  })
  if (!response.ok) return false
  tokens.save(await parse(response))
  return true
}

export async function request(path, { method = 'GET', body, auth = true, retry = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (response.status === 401 && auth && retry && (await refreshAccessToken())) {
    return request(path, { method, body, auth, retry: false })
  }

  const data = await parse(response)
  if (!response.ok) throw new ApiError(data.error || 'Error inesperado', response.status)
  return data
}

export const api = {
  register: (payload) => request('/auth/register', { method: 'POST', body: payload, auth: false }),
  login: (payload) => request('/auth/login', { method: 'POST', body: payload, auth: false }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  me: () => request('/users/me'),
  updateMe: (payload) => request('/users/me', { method: 'PATCH', body: payload }),

  activeSession: () => request('/sessions/active'),
  listSessions: (page = 1) => request(`/sessions?page=${page}&per_page=10`),
  startSession: (payload) => request('/sessions', { method: 'POST', body: { source: 'web', ...payload } }),
  pauseSession: (id) => request(`/sessions/${id}/pause`, { method: 'POST' }),
  resumeSession: (id) => request(`/sessions/${id}/resume`, { method: 'POST' }),
  completeSession: (id) => request(`/sessions/${id}/complete`, { method: 'POST' }),
  abandonSession: (id) => request(`/sessions/${id}/abandon`, { method: 'POST' }),

  stats: (days = 30) => request(`/stats/overview?days=${days}`),
  achievements: () => request('/stats/achievements'),
  leaderboard: () => request('/stats/leaderboard'),

  challenges: () => request('/challenges'),
  createChallenge: (payload) => request('/challenges', { method: 'POST', body: payload }),
  joinChallenge: (id) => request(`/challenges/${id}/join`, { method: 'POST' }),
  leaveChallenge: (id) => request(`/challenges/${id}/leave`, { method: 'DELETE' }),

  blockedApps: () => request('/blocked-apps'),
  addBlockedApp: (payload) => request('/blocked-apps', { method: 'POST', body: payload }),
  updateBlockedApp: (id, payload) => request(`/blocked-apps/${id}`, { method: 'PATCH', body: payload }),
  deleteBlockedApp: (id) => request(`/blocked-apps/${id}`, { method: 'DELETE' }),
}
