import { Outlet } from 'react-router-dom'
import Navbar from './Navbar.jsx'

export default function Layout() {
  return (
    <div className="min-h-screen bg-navy-900 bg-grid-slate bg-[length:60px_60px]">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-cyan-400/10 pointer-events-none" />
      <Navbar />
      <main className="relative mx-auto max-w-6xl px-4 py-8 sm:px-6 z-10">
        <Outlet />
      </main>
    </div>
  )
}

