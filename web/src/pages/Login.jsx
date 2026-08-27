import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await login(form)
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
          <h1 className="text-2xl font-black">
            Focus<span className="text-sky-400">.</span>
          </h1>
          <p className="text-sm text-slate-400">Recupera tu atención, sesión a sesión.</p>
        </div>

        <div>
          <label className="label" htmlFor="username">
            Usuario o email
          </label>
          <input
            id="username"
            className="input"
            autoComplete="username"
            value={form.username}
            onChange={(event) => setForm({ ...form, username: event.target.value })}
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
            autoComplete="current-password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            required
          />
        </div>

        {error ? <p className="text-sm text-rose-400">{error}</p> : null}

        <button className="btn-primary w-full" disabled={loading}>
          {loading ? 'Entrando…' : 'Entrar'}
        </button>
        <p className="text-center text-sm text-slate-400">
          ¿Sin cuenta?{' '}
          <Link to="/register" className="text-sky-400 hover:underline">
            Crear una
          </Link>
        </p>
      </form>
    </div>
  )
}
