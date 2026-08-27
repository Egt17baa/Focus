import { Navigate, Route, Routes } from 'react-router-dom'

import Layout from './components/Layout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Apps from './pages/Apps.jsx'
import Challenges from './pages/Challenges.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Settings from './pages/Settings.jsx'
import Stats from './pages/Stats.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/stats" element={<Stats />} />
        <Route path="/challenges" element={<Challenges />} />
        <Route path="/apps" element={<Apps />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
