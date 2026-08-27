import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    if (form.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      return
    }
    setLoading(true)
    setError(null)
    try {
      await register(form)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid min-h-screen place-items-center px-4">
      <form onSubmit={submit} className="card w-full max-w-sm space-y-4">
        <div>
          <h1 className="text-2xl font-black">Crea tu cuenta</h1>
          <p className="text-sm text-slate-400">Empieza tu primera sesión de enfoque hoy.</p>
        </div>

        <div>
          <label className="label" htmlFor="username">
            Usuario
          </label>
          <input
            id="username"
            className="input"
            value={form.username}
            onChange={(event) => setForm({ ...form, username: event.target.value })}
            required
            minLength={3}
          />
        </div>

        <div>
          <label className="label" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            className="input"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            required
          />
        </div>

        <div>
          <label className="label" htmlFor="password">
            Contraseña
          </label>
          <input
            id="password"
            type="password"
            className="input"
            autoComplete="new-password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            required
            minLength={8}
          />
        </div>

        {error ? <p className="text-sm text-rose-400">{error}</p> : null}

        <button className="btn-primary w-full" disabled={loading}>
          {loading ? 'Creando…' : 'Crear cuenta'}
        </button>
        <p className="text-center text-sm text-slate-400">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-sky-400 hover:underline">
            Entrar
          </Link>
        </p>
      </form>
    </div>
  )
}
