import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function Orders() {
  const { token } = useAuth()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshingPnL, setRefreshingPnL] = useState({}) // Track which order is refreshing
  const [filter, setFilter] = useState({
    status: '',
    side: '',
    showCompletedOnly: false
  })

  useEffect(() => {
    if (token) {
      fetchOrders()
    }
  }, [token, filter.showCompletedOnly])

  const fetchOrders = async () => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = filter.showCompletedOnly 
        ? '/api/orders/completed' 
        : '/api/orders/history'
      
      const params = {}
      if (filter.status) params.status = filter.status
      if (filter.side) params.side = filter.side
      
      const response = await axios.get(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: params
      })
      setOrders(response.data || [])
    } catch (error) {
      console.error('Failed to fetch orders:', error)
      
      // Ensure error message is always a string
      let errorMessage = 'Không thể tải danh sách lệnh'
      
      if (error.response?.status === 403 || error.response?.status === 401) {
        errorMessage = 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
      } else if (error.response?.data) {
        const detail = error.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          // FastAPI validation errors
          errorMessage = detail.map(err => {
            if (typeof err === 'string') return err
            if (err.msg) return err.msg
            return JSON.stringify(err)
          }).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = JSON.stringify(detail)
        } else {
          errorMessage = String(detail)
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      filled: 'bg-success',
      pending: 'bg-warning',
      cancelled: 'bg-secondary',
      closed: 'bg-info',
      error: 'bg-danger'
    }
    return badges[status] || 'bg-secondary'
  }

  const getStatusText = (status) => {
    const texts = {
      filled: 'Đã khớp',
      pending: 'Đang chờ',
      cancelled: 'Đã hủy',
      closed: 'Đã đóng',
      error: 'Lỗi'
    }
    return texts[status] || status
  }

  const getStatusTooltip = (status) => {
    const tooltips = {
      filled: 'Lệnh đã khớp trên sàn, position đang mở',
      pending: 'Lệnh đang chờ khớp',
      cancelled: 'Lệnh đã bị hủy',
      closed: 'Position đã được đóng hoàn toàn',
      error: 'Lệnh bị lỗi'
    }
    return tooltips[status] || ''
  }

  const formatDateTime = (dateString) => {
    if (!dateString) return '-'

    try {
      // Parse ISO string từ backend (UTC)
      const date = new Date(dateString)

      // Nếu invalid thì trả thẳng về chuỗi gốc
      if (isNaN(date.getTime())) {
        return dateString
      }

      // Hiển thị THEO UTC (không auto +7 theo giờ máy)
      const day = String(date.getUTCDate()).padStart(2, '0')
      const month = String(date.getUTCMonth() + 1).padStart(2, '0')
      const year = date.getUTCFullYear()
      const hours = String(date.getUTCHours()).padStart(2, '0')
      const minutes = String(date.getUTCMinutes()).padStart(2, '0')
      const seconds = String(date.getUTCSeconds()).padStart(2, '0')

      return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`
    } catch (e) {
      console.error('Error formatting date:', e, dateString)
      return dateString
    }
  }

  const refreshPnL = async (orderId) => {
    setRefreshingPnL({ ...refreshingPnL, [orderId]: true })
    try {
      const response = await axios.post(`/api/trading/refresh-pnl/${orderId}`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      // Update order in list
      setOrders(orders.map(order => 
        order.id === orderId 
          ? { ...order, pnl: response.data.pnl, pnl_percent: response.data.pnl_percent }
          : order
      ))
      
      // Show success message
      setError(null)
      alert(`Đã cập nhật PnL: ${response.data.pnl > 0 ? '+' : ''}${parseFloat(response.data.pnl).toFixed(2)} (${response.data.pnl_percent > 0 ? '+' : ''}${parseFloat(response.data.pnl_percent).toFixed(2)}%)`)
    } catch (error) {
      console.error('Failed to refresh PnL:', error)
      const errorMessage = error.response?.data?.detail || 'Không thể lấy PnL từ sàn'
      setError(errorMessage)
    } finally {
      setRefreshingPnL({ ...refreshingPnL, [orderId]: false })
    }
  }

  return (
    <div>
      <h2 className="mb-4">Lịch Sử Lệnh</h2>

      {/* Filters */}
      <div className="card mb-3">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-3">
              <label className="form-label">Lọc theo trạng thái</label>
              <select
                className="form-select"
                value={filter.status}
                onChange={(e) => {
                  setFilter({ ...filter, status: e.target.value })
                }}
              >
                <option value="">Tất cả</option>
                <option value="filled">Đã khớp</option>
                <option value="closed">Đã đóng</option>
                <option value="pending">Đang chờ</option>
                <option value="cancelled">Đã hủy</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Lọc theo hướng</label>
              <select
                className="form-select"
                value={filter.side}
                onChange={(e) => {
                  setFilter({ ...filter, side: e.target.value })
                }}
              >
                <option value="">Tất cả</option>
                <option value="buy">Mua (Buy)</option>
                <option value="sell">Bán (Sell)</option>
              </select>
            </div>
            <div className="col-md-3 d-flex align-items-end">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="showCompletedOnly"
                  checked={filter.showCompletedOnly}
                  onChange={(e) => {
                    setFilter({ ...filter, showCompletedOnly: e.target.checked })
                  }}
                />
                <label className="form-check-label" htmlFor="showCompletedOnly">
                  Chỉ hiển thị lệnh đã hoàn thành
                </label>
              </div>
            </div>
            <div className="col-md-3 d-flex align-items-end">
              <button
                className="btn btn-primary w-100"
                onClick={fetchOrders}
                disabled={loading}
                title="Tải lại danh sách lệnh từ database"
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                    Đang tải...
                  </>
                ) : (
                  <>🔄 Tải lại danh sách</>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          {error}
          <button
            type="button"
            className="btn-close"
            onClick={() => setError(null)}
          ></button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Đang tải...</span>
          </div>
          <p className="mt-2">Đang tải danh sách lệnh...</p>
        </div>
      )}

      {/* Orders Table */}
      {!loading && (
        <div className="card">
          {orders.length === 0 ? (
            <div className="card-body text-center py-5">
              <p className="text-muted mb-0">
                {filter.showCompletedOnly 
                  ? 'Chưa có lệnh nào đã hoàn thành' 
                  : 'Chưa có lệnh nào'}
              </p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Bot Config</th>
                    <th>Symbol</th>
                    <th>Mode</th>
                    <th>Side</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Entry Price</th>
                    <th>Stop Loss</th>
                    <th>Take Profit</th>
                    <th>Status</th>
                    <th>PnL</th>
                    <th>ROI</th>
                    <th>Actions</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id}>
                      <td>{order.id}</td>
                      <td>
                        <small className="text-muted" title={`Bot Config ID: ${order.bot_config_id}`}>
                          {order.bot_config_name || `Bot #${order.bot_config_id}`}
                        </small>
                      </td>
                      <td><strong>{order.symbol}</strong></td>
                      <td>
                        <span className={`badge ${order.trading_mode === 'futures' ? 'bg-warning text-dark' : 'bg-info'}`}>
                          {order.trading_mode === 'futures' ? 'Futures' : 'Spot'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${order.side === 'buy' ? 'bg-success' : 'bg-danger'}`}>
                          {order.side.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <small className="text-muted">{order.order_type || 'market'}</small>
                      </td>
                      <td>{order.amount ? parseFloat(order.amount).toFixed(4) : '-'}</td>
                      <td>
                        {order.filled_price 
                          ? <strong>{parseFloat(order.filled_price || 0).toFixed(2)}</strong>
                          : order.price 
                            ? <span className="text-muted">{parseFloat(order.price || 0).toFixed(2)}</span>
                            : '-'
                        }
                      </td>
                      <td>
                        {order.stop_loss_price && !isNaN(parseFloat(order.stop_loss_price)) ? (
                          <span className="text-danger">🛑 {parseFloat(order.stop_loss_price).toFixed(2)}</span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        {order.take_profit_price && !isNaN(parseFloat(order.take_profit_price)) ? (
                          <span className="text-success">🎯 {parseFloat(order.take_profit_price).toFixed(2)}</span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        <span 
                          className={`badge ${getStatusBadge(order.status)}`}
                          title={getStatusTooltip(order.status)}
                          style={{ cursor: 'help' }}
                        >
                          {getStatusText(order.status)}
                        </span>
                      </td>
                      <td>
                        {/* PnL: Số tiền (USDT) */}
                        {order.pnl !== undefined && order.pnl !== null && !isNaN(parseFloat(order.pnl)) && order.pnl !== 0 ? (
                          <span className={order.pnl > 0 ? 'text-success fw-bold' : 'text-danger fw-bold'}>
                            {order.pnl > 0 ? '+' : ''}{parseFloat(order.pnl).toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        {/* ROI: Phần trăm (%) */}
                        {order.pnl_percent !== undefined && order.pnl_percent !== null && !isNaN(parseFloat(order.pnl_percent)) && order.pnl_percent !== 0 ? (
                          <span className={order.pnl_percent > 0 ? 'text-success fw-bold' : 'text-danger fw-bold'}>
                            {order.pnl_percent > 0 ? '+' : ''}{parseFloat(order.pnl_percent).toFixed(2)}%
                          </span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        {/* Chỉ hiển thị nút Refresh PnL cho:
                            - Lệnh đang mở (filled) - để xem unrealized PnL
                            - Lệnh đã đóng nhưng chưa có PnL */}
                        {(order.status === 'filled' || (order.status === 'closed' && (!order.pnl || order.pnl === 0))) ? (
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => refreshPnL(order.id)}
                            disabled={refreshingPnL[order.id]}
                            title={order.status === 'filled' ? 'Lấy unrealized PnL từ sàn' : 'Lấy lại PnL từ sàn'}
                          >
                            {refreshingPnL[order.id] ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                                Đang lấy...
                              </>
                            ) : (
                              <>🔄 Refresh PnL</>
                            )}
                          </button>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        <small>{formatDateTime(order.created_at)}</small>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Summary */}
      {!loading && orders.length > 0 && (
        <div className="mt-3">
          <small className="text-muted">
            Hiển thị {orders.length} lệnh
            {filter.showCompletedOnly && ' (chỉ lệnh đã hoàn thành)'}
          </small>
        </div>
      )}
    </div>
  )
}

