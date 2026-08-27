import { Ban, Pause, Play, Square } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

import StatCard from '../components/StatCard.jsx'
import TimerRing from '../components/TimerRing.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { useFocusTimer } from '../hooks/useFocusTimer.js'
import { api } from '../lib/api'
import { formatClock } from '../lib/time.js'

const PRESETS = [
  { label: 'Pomodoro', minutes: 25, mode: 'pomodoro' },
  { label: 'Foco largo', minutes: 50, mode: 'deep_work' },
  { label: 'Inmersión', minutes: 90, mode: 'deep_work' },
  { label: 'Descanso', minutes: 5, mode: 'break' },
]

function notify(title, body) {
  if (typeof Notification === 'undefined' || Notification.permission !== 'granted') return
  new Notification(title, { body, icon: '/icon-192.png' })
}

export default function Dashboard() {
  const { user, setUser } = useAuth()
  const [preset, setPreset] = useState(PRESETS[0])
  const [tag, setTag] = useState('')
  const [overview, setOverview] = useState(null)
  const [reward, setReward] = useState(null)

  const handleComplete = useCallback(
    (result) => {
      setUser(result.user)
      setReward(result)
      notify('¡Sesión completada!', `+${result.session.points_earned} puntos de enfoque`)
      api.stats(7).then((data) => setOverview(data.overview))
    },
    [setUser],
  )

  const timer = useFocusTimer({ onComplete: handleComplete })
  const { session, elapsed, remaining, progress } = timer

  useEffect(() => {
    api.stats(7).then((data) => setOverview(data.overview))
  }, [])

  useEffect(() => {
    if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [])

  useEffect(() => {
    if (session?.status === 'running' && remaining === 0) {
      notify('Objetivo alcanzado', 'Puedes cerrar la sesión y guardar tus puntos')
    }
  }, [session?.status, remaining])

  useEffect(() => {
    document.title = session?.status === 'running' ? `${formatClock(remaining)} · Focus` : 'Focus'
  }, [session?.status, remaining])

  const startPreset = () =>
    timer.start({ planned_minutes: preset.minutes, mode: preset.mode, tag: tag.trim() || null })

  return (
    <div className="space-y-6">
      <section className="card">
        <div className="flex flex-col items-center gap-6 md:flex-row md:items-center md:justify-around">
          <TimerRing
            progress={progress}
            label={session ? formatClock(remaining) : formatClock(preset.minutes * 60)}
            caption={
              session
                ? `${session.status === 'paused' ? 'En pausa' : 'En curso'} · ${Math.floor(elapsed / 60)} min de foco`
                : 'Elige un modo y empieza'
            }
          />

          <div className="w-full max-w-xs space-y-4">
            {!session && (
              <>
                <div className="grid grid-cols-2 gap-2">
                  {PRESETS.map((item) => (
                    <button
                      key={item.label}
                      onClick={() => setPreset(item)}
                      className={`rounded-xl border px-3 py-2 text-sm transition ${
                        preset.label === item.label
                          ? 'border-sky-400 bg-sky-400/10 text-sky-200'
                          : 'border-white/10 text-slate-300 hover:border-white/25'
                      }`}
                    >
                      {item.label}
                      <span className="block text-xs text-slate-500">{item.minutes} min</span>
                    </button>
                  ))}
                </div>
                <div>
                  <label className="label" htmlFor="tag">
                    Etiqueta (opcional)
                  </label>
                  <input
                    id="tag"
                    className="input"
                    value={tag}
                    onChange={(event) => setTag(event.target.value)}
                    placeholder="estudio, trabajo, lectura…"
                  />
                </div>
                <button className="btn-primary w-full" onClick={startPreset}>
                  <Play size={16} /> Empezar sesión
                </button>
              </>
            )}

            {session && (
              <div className="space-y-3">
                <p className="text-sm text-slate-400">
                  Objetivo: {session.planned_minutes} min
                  {session.tag ? ` · ${session.tag}` : ''}
                  {session.interruptions ? ` · ${session.interruptions} interrupciones` : ''}
                </p>
                <div className="flex gap-2">
                  {session.status === 'running' ? (
                    <button className="btn-ghost flex-1" onClick={timer.pause}>
                      <Pause size={16} /> Pausar
                    </button>
                  ) : (
                    <button className="btn-ghost flex-1" onClick={timer.resume}>
                      <Play size={16} /> Reanudar
                    </button>
                  )}
                  <button className="btn-primary flex-1" onClick={timer.complete}>
                    <Square size={16} /> Completar
                  </button>
                </div>
                <button className="btn-danger w-full" onClick={timer.abandon}>
                  <Ban size={16} /> Abandonar (sin puntos)
                </button>
              </div>
            )}

            {timer.error ? <p className="text-sm text-rose-400">{timer.error}</p> : null}
          </div>
        </div>
      </section>

      {reward ? (
        <section className="card animate-pop border-sky-400/40 bg-sky-400/10">
          <p className="font-semibold text-sky-200">
            +{reward.session.points_earned} puntos · {reward.session.focus_minutes} min de foco
          </p>
          {reward.unlocked_achievements.length > 0 && (
            <p className="mt-1 text-sm text-slate-300">
              Logros desbloqueados:{' '}
              {reward.unlocked_achievements
                .map((item) => `${item.achievement.icon} ${item.achievement.name}`)
                .join(' · ')}
            </p>
          )}
          <button className="btn-ghost mt-3" onClick={() => setReward(null)}>
            Cerrar
          </button>
        </section>
      ) : null}

      <section className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatCard
          label="Hoy"
          value={`${overview?.today_minutes ?? 0} min`}
          hint={`Meta ${user.daily_goal_minutes} min`}
        />
        <StatCard label="Racha" value={`${overview?.current_streak ?? 0} días`} accent="text-amber-400" />
        <StatCard label="Esta semana" value={`${overview?.week_minutes ?? 0} min`} accent="text-emerald-400" />
        <StatCard
          label="Nivel"
          value={user.level_name}
          hint={
            user.points_to_next_level === null
              ? 'Nivel máximo'
              : `${user.points_to_next_level} pts para subir`
          }
          accent="text-fuchsia-400"
        />
      </section>

      <section className="card">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-slate-400">Meta diaria</span>
          <span className="font-semibold">
            {overview?.today_minutes ?? 0} / {user.daily_goal_minutes} min
          </span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-sky-500 to-emerald-400 transition-all"
            style={{ width: `${Math.round((overview?.daily_goal_progress ?? 0) * 100)}%` }}
          />
        </div>
      </section>
    </div>
  )
}
