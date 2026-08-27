import { useCallback, useEffect, useRef, useState } from 'react'

import { api } from '../lib/api'

/**
 * Reloj del lado del cliente sincronizado con la sesión del servidor: el
 * servidor es la fuente de verdad y el hook sólo interpola los segundos.
 */
export function useFocusTimer({ onComplete } = {}) {
  const [session, setSession] = useState(null)
  const [elapsed, setElapsed] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const anchor = useRef(null)

  const sync = useCallback((next) => {
    setSession(next)
    anchor.current = { seconds: next?.elapsed_seconds ?? 0, at: Date.now() }
    setElapsed(next?.elapsed_seconds ?? 0)
  }, [])

  useEffect(() => {
    api
      .activeSession()
      .then((data) => sync(data.session))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sync])

  useEffect(() => {
    if (session?.status !== 'running' || !anchor.current) return undefined
    const id = setInterval(() => {
      const { seconds, at } = anchor.current
      setElapsed(seconds + Math.floor((Date.now() - at) / 1000))
    }, 1000)
    return () => clearInterval(id)
  }, [session?.status])

  const run = useCallback(
    async (fn) => {
      setError(null)
      try {
        return await fn()
      } catch (err) {
        setError(err.message)
        throw err
      }
    },
    [],
  )

  const start = useCallback(
    (payload) => run(async () => sync(await api.startSession(payload))),
    [run, sync],
  )
  const pause = useCallback(
    () => run(async () => sync(await api.pauseSession(session.id))),
    [run, session, sync],
  )
  const resume = useCallback(
    () => run(async () => sync(await api.resumeSession(session.id))),
    [run, session, sync],
  )
  const complete = useCallback(
    () =>
      run(async () => {
        const result = await api.completeSession(session.id)
        sync(null)
        onComplete?.(result)
        return result
      }),
    [run, session, sync, onComplete],
  )
  const abandon = useCallback(
    () =>
      run(async () => {
        await api.abandonSession(session.id)
        sync(null)
      }),
    [run, session, sync],
  )

  const plannedSeconds = (session?.planned_minutes ?? 25) * 60
  return {
    session,
    elapsed,
    remaining: Math.max(0, plannedSeconds - elapsed),
    progress: session ? Math.min(1, elapsed / plannedSeconds) : 0,
    loading,
    error,
    start,
    pause,
    resume,
    complete,
    abandon,
  }
}
