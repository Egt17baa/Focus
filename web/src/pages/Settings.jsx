import { useState } from 'react'

import { useAuth } from '../context/AuthContext.jsx'
import { api } from '../lib/api'

const EMOJIS = ['🎯', '🧠', '🚀', '🌱', '🦉', '🔥', '📚', '🧘']

export default function Settings() {
  const { user, setUser } = useAuth()
  const [goal, setGoal] = useState(user.daily_goal_minutes)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  const save = async (payload) => {
    setError(null)
    try {
      setUser(await api.updateMe(payload))
      setMessage('Ajustes guardados')
      setTimeout(() => setMessage(null), 2000)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-bold">Ajustes</h1>

      <section className="card space-y-3">
        <div>
          <label className="label" htmlFor="goal">
            Meta diaria de foco (minutos)
          </label>
          <input
            id="goal"
            type="number"
            min="5"
            max="1440"
            className="input"
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
          />
        </div>
        <button className="btn-primary" onClick={() => save({ daily_goal_minutes: Number(goal) })}>
          Guardar meta
        </button>
      </section>

      <section className="card">
        <p className="label">Avatar</p>
        <div className="flex flex-wrap gap-2">
          {EMOJIS.map((emoji) => (
            <button
              key={emoji}
              onClick={() => save({ avatar_emoji: emoji })}
              className={`rounded-xl border px-3 py-2 text-xl transition ${
                user.avatar_emoji === emoji ? 'border-sky-400 bg-sky-400/10' : 'border-white/10'
              }`}
            >
              {emoji}
            </button>
          ))}
        </div>
      </section>

      <section className="card text-sm text-slate-400">
        <p>
          Cuenta: <span className="text-slate-200">{user.email}</span>
        </p>
        <p>
          Puntos totales: <span className="text-slate-200">{user.total_focus_points}</span> ·{' '}
          {user.level_name}
        </p>
      </section>

      {message ? <p className="text-sm text-emerald-400">{message}</p> : null}
      {error ? <p className="text-sm text-rose-400">{error}</p> : null}
    </div>
  )
}
