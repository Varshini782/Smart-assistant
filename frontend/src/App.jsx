import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'
import Results from './pages/Results.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Practice from './pages/Practice.jsx'
import Learning from './pages/Learning.jsx'

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="results" element={<Results />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="practice" element={<Practice />} />
          <Route path="learning" element={<Learning />} />
        </Route>
      </Routes>
      <Toaster
        toastOptions={{
          className: 'dark:bg-slate-800 dark:text-slate-100',
          style: {
            borderRadius: '12px',
          },
        }}
      />
    </>
  )
}
