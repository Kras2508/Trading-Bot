import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { token } = useAuth()
  const [stats, setStats] = useState({
    totalBots: 0,
    activeBots: 0,
    totalOrders: 0,
    successRate: 0
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const headers = {
        'Authorization': `Bearer ${token}`
      }
      const [configsRes, ordersRes, statusRes] = await Promise.all([
        axios.get('/api/config/', { headers }),
        axios.get('/api/orders/', { headers }),
        axios.get('/api/monitoring/status', { headers })
      ])

      const configs = configsRes.data
      const orders = ordersRes.data
      const statuses = statusRes.data

      const activeBots = statuses.filter(s => s.is_running && !s.is_paused).length
      const successfulOrders = orders.filter(o => o.status === 'filled').length

      setStats({
        totalBots: configs.length,
        activeBots,
        totalOrders: orders.length,
        successRate: orders.length > 0 ? Math.round((successfulOrders / orders.length) * 100) : 0
      })
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  return (
    <div>
      <h2 className="mb-4">Dashboard</h2>
      <div className="row">
        <div className="col-md-3">
          <div className="stat-card">
            <h5>Total Bots</h5>
            <h2>{stats.totalBots}</h2>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h5>Active Bots</h5>
            <h2>{stats.activeBots}</h2>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h5>Total Orders</h5>
            <h2>{stats.totalOrders}</h2>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h5>Success Rate</h5>
            <h2>{stats.successRate}%</h2>
          </div>
        </div>
      </div>
    </div>
  )
}

