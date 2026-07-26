import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SearchProvider } from './contexts/SearchContext'
import ErrorBoundary from "./components/ErrorBoundary";
import './index.css'

import ScrollReset from './components/ScrollReset'
import Home from './pages/Home'
import Features from './pages/Features'
import Commands from './pages/Commands'
import Support from './pages/Support'
import Callback from './pages/Callback'
import { DashboardContent } from './pages/Dashboard'
import { PreferencesContent } from './pages/Preferences'
import { HistoryContent } from './pages/History'
import { LiveContent } from './pages/Live'
import { ServersContent } from './pages/Servers'
import ProtectedRoute from './components/ProtectedRoute'
import AppShell from './components/AppShell'


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
        <SearchProvider>
          <BrowserRouter>
            <ScrollReset />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/features" element={<Features />} />
              <Route path="/commands" element={<Commands />} />
              <Route path="/support" element={<Support />} />
              <Route path="/callback" element={<Callback />} />
              <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
                <Route path="/dashboard" element={<DashboardContent />} />
                <Route path="/servers" element={<ServersContent />} />
                <Route path="/preferences" element={<PreferencesContent />} />
                <Route path="/history" element={<HistoryContent />} />
                <Route path="/live" element={<LiveContent />} />
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </SearchProvider>
    </ErrorBoundary>
  </React.StrictMode>
)