import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import BotConfigs from './pages/BotConfigs'
import Orders from './pages/Orders'
import Monitoring from './pages/Monitoring'
import Trading from './pages/Trading'
import ActivityLogs from './pages/ActivityLogs'
import Layout from './components/Layout'
import { AuthProvider, useAuth } from './context/AuthContext'
import './App.css'

function ProtectedRoute({ children }) {
  const auth = useAuth()
  const token = auth?.token
  return token ? children : <Navigate to="/login" />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="configs" element={<BotConfigs />} />
        <Route path="orders" element={<Orders />} />
        <Route path="trading" element={<Trading />} />
        <Route path="monitoring" element={<Monitoring />} />
        <Route path="activity-logs" element={<ActivityLogs />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  )
}

export default App

