import { useEffect, useState } from 'react'

import BarChart from '../components/BarChart.jsx'
import StatCard from '../components/StatCard.jsx'
import { api } from '../lib/api'

const RANGES = [7, 30, 90]

export default function Stats() {
  const [days, setDays] = useState(30)
  const [data, setData] = useState(null)
  const [achievements, setAchievements] = useState([])
  const [leaderboard, setLeaderboard] = useState([])

  useEffect(() => {
    api.stats(days).then(setData)
  }, [days])

  useEffect(() => {
    api.achievements().then((result) => setAchievements(result.earned))
    api.leaderboard().then((result) => setLeaderboard(result.leaderboard))
  }, [])

  if (!data) return <p className="text-slate-400">Cargando estadísticas…</p>

  const { overview, daily, tags, hours } = data

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        {RANGES.map((range) => (
          <button
            key={range}
            onClick={() => setDays(range)}
            className={`rounded-lg px-3 py-1.5 text-sm ${
              days === range ? 'bg-sky-500 text-slate-950' : 'border border-white/10 text-slate-300'
            }`}
          >
            {range} días
          </button>
        ))}
      </div>

      <section className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatCard label="Minutos totales" value={overview.total_minutes} />
        <StatCard label="Sesiones" value={overview.total_sessions} accent="text-emerald-400" />
        <StatCard label="Media por sesión" value={`${overview.average_minutes} min`} accent="text-amber-400" />
        <StatCard
          label="Tasa de finalización"
          value={`${Math.round(overview.completion_rate * 100)}%`}
          hint={`Racha máxima: ${overview.longest_streak} días`}
          accent="text-fuchsia-400"
        />
      </section>

      <section className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-300">Minutos de foco por día</h2>
        <BarChart
          data={daily}
          labelKey="date"
          valueKey="minutes"
          formatLabel={(value) => value.slice(5)}
        />
      </section>

      <section className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-300">Tus mejores horas</h2>
        <BarChart data={hours} labelKey="hour" valueKey="minutes" formatLabel={(hour) => `${hour}:00`} />
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        <section className="card">
          <h2 className="mb-3 text-sm font-semibold text-slate-300">Reparto por etiqueta</h2>
          {tags.length === 0 ? (
            <p className="text-sm text-slate-500">Aún no has etiquetado sesiones.</p>
          ) : (
            <ul className="space-y-2">
              {tags.map((item) => (
                <li key={item.tag} className="flex items-center justify-between text-sm">
                  <span className="text-slate-300">{item.tag}</span>
                  <span className="font-semibold">{item.minutes} min</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <h2 className="mb-3 text-sm font-semibold text-slate-300">Logros</h2>
          {achievements.length === 0 ? (
            <p className="text-sm text-slate-500">Completa sesiones para desbloquear logros.</p>
          ) : (
            <ul className="space-y-2">
              {achievements.map((item) => (
                <li key={item.id} className="flex items-center gap-3 text-sm">
                  <span className="text-xl">{item.achievement.icon}</span>
                  <div>
                    <p className="font-medium">{item.achievement.name}</p>
                    <p className="text-xs text-slate-500">{item.achievement.description}</p>
                  </div>
                  <span className="ml-auto text-xs text-emerald-400">+{item.points_awarded}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <section className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-300">Clasificación global</h2>
        <ol className="space-y-2">
          {leaderboard.map((row) => (
            <li
              key={row.rank}
              className={`flex items-center gap-3 rounded-lg px-2 py-1.5 text-sm ${
                row.is_me ? 'bg-sky-400/10 text-sky-200' : ''
              }`}
            >
              <span className="w-6 text-slate-500">{row.rank}</span>
              <span>{row.avatar_emoji}</span>
              <span className="font-medium">{row.username}</span>
              <span className="ml-auto text-slate-400">{row.points} pts</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  )
}
