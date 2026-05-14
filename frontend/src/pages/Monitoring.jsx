import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function Monitoring() {
  const { token } = useAuth()
  const [statuses, setStatuses] = useState([])

  useEffect(() => {
    if (token) {
      fetchStatuses()
      const interval = setInterval(fetchStatuses, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    }
  }, [token])

  const fetchStatuses = async () => {
    try {
      const response = await axios.get('/api/monitoring/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setStatuses(response.data)
    } catch (error) {
      console.error('Failed to fetch statuses:', error)
      if (error.response?.status === 403 || error.response?.status === 401) {
        alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.')
      }
    }
  }

  const handlePause = async (botConfigId) => {
    try {
      await axios.post(`/api/monitoring/status/${botConfigId}/pause`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      fetchStatuses()
    } catch (error) {
      alert('Lỗi: ' + (error.response?.data?.detail || 'Pause thất bại'))
    }
  }

  const handleResume = async (botConfigId) => {
    try {
      await axios.post(`/api/monitoring/status/${botConfigId}/resume`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      fetchStatuses()
    } catch (error) {
      alert('Lỗi: ' + (error.response?.data?.detail || 'Resume thất bại'))
    }
  }

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'Running':
        return 'bg-success'
      case 'Paused':
        return 'bg-warning'
      case 'Stopped':
        return 'bg-secondary'
      case 'Error':
        return 'bg-danger'
      case 'Idle':
        return 'bg-info'
      case 'Completed':
        return 'bg-dark'
      default:
        return 'bg-secondary'
    }
  }

  const getHealthBadgeColor = (health) => {
    switch (health) {
      case 'healthy':
        return 'bg-success'
      case 'warning':
        return 'bg-warning'
      case 'error':
        return 'bg-danger'
      case 'offline':
        return 'bg-dark'
      default:
        return 'bg-secondary'
    }
  }

  return (
    <div>
      <h2 className="mb-4">Monitoring</h2>
      {statuses.length === 0 ? (
        <div className="alert alert-info">Không có bot nào. Vui lòng tạo bot mới.</div>
      ) : (
        <div className="row">
          {statuses.map((status) => {
            // Fallback values in case fields are missing
            const displayName = status.display_name || `Bot ID: ${status.bot_config_id}`
            const botStatus = status.status || (status.is_paused ? 'Paused' : status.is_running ? 'Running' : 'Stopped')
            const symbol = status.symbol || 'N/A'
            const exchange = status.exchange || 'N/A'
            
            return (
              <div key={status.bot_config_id} className="col-md-6 mb-3">
                <div className="card">
                  <div className="card-header">
                    <h5>{displayName}</h5>
                  </div>
                  <div className="card-body">
                    <div className="mb-2">
                      <strong>Status:</strong>{' '}
                      <span className={`badge ${getStatusBadgeColor(botStatus)}`}>
                        {botStatus}
                      </span>
                    </div>
                    <div className="mb-2">
                      <strong>Mode:</strong> {status.trading_mode === 'futures' ? `Futures (${status.leverage}x)` : 'Spot'}
                    </div>
                    <div className="mb-2">
                      <strong>Symbol:</strong> {symbol} @ {exchange}
                    </div>
                    <div className="mb-2">
                      <strong>Total Orders:</strong> {status.total_orders || 0}
                    </div>
                    <div className="mb-2">
                      <strong>Successful:</strong> {status.successful_orders || 0} / <strong>Failed:</strong> {status.failed_orders || 0}
                    </div>
                    <div className="mb-2">
                      <strong>Total PnL:</strong>{' '}
                      <span className={status.total_pnl >= 0 ? 'text-success' : 'text-danger'}>
                        {(status.total_pnl || 0).toFixed(2)}
                      </span>
                    </div>
                    <div className="mb-2">
                      <strong>Health:</strong>{' '}
                      <span className={`badge ${getHealthBadgeColor(status.health_status)}`}>
                        {status.health_status || 'unknown'}
                      </span>
                    </div>
                    {status.last_heartbeat && (
                      <div className="mb-2" style={{fontSize: '0.85em'}}>
                        <strong>Last Heartbeat:</strong> {new Date(status.last_heartbeat).toLocaleString()}
                      </div>
                    )}
                    {status.last_updated && (
                      <div className="mb-2" style={{fontSize: '0.85em'}}>
                        <strong>Status Updated:</strong> {new Date(status.last_updated).toLocaleString()}
                      </div>
                    )}
                    {status.last_error && (
                      <div className="mb-2 text-danger" style={{fontSize: '0.85em'}}>
                        <strong>Last Error:</strong> {status.last_error}
                      </div>
                    )}
                    <div className="mt-3">
                      {status.is_paused ? (
                        <button
                          className="btn btn-sm btn-success"
                          onClick={() => handleResume(status.bot_config_id)}
                        >
                          Resume
                        </button>
                      ) : (
                        <button
                          className="btn btn-sm btn-warning"
                          onClick={() => handlePause(status.bot_config_id)}
                        >
                          Pause
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}