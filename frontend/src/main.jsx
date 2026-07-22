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
import Dashboard from './pages/Dashboard'
import Preferences from './pages/Preferences'
import History from './pages/History'
import Live from './pages/Live'
import Servers from './pages/Servers'
import ProtectedRoute from './components/ProtectedRoute'


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
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/servers" element={<ProtectedRoute><Servers /></ProtectedRoute>} />
              <Route path="/preferences" element={<ProtectedRoute><Preferences /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
              <Route path="/live" element={<ProtectedRoute><Live /></ProtectedRoute>} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </SearchProvider>
    </ErrorBoundary>
  </React.StrictMode>
)
