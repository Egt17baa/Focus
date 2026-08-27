import { Trash2 } from 'lucide-react'
import { useEffect, useState } from 'react'

import { api } from '../lib/api'

const SUGGESTIONS = [
  { app_name: 'TikTok', package_name: 'com.zhiliaoapp.musically', category: 'redes' },
  { app_name: 'Instagram', package_name: 'com.instagram.android', category: 'redes' },
  { app_name: 'YouTube', package_name: 'com.google.android.youtube', category: 'video' },
  { app_name: 'X', package_name: 'com.twitter.android', category: 'redes' },
]

export default function Apps() {
  const [apps, setApps] = useState([])
  const [form, setForm] = useState({ app_name: '', package_name: '' })
  const [error, setError] = useState(null)

  const load = () => api.blockedApps().then((data) => setApps(data.apps))

  useEffect(() => {
    load()
  }, [])

  const add = async (payload) => {
    setError(null)
    try {
      await api.addBlockedApp(payload)
      setForm({ app_name: '', package_name: '' })
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-bold">Apps que te distraen</h1>
        <p className="text-sm text-slate-400">
          La app Android consulta esta lista para bloquearlas mientras estás en una sesión.
        </p>
      </div>

      <form
        className="card flex flex-col gap-3 md:flex-row"
        onSubmit={(event) => {
          event.preventDefault()
          add(form)
        }}
      >
        <input
          className="input"
          placeholder="Nombre de la app"
          value={form.app_name}
          onChange={(event) => setForm({ ...form, app_name: event.target.value })}
          required
        />
        <input
          className="input"
          placeholder="Paquete Android (com.ejemplo.app)"
          value={form.package_name}
          onChange={(event) => setForm({ ...form, package_name: event.target.value })}
        />
        <button className="btn-primary md:w-40">Añadir</button>
      </form>

      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((suggestion) => (
          <button key={suggestion.app_name} className="btn-ghost py-1.5 text-xs" onClick={() => add(suggestion)}>
            + {suggestion.app_name}
          </button>
        ))}
      </div>

      {error ? <p className="text-sm text-rose-400">{error}</p> : null}

      <ul className="space-y-2">
        {apps.map((app) => (
          <li key={app.id} className="card flex items-center gap-3 py-3">
            <div>
              <p className="font-medium">{app.app_name}</p>
              <p className="text-xs text-slate-500">{app.package_name || 'sin paquete'} · {app.category}</p>
            </div>
            <label className="ml-auto flex items-center gap-2 text-xs text-slate-400">
              <input
                type="checkbox"
                checked={app.is_active}
                onChange={(event) =>
                  api.updateBlockedApp(app.id, { is_active: event.target.checked }).then(load)
                }
              />
              Activa
            </label>
            <button
              className="btn-ghost px-2 py-1.5"
              aria-label={`Eliminar ${app.app_name}`}
              onClick={() => api.deleteBlockedApp(app.id).then(load)}
            >
              <Trash2 size={16} />
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
