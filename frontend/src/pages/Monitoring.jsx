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

  return (
    <div>
      <h2 className="mb-4">Monitoring</h2>
      <div className="row">
        {statuses.map((status) => (
          <div key={status.bot_config_id} className="col-md-6 mb-3">
            <div className="card">
              <div className="card-header">
                Bot Config ID: {status.bot_config_id}
              </div>
              <div className="card-body">
                <div className="mb-2">
                  <strong>Status:</strong>{' '}
                  <span className={`badge ${status.is_running ? 'bg-success' : 'bg-secondary'}`}>
                    {status.is_running ? 'Running' : 'Stopped'}
                  </span>
                  {status.is_paused && (
                    <span className="badge bg-warning ms-2">Paused</span>
                  )}
                </div>
                <div className="mb-2">
                  <strong>Total Orders:</strong> {status.total_orders}
                </div>
                <div className="mb-2">
                  <strong>Successful:</strong> {status.successful_orders}
                </div>
                <div className="mb-2">
                  <strong>Failed:</strong> {status.failed_orders}
                </div>
                <div className="mb-2">
                  <strong>Total PnL:</strong>{' '}
                  <span className={status.total_pnl >= 0 ? 'text-success' : 'text-danger'}>
                    {status.total_pnl.toFixed(2)}
                  </span>
                </div>
                <div className="mb-2">
                  <strong>Health:</strong>{' '}
                  <span className={`badge ${
                    status.health_status === 'healthy' ? 'bg-success' :
                    status.health_status === 'warning' ? 'bg-warning' : 'bg-danger'
                  }`}>
                    {status.health_status}
                  </span>
                </div>
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
        ))}
      </div>
    </div>
  )
}

