import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from './layout/AppLayout'
import AiStrategyPage from './pages/AiStrategyPage'
import DataPreviewPage from './pages/DataPreviewPage'
import EnginePage from './pages/EnginePage'
import SyncSettingsPage from './pages/SyncSettingsPage'
import WhatsappPage from './pages/WhatsappPage'

import './App.css'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Navigate to="/engine" replace />} />
        <Route path="/engine" element={<EnginePage />} />
        <Route path="/data" element={<DataPreviewPage />} />
        <Route path="/ai" element={<AiStrategyPage />} />
        <Route path="/sync" element={<SyncSettingsPage />} />
        <Route path="/whatsapp" element={<WhatsappPage />} />
      </Route>
    </Routes>
  )
}
