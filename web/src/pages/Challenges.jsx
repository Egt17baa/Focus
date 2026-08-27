import { useEffect, useState } from 'react'

import { api } from '../lib/api'

const emptyForm = { title: '', description: '', metric: 'minutes', target_value: 300, reward_points: 200 }

export default function Challenges() {
  const [challenges, setChallenges] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(false)

  const load = () => api.challenges().then((data) => setChallenges(data.challenges))

  useEffect(() => {
    load()
  }, [])

  const submit = async (event) => {
    event.preventDefault()
    setError(null)
    try {
      await api.createChallenge({ ...form, target_value: Number(form.target_value) })
      setForm(emptyForm)
      setCreating(false)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const toggleParticipation = async (challenge) => {
    try {
      if (challenge.my_participation) await api.leaveChallenge(challenge.id)
      else await api.joinChallenge(challenge.id)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">Retos activos</h1>
        <button className="btn-ghost" onClick={() => setCreating((value) => !value)}>
          {creating ? 'Cancelar' : 'Crear reto'}
        </button>
      </div>

      {creating && (
        <form onSubmit={submit} className="card space-y-3">
          <div>
            <label className="label" htmlFor="title">
              Título
            </label>
            <input
              id="title"
              className="input"
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              required
              minLength={3}
            />
          </div>
          <div>
            <label className="label" htmlFor="description">
              Descripción
            </label>
            <input
              id="description"
              className="input"
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="label" htmlFor="metric">
                Métrica
              </label>
              <select
                id="metric"
                className="input"
                value={form.metric}
                onChange={(event) => setForm({ ...form, metric: event.target.value })}
              >
                <option value="minutes">Minutos</option>
                <option value="sessions">Sesiones</option>
              </select>
            </div>
            <div>
              <label className="label" htmlFor="target">
                Objetivo
              </label>
              <input
                id="target"
                type="number"
                min="1"
                className="input"
                value={form.target_value}
                onChange={(event) => setForm({ ...form, target_value: event.target.value })}
              />
            </div>
            <div>
              <label className="label" htmlFor="reward">
                Recompensa
              </label>
              <input
                id="reward"
                type="number"
                min="0"
                className="input"
                value={form.reward_points}
                onChange={(event) => setForm({ ...form, reward_points: event.target.value })}
              />
            </div>
          </div>
          <button className="btn-primary w-full">Crear reto</button>
        </form>
      )}

      {error ? <p className="text-sm text-rose-400">{error}</p> : null}

      {challenges.length === 0 ? (
        <p className="text-slate-400">No hay retos abiertos. ¡Crea el primero!</p>
      ) : (
        <ul className="grid gap-3 md:grid-cols-2">
          {challenges.map((challenge) => {
            const participation = challenge.my_participation
            const progress = participation
              ? Math.min(1, participation.progress / challenge.target_value)
              : 0
            return (
              <li key={challenge.id} className="card space-y-3">
                <div>
                  <h2 className="font-semibold">{challenge.title}</h2>
                  <p className="text-sm text-slate-400">{challenge.description}</p>
                </div>
                <p className="text-xs text-slate-500">
                  Objetivo: {challenge.target_value}{' '}
                  {challenge.metric === 'minutes' ? 'minutos' : 'sesiones'} · +{challenge.reward_points} pts ·{' '}
                  {challenge.participants} participantes
                </p>
                {participation && (
                  <div>
                    <div className="h-2 overflow-hidden rounded-full bg-white/10">
                      <div
                        className="h-full rounded-full bg-emerald-400"
                        style={{ width: `${Math.round(progress * 100)}%` }}
                      />
                    </div>
                    <p className="mt-1 text-xs text-slate-400">
                      {participation.progress} / {challenge.target_value}
                      {participation.completed ? ' · ¡Completado!' : ''}
                    </p>
                  </div>
                )}
                <button
                  className={participation ? 'btn-ghost w-full' : 'btn-primary w-full'}
                  onClick={() => toggleParticipation(challenge)}
                >
                  {participation ? 'Salir del reto' : 'Unirme'}
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
