import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { api, tokens } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!tokens.access) {
      setLoading(false)
      return
    }
    api
      .me()
      .then(setUser)
      .catch(() => tokens.clear())
      .finally(() => setLoading(false))
  }, [])

  const authenticate = useCallback(async (fn) => {
    const data = await fn()
    tokens.save(data)
    setUser(data.user)
    return data.user
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      setUser,
      login: (payload) => authenticate(() => api.login(payload)),
      register: (payload) => authenticate(() => api.register(payload)),
      logout: async () => {
        try {
          await api.logout()
        } finally {
          tokens.clear()
          setUser(null)
        }
      },
    }),
    [user, loading, authenticate],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return context
}
