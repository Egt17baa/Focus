import { BarChart3, LogOut, Settings as SettingsIcon, Shield, Target, Trophy } from 'lucide-react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext.jsx'

const NAV = [
  { to: '/', label: 'Enfoque', icon: Target },
  { to: '/stats', label: 'Progreso', icon: BarChart3 },
  { to: '/challenges', label: 'Retos', icon: Trophy },
  { to: '/apps', label: 'Apps', icon: Shield },
  { to: '/settings', label: 'Ajustes', icon: SettingsIcon },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen pb-20 md:pb-0">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/70 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-3">
          <span className="text-lg font-black tracking-tight">
            Focus<span className="text-sky-400">.</span>
          </span>
          <nav className="ml-4 hidden gap-1 md:flex">
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                    isActive ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-slate-200'
                  }`
                }
              >
                <Icon size={16} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-semibold leading-tight">
                {user.avatar_emoji} {user.username}
              </p>
              <p className="text-xs text-slate-400">
                {user.level_name} · {user.total_focus_points} pts
              </p>
            </div>
            <button onClick={handleLogout} className="btn-ghost px-2.5 py-2" aria-label="Cerrar sesión">
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-6">
        <Outlet />
      </main>

      <nav className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-5 border-t border-white/10 bg-slate-950/90 backdrop-blur md:hidden">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 py-2.5 text-[11px] ${
                isActive ? 'text-sky-400' : 'text-slate-400'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
