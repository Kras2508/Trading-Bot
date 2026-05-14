import React, { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function Orders() {
  const { token } = useAuth()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const toastTimeoutRef = useRef(null)
  const [refreshingPnL, setRefreshingPnL] = useState({}) // Track which order is refreshing
  const [showEditModal, setShowEditModal] = useState(false)
  const [editFormData, setEditFormData] = useState(null)
  const [editErrors, setEditErrors] = useState({})
  const [editSubmitting, setEditSubmitting] = useState(false)
  const [view, setView] = useState('all')
  const [filter, setFilter] = useState({
    side: ''
  })

  useEffect(() => {
    if (token) {
      fetchOrders()
    }
  }, [token, view, filter.side])

  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current)
      }
    }
  }, [])

  const fetchOrders = async () => {
    setLoading(true)
    setError(null)
    try {
      const isCompletedView = view === 'completed'
      const endpoint = isCompletedView
        ? '/api/orders/completed'
        : '/api/orders/history'
      
      const params = {}
      if (!isCompletedView && view !== 'all') params.status = view
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

  const showToast = (type, text) => {
    setToast({ type, text })
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current)
    }
    toastTimeoutRef.current = setTimeout(() => {
      setToast(null)
    }, 3000)
  }

  const getEditEligibility = (order) => {
    const orderType = (order.order_type || 'market').toLowerCase()
    if (order.status === 'pending' && orderType === 'limit') {
      return { allowed: true, reason: '' }
    }

    if (order.status === 'pending') {
      return { allowed: false, reason: 'Chỉ lệnh pending limit mới được chỉnh sửa' }
    }

    if (order.status === 'filled' || order.status === 'closed') {
      return { allowed: false, reason: 'Lệnh đã khớp/đóng, không thể sửa dữ liệu khớp' }
    }

    if (order.status === 'cancelled') {
      return { allowed: false, reason: 'Lệnh đã hủy, không thể sửa' }
    }

    if (order.status === 'error') {
      return { allowed: false, reason: 'Lệnh lỗi, không thể sửa' }
    }

    return { allowed: false, reason: 'Lệnh không thể sửa trong trạng thái hiện tại' }
  }

  const validateEditForm = (data) => {
    const errors = {}

    const amount = Number(data.amount)
    if (!Number.isFinite(amount) || amount <= 0) {
      errors.amount = 'Amount phải lớn hơn 0'
    }

    const price = Number(data.price)
    if (!Number.isFinite(price) || price <= 0) {
      errors.price = 'Price phải lớn hơn 0'
    }

    if (data.stop_loss_price !== '' && data.stop_loss_price !== null) {
      const stopLoss = Number(data.stop_loss_price)
      if (!Number.isFinite(stopLoss) || stopLoss < 0) {
        errors.stop_loss_price = 'Stop loss phải >= 0'
      }
    }

    if (data.take_profit_price !== '' && data.take_profit_price !== null) {
      const takeProfit = Number(data.take_profit_price)
      if (!Number.isFinite(takeProfit) || takeProfit < 0) {
        errors.take_profit_price = 'Take profit phải >= 0'
      }
    }

    return {
      errors,
      isValid: Object.keys(errors).length === 0
    }
  }

  const openEditModal = (order) => {
    const eligibility = getEditEligibility(order)
    if (!eligibility.allowed) {
      showToast('warning', eligibility.reason)
      return
    }

    setEditErrors({})
    setEditFormData({
      id: order.id,
      symbol: order.symbol,
      order_type: order.order_type || 'market',
      status: order.status,
      amount: order.amount ?? '',
      price: order.price ?? '',
      stop_loss_price: order.stop_loss_price ?? '',
      take_profit_price: order.take_profit_price ?? ''
    })
    setShowEditModal(true)
  }

  const closeEditModal = () => {
    if (editSubmitting) {
      return
    }
    setShowEditModal(false)
    setEditFormData(null)
    setEditErrors({})
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    if (!editFormData) {
      return
    }

    const { errors, isValid } = validateEditForm(editFormData)
    if (!isValid) {
      setEditErrors(errors)
      return
    }

    setEditSubmitting(true)
    setEditErrors({})
    try {
      const payload = {
        amount: Number(editFormData.amount),
        price: Number(editFormData.price),
        stop_loss_price: editFormData.stop_loss_price === '' ? null : Number(editFormData.stop_loss_price),
        take_profit_price: editFormData.take_profit_price === '' ? null : Number(editFormData.take_profit_price)
      }

      await axios.patch(`/api/orders/${editFormData.id}`, payload, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      showToast('success', 'Cập nhật lệnh thành công.')
      closeEditModal()
      fetchOrders()
    } catch (error) {
      const message = error.response?.data?.detail || 'Cập nhật lệnh thất bại'
      showToast('danger', message)
    } finally {
      setEditSubmitting(false)
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

  const viewLabels = {
    all: 'Tất cả',
    pending: 'Đang chờ',
    filled: 'Đã khớp',
    closed: 'Đã đóng',
    cancelled: 'Đã hủy',
    error: 'Lỗi',
    completed: 'Hoàn thành'
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
      {toast && (
        <div className="position-fixed top-0 end-0 p-3" style={{ zIndex: 1080 }}>
          <div className={`alert alert-${toast.type} shadow-sm mb-0`} role="alert">
            {toast.text}
          </div>
        </div>
      )}
      <h2 className="mb-4">Lịch Sử Lệnh</h2>

      <div className="mb-3">
        <ul className="nav nav-pills flex-wrap gap-2">
          {['all', 'pending', 'filled', 'closed', 'cancelled', 'error', 'completed'].map((tab) => (
            <li className="nav-item" key={tab}>
              <button
                className={`nav-link ${view === tab ? 'active' : ''}`}
                type="button"
                onClick={() => setView(tab)}
              >
                {viewLabels[tab]}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Filters */}
      <div className="card mb-3">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-4">
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
            <div className="col-md-4 d-flex align-items-end">
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
                {view === 'completed'
                  ? 'Chưa có lệnh nào đã hoàn thành'
                  : `Chưa có lệnh nào (${viewLabels[view]})`}
              </p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Bot</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Amount</th>
                    <th>Type</th>
                    <th>Filled Price</th>
                    <th>Stop Loss</th>
                    <th>Take Profit</th>
                    <th>PnL</th>
                    <th>Actions</th>
                    <th>Created</th>
                    <th>Closed</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id}>
                      <td>{order.id}</td>
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
                        <div className="fw-semibold" title={`Bot Config ID: ${order.bot_config_id}`}>
                          {order.bot_config_name || `Bot #${order.bot_config_id}`}
                        </div>
                      </td>
                      <td><strong>{order.symbol}</strong></td>
                      <td>
                        <span className={`badge ${order.side === 'buy' ? 'bg-success' : 'bg-danger'}`}>
                          {order.side.toUpperCase()}
                        </span>
                      </td>
                      <td>{order.amount ? parseFloat(order.amount).toFixed(4) : '-'}</td>
                      <td>
                        <small className="text-muted">{order.order_type || 'market'}</small>
                      </td>
                      <td>
                        {order.filled_price 
                          ? <strong>{parseFloat(order.filled_price || 0).toFixed(2)}</strong>
                          : order.price 
                            ? <span className="text-muted">Limit: {parseFloat(order.price || 0).toFixed(2)}</span>
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
                        <div className="d-flex flex-column gap-1">
                          {(() => {
                            const eligibility = getEditEligibility(order)
                            if (eligibility.allowed) {
                              return (
                                <button
                                  className="btn btn-sm btn-outline-primary"
                                  onClick={() => openEditModal(order)}
                                >
                                  Sửa
                                </button>
                              )
                            }

                            return (
                              <button
                                className="btn btn-sm btn-outline-secondary"
                                onClick={() => showToast('warning', eligibility.reason)}
                              >
                                Không thể sửa
                              </button>
                            )
                          })()}

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
                        </div>
                      </td>
                      <td>
                        <small>{formatDateTime(order.created_at)}</small>
                      </td>
                      <td>
                        <small>{formatDateTime(order.closed_at)}</small>
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
            Hiển thị {orders.length} lệnh ({viewLabels[view]})
          </small>
        </div>
      )}

      {showEditModal && editFormData && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Chỉnh sửa lệnh #{editFormData.id}</h5>
                <button className="btn-close" onClick={closeEditModal}></button>
              </div>
              <form onSubmit={handleUpdate}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Symbol</label>
                    <input
                      type="text"
                      className="form-control"
                      value={editFormData.symbol}
                      disabled
                    />
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Order Type</label>
                        <input
                          type="text"
                          className="form-control"
                          value={editFormData.order_type}
                          disabled
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Status</label>
                        <input
                          type="text"
                          className="form-control"
                          value={editFormData.status}
                          disabled
                        />
                      </div>
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Amount</label>
                        <input
                          type="number"
                          className={`form-control ${editErrors.amount ? 'is-invalid' : ''}`}
                          value={editFormData.amount}
                          onChange={(e) => setEditFormData({ ...editFormData, amount: e.target.value })}
                          step="0.0001"
                        />
                        {editErrors.amount && <div className="invalid-feedback">{editErrors.amount}</div>}
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Price</label>
                        <input
                          type="number"
                          className={`form-control ${editErrors.price ? 'is-invalid' : ''}`}
                          value={editFormData.price}
                          onChange={(e) => setEditFormData({ ...editFormData, price: e.target.value })}
                          step="0.01"
                        />
                        {editErrors.price && <div className="invalid-feedback">{editErrors.price}</div>}
                      </div>
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Stop Loss</label>
                        <input
                          type="number"
                          className={`form-control ${editErrors.stop_loss_price ? 'is-invalid' : ''}`}
                          value={editFormData.stop_loss_price}
                          onChange={(e) => setEditFormData({ ...editFormData, stop_loss_price: e.target.value })}
                          step="0.01"
                          placeholder="Để trống nếu không dùng"
                        />
                        {editErrors.stop_loss_price && (
                          <div className="invalid-feedback">{editErrors.stop_loss_price}</div>
                        )}
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Take Profit</label>
                        <input
                          type="number"
                          className={`form-control ${editErrors.take_profit_price ? 'is-invalid' : ''}`}
                          value={editFormData.take_profit_price}
                          onChange={(e) => setEditFormData({ ...editFormData, take_profit_price: e.target.value })}
                          step="0.01"
                          placeholder="Để trống nếu không dùng"
                        />
                        {editErrors.take_profit_price && (
                          <div className="invalid-feedback">{editErrors.take_profit_price}</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeEditModal} disabled={editSubmitting}>
                    Hủy
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={editSubmitting}>
                    {editSubmitting ? 'Đang lưu...' : 'Lưu thay đổi'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

