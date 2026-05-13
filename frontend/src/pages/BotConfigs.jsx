import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function BotConfigs() {
  const { token } = useAuth()
  const [configs, setConfigs] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editFormData, setEditFormData] = useState(null)
  const [editErrors, setEditErrors] = useState({})
  const [editSubmitting, setEditSubmitting] = useState(false)
  const [flashMessage, setFlashMessage] = useState(null)

  const defaultFormData = {
    name: '',
    symbol: '',
    exchange: 'binance',
    amount: '',
    leverage: 1,
    stop_loss_percent: '',
    take_profit_percent: '',
    trading_mode: 'spot',
    api_key: '',
    api_secret: '',
    ip_whitelist: ''
  }
  const [formData, setFormData] = useState(defaultFormData)

  useEffect(() => {
    fetchConfigs()
  }, [])

  const fetchConfigs = async () => {
    try {
      const response = await axios.get('/api/config/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setConfigs(response.data)
    } catch (error) {
      console.error('Failed to fetch configs:', error)
      if (error.response?.status === 403 || error.response?.status === 401) {
        alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.')
      }
    }
  }

  const resetCreateForm = () => {
    setFormData(defaultFormData)
  }

  const validateEditForm = (data) => {
    const errors = {}
    const symbolPattern = /^[A-Za-z0-9]+(\/[A-Za-z0-9]+)?(\.D)?$/

    if (!data.name?.trim()) {
      errors.name = 'Vui lòng nhập tên bot'
    }

    if (!data.symbol?.trim() || !symbolPattern.test(data.symbol.trim())) {
      errors.symbol = 'Symbol không đúng định dạng'
    }

    if (!data.exchange?.trim()) {
      errors.exchange = 'Vui lòng chọn sàn giao dịch'
    }

    const amount = Number(data.amount)
    if (!Number.isFinite(amount) || amount <= 0) {
      errors.amount = 'Amount phải lớn hơn 0'
    }

    const leverage = Number(data.leverage)
    if (!Number.isInteger(leverage) || leverage < 1 || leverage > 125) {
      errors.leverage = 'Leverage phải trong khoảng 1-125'
    }
    if (data.trading_mode === 'spot' && leverage !== 1) {
      errors.leverage = 'Spot chỉ hỗ trợ leverage = 1'
    }

    const stopLoss = Number(data.stop_loss_percent)
    if (!Number.isFinite(stopLoss) || stopLoss < 0) {
      errors.stop_loss_percent = 'Stop loss phải >= 0'
    }

    const takeProfit = Number(data.take_profit_percent)
    if (!Number.isFinite(takeProfit) || takeProfit < 0) {
      errors.take_profit_percent = 'Take profit phải >= 0'
    }

    let parsedTpLevels = null
    if (data.tp_levels_input && data.tp_levels_input.trim()) {
      try {
        parsedTpLevels = JSON.parse(data.tp_levels_input)
        if (!Array.isArray(parsedTpLevels)) {
          errors.tp_levels_input = 'TP levels phải là mảng JSON'
        } else {
          let totalClose = 0
          parsedTpLevels.forEach((level) => {
            const percent = Number(level.percent)
            const closePercent = Number(level.close_percent)
            if (!Number.isFinite(percent) || percent < 0) {
              errors.tp_levels_input = 'TP percent phải >= 0'
            }
            if (!Number.isFinite(closePercent) || closePercent < 0) {
              errors.tp_levels_input = 'TP close_percent phải >= 0'
            }
            totalClose += Number.isFinite(closePercent) ? closePercent : 0
          })
          if (totalClose > 100) {
            errors.tp_levels_input = 'Tổng close_percent không được vượt 100%'
          }
        }
      } catch (error) {
        errors.tp_levels_input = 'TP levels không đúng JSON'
      }
    }

    if (data.enable_trailing) {
      if (data.trailing_type === 'percent') {
        const trailingPercent = Number(data.trailing_percent)
        if (!Number.isFinite(trailingPercent) || trailingPercent <= 0) {
          errors.trailing_percent = 'Trailing percent phải > 0'
        }
      } else if (data.trailing_type === 'atr') {
        const atrMultiplier = Number(data.trailing_atr_multiplier)
        const atrPeriod = Number(data.trailing_atr_period)
        if (!Number.isFinite(atrMultiplier) || atrMultiplier <= 0) {
          errors.trailing_atr_multiplier = 'ATR multiplier phải > 0'
        }
        if (!Number.isInteger(atrPeriod) || atrPeriod < 1) {
          errors.trailing_atr_period = 'ATR period phải >= 1'
        }
      } else {
        errors.trailing_type = 'Trailing type không hợp lệ'
      }
    }

    return {
      errors,
      isValid: Object.keys(errors).length === 0,
      parsedTpLevels
    }
  }

  const openEditModal = (config) => {
    setEditErrors({})
    setFlashMessage(null)
    setEditFormData({
      id: config.id,
      name: config.name || '',
      symbol: config.symbol || '',
      exchange: config.exchange || 'binance',
      amount: config.amount ?? '',
      leverage: config.leverage ?? 1,
      stop_loss_percent: config.stop_loss_percent ?? '',
      take_profit_percent: config.take_profit_percent ?? '',
      tp_levels_input: JSON.stringify(config.tp_levels || []),
      enable_trailing: !!config.enable_trailing,
      trailing_type: config.trailing_type || 'percent',
      trailing_percent: config.trailing_percent ?? '',
      trailing_atr_multiplier: config.trailing_atr_multiplier ?? '',
      trailing_atr_period: config.trailing_atr_period ?? 14,
      trading_mode: config.trading_mode || 'spot',
      enable_notifications: config.enable_notifications ?? true,
      is_active: config.is_active ?? true,
      api_key: '',
      api_secret: ''
    })
    setShowEditModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/config/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setShowModal(false)
      fetchConfigs()
      resetCreateForm()
    } catch (error) {
      alert('Lỗi: ' + (error.response?.data?.detail || 'Tạo config thất bại'))
    }
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    if (!editFormData) {
      return
    }

    const { errors, isValid, parsedTpLevels } = validateEditForm(editFormData)
    if (!isValid) {
      setEditErrors(errors)
      return
    }

    setEditSubmitting(true)
    setEditErrors({})
    try {
      const payload = {
        name: editFormData.name.trim(),
        symbol: editFormData.symbol.trim(),
        exchange: editFormData.exchange.trim(),
        amount: Number(editFormData.amount),
        leverage: Number(editFormData.leverage),
        stop_loss_percent: Number(editFormData.stop_loss_percent),
        take_profit_percent: Number(editFormData.take_profit_percent),
        trading_mode: editFormData.trading_mode,
        enable_trailing: !!editFormData.enable_trailing,
        enable_notifications: !!editFormData.enable_notifications,
        is_active: !!editFormData.is_active
      }

      if (parsedTpLevels !== null) {
        payload.tp_levels = parsedTpLevels
      }

      if (editFormData.enable_trailing) {
        payload.trailing_type = editFormData.trailing_type
        if (editFormData.trailing_type === 'percent') {
          payload.trailing_percent = Number(editFormData.trailing_percent)
        } else if (editFormData.trailing_type === 'atr') {
          payload.trailing_atr_multiplier = Number(editFormData.trailing_atr_multiplier)
          payload.trailing_atr_period = Number(editFormData.trailing_atr_period)
        }
      }

      if (editFormData.api_key && editFormData.api_key.trim()) {
        payload.api_key = editFormData.api_key.trim()
      }
      if (editFormData.api_secret && editFormData.api_secret.trim()) {
        payload.api_secret = editFormData.api_secret.trim()
      }

      await axios.put(`/api/config/${editFormData.id}`, payload, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      setShowEditModal(false)
      setEditFormData(null)
      setFlashMessage({ type: 'success', text: 'Cập nhật bot config thành công.' })
      fetchConfigs()
    } catch (error) {
      setFlashMessage({
        type: 'danger',
        text: error.response?.data?.detail || 'Cập nhật config thất bại'
      })
    } finally {
      setEditSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Bạn có chắc muốn xóa config này?')) {
      try {
        await axios.delete(`/api/config/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        fetchConfigs()
      } catch (error) {
        alert('Lỗi: ' + (error.response?.data?.detail || 'Xóa thất bại'))
      }
    }
  }

  const editValidation = editFormData ? validateEditForm(editFormData) : { isValid: false }

  return (
    <div>
      {flashMessage && (
        <div className={`alert alert-${flashMessage.type}`} role="alert">
          {flashMessage.text}
        </div>
      )}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Bot Configurations</h2>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <i className="bi bi-plus-circle me-2"></i>
          Tạo Config Mới
        </button>
      </div>

      <div className="card">
        <div className="table-responsive">
          <table className="table table-hover mb-0">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tên</th>
                <th>Symbol</th>
                <th>Sàn</th>
                <th>Amount</th>
                <th>SL %</th>
                <th>TP %</th>
                <th>Mode</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configs.map((config) => (
                <tr key={config.id}>
                  <td>{config.id}</td>
                  <td>{config.name}</td>
                  <td>{config.symbol}</td>
                  <td>
                    <span className="badge bg-primary text-uppercase">{config.exchange || 'binance'}</span>
                  </td>
                  <td>{config.amount}</td>
                  <td>{config.stop_loss_percent}%</td>
                  <td>{config.take_profit_percent}%</td>
                  <td>
                    <span className="badge bg-info">{config.trading_mode}</span>
                  </td>
                  <td>
                    <span className={`badge ${config.is_active ? 'bg-success' : 'bg-secondary'}`}>
                      {config.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {config.is_paused ? (
                      <span className="badge bg-warning text-dark ms-1">Paused</span>
                    ) : (
                      config.is_active && <span className="badge bg-primary ms-1">Running</span>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-outline-primary me-2"
                      onClick={() => openEditModal(config)}
                    >
                      Sửa
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(config.id)}
                    >
                      Xóa
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Tạo Bot Config Mới</h5>
                <button className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Tên Bot</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Symbol</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.symbol}
                      onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                      placeholder="BTC/USDT"
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Sàn Giao Dịch</label>
                    <select
                      className="form-select"
                      value={formData.exchange}
                      onChange={(e) => setFormData({ ...formData, exchange: e.target.value })}
                      required
                    >
                      <option value="binance">Binance</option>
                      <option value="bitget">Bitget</option>
                      <option value="okx">OKX (OKEx)</option>
                      <option value="bybit">Bybit</option>
                      <option value="gateio">Gate.io</option>
                      <option value="kucoin">KuCoin</option>
                      <option value="huobi">Huobi</option>
                      <option value="coinbasepro">Coinbase Pro</option>
                      <option value="kraken">Kraken</option>
                      <option value="bitfinex">Bitfinex</option>
                    </select>
                    <small className="form-text text-muted">
                      Chọn sàn giao dịch bạn muốn sử dụng
                    </small>
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Amount</label>
                        <input
                          type="number"
                          className="form-control"
                          value={formData.amount}
                          onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                          step="0.01"
                          required
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Leverage</label>
                        <input
                          type="number"
                          className="form-control"
                          value={formData.leverage}
                          onChange={(e) => setFormData({ ...formData, leverage: parseInt(e.target.value) })}
                          min="1"
                          max="125"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Stop Loss (%)</label>
                        <input
                          type="number"
                          className="form-control"
                          value={formData.stop_loss_percent}
                          onChange={(e) => setFormData({ ...formData, stop_loss_percent: e.target.value })}
                          step="0.1"
                          required
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Take Profit (%)</label>
                        <input
                          type="number"
                          className="form-control"
                          value={formData.take_profit_percent}
                          onChange={(e) => setFormData({ ...formData, take_profit_percent: e.target.value })}
                          step="0.1"
                          required
                        />
                      </div>
                    </div>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Trading Mode</label>
                    <select
                      className="form-select"
                      value={formData.trading_mode}
                      onChange={(e) => setFormData({ ...formData, trading_mode: e.target.value })}
                    >
                      <option value="spot">Spot</option>
                      <option value="futures">Futures</option>
                    </select>
                  </div>
                  
                  <hr className="my-4" />
                  <h6 className="mb-3">API Credentials (Tùy chọn)</h6>
                  
                  <div className="mb-3">
                    <label className="form-label">API Key</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.api_key}
                      onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                      placeholder="Nhập API Key từ sàn giao dịch"
                    />
                    <small className="form-text text-muted">
                      API Key từ {formData.exchange.charAt(0).toUpperCase() + formData.exchange.slice(1)} (sẽ được mã hóa)
                    </small>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Secret Key</label>
                    <input
                      type="password"
                      className="form-control"
                      value={formData.api_secret}
                      onChange={(e) => setFormData({ ...formData, api_secret: e.target.value })}
                      placeholder="Nhập Secret Key từ sàn giao dịch"
                    />
                    <small className="form-text text-muted">
                      Secret Key từ {formData.exchange.charAt(0).toUpperCase() + formData.exchange.slice(1)} (sẽ được mã hóa)
                    </small>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">IP Whitelist</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.ip_whitelist}
                      onChange={(e) => setFormData({ ...formData, ip_whitelist: e.target.value })}
                      placeholder="1.2.3.4, 5.6.7.8"
                    />
                    <small className="form-text text-muted">
                      Danh sách IP được phép (phân cách bằng dấu phẩy). Ví dụ: 1.2.3.4, 5.6.7.8
                    </small>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                    Hủy
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Tạo
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showEditModal && editFormData && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Chỉnh Sửa Bot Config</h5>
                <button className="btn-close" onClick={() => setShowEditModal(false)}></button>
              </div>
              <form onSubmit={handleUpdate}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Tên Bot</label>
                    <input
                      type="text"
                      className={`form-control ${editErrors.name ? 'is-invalid' : ''}`}
                      value={editFormData.name}
                      onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                      required
                    />
                    {editErrors.name && <div className="invalid-feedback">{editErrors.name}</div>}
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Symbol</label>
                    <input
                      type="text"
                      className={`form-control ${editErrors.symbol ? 'is-invalid' : ''}`}
                      value={editFormData.symbol}
                      onChange={(e) => setEditFormData({ ...editFormData, symbol: e.target.value })}
                      placeholder="BTC/USDT hoặc BTCUSDT"
                      required
                    />
                    {editErrors.symbol && <div className="invalid-feedback">{editErrors.symbol}</div>}
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Sàn Giao Dịch</label>
                    <select
                      className={`form-select ${editErrors.exchange ? 'is-invalid' : ''}`}
                      value={editFormData.exchange}
                      onChange={(e) => setEditFormData({ ...editFormData, exchange: e.target.value })}
                      required
                    >
                      <option value="binance">Binance</option>
                      <option value="bitget">Bitget</option>
                      <option value="okx">OKX (OKEx)</option>
                      <option value="bybit">Bybit</option>
                      <option value="gateio">Gate.io</option>
                      <option value="kucoin">KuCoin</option>
                      <option value="huobi">Huobi</option>
                      <option value="coinbasepro">Coinbase Pro</option>
                      <option value="kraken">Kraken</option>
                      <option value="bitfinex">Bitfinex</option>
                    </select>
                    {editErrors.exchange && <div className="invalid-feedback">{editErrors.exchange}</div>}
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
                          step="0.01"
                          required
                        />
                        {editErrors.amount && <div className="invalid-feedback">{editErrors.amount}</div>}
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Leverage</label>
                        <input
                          type="number"
                          className={`form-control ${editErrors.leverage ? 'is-invalid' : ''}`}
                          value={editFormData.leverage}
                          onChange={(e) => setEditFormData({ ...editFormData, leverage: e.target.value })}
                          min="1"
                          max="125"
                        />
                        {editErrors.leverage && <div className="invalid-feedback">{editErrors.leverage}</div>}
                      </div>
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Stop Loss (%)</label>
                        <input
                          type="number"
                          className={`form-control ${editErrors.stop_loss_percent ? 'is-invalid' : ''}`}
                          value={editFormData.stop_loss_percent}
                          onChange={(e) => setEditFormData({ ...editFormData, stop_loss_percent: e.target.value })}
                          step="0.1"
                          required
                        />
                        {editErrors.stop_loss_percent && <div className="invalid-feedback">{editErrors.stop_loss_percent}</div>}
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Take Profit (%)</label>
                        <input
                          type="number"
                          className={`form-control ${editErrors.take_profit_percent ? 'is-invalid' : ''}`}
                          value={editFormData.take_profit_percent}
                          onChange={(e) => setEditFormData({ ...editFormData, take_profit_percent: e.target.value })}
                          step="0.1"
                          required
                        />
                        {editErrors.take_profit_percent && <div className="invalid-feedback">{editErrors.take_profit_percent}</div>}
                      </div>
                    </div>
                  </div>

                  <div className="mb-3">
                    <label className="form-label">TP Levels (JSON)</label>
                    <textarea
                      className={`form-control ${editErrors.tp_levels_input ? 'is-invalid' : ''}`}
                      value={editFormData.tp_levels_input}
                      onChange={(e) => setEditFormData({ ...editFormData, tp_levels_input: e.target.value })}
                      rows="3"
                      placeholder='[{"percent":1,"close_percent":50}]'
                    />
                    {editErrors.tp_levels_input && (
                      <div className="invalid-feedback">{editErrors.tp_levels_input}</div>
                    )}
                    <small className="form-text text-muted">
                      Ví dụ: [{'{"percent":1,"close_percent":50}'}]
                    </small>
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Trading Mode</label>
                    <select
                      className="form-select"
                      value={editFormData.trading_mode}
                      onChange={(e) => setEditFormData({ ...editFormData, trading_mode: e.target.value })}
                    >
                      <option value="spot">Spot</option>
                      <option value="futures">Futures</option>
                    </select>
                  </div>

                  <div className="form-check form-switch mb-3">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={editFormData.enable_trailing}
                      onChange={(e) => setEditFormData({ ...editFormData, enable_trailing: e.target.checked })}
                    />
                    <label className="form-check-label">Bật Trailing</label>
                  </div>

                  {editFormData.enable_trailing && (
                    <div className="border rounded p-3 mb-3">
                      <div className="mb-3">
                        <label className="form-label">Trailing Type</label>
                        <select
                          className={`form-select ${editErrors.trailing_type ? 'is-invalid' : ''}`}
                          value={editFormData.trailing_type}
                          onChange={(e) => setEditFormData({ ...editFormData, trailing_type: e.target.value })}
                        >
                          <option value="percent">Percent</option>
                          <option value="atr">ATR</option>
                        </select>
                        {editErrors.trailing_type && <div className="invalid-feedback">{editErrors.trailing_type}</div>}
                      </div>
                      {editFormData.trailing_type === 'percent' && (
                        <div className="mb-3">
                          <label className="form-label">Trailing Percent</label>
                          <input
                            type="number"
                            className={`form-control ${editErrors.trailing_percent ? 'is-invalid' : ''}`}
                            value={editFormData.trailing_percent}
                            onChange={(e) => setEditFormData({ ...editFormData, trailing_percent: e.target.value })}
                            step="0.1"
                          />
                          {editErrors.trailing_percent && <div className="invalid-feedback">{editErrors.trailing_percent}</div>}
                        </div>
                      )}
                      {editFormData.trailing_type === 'atr' && (
                        <div className="row">
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label">ATR Multiplier</label>
                              <input
                                type="number"
                                className={`form-control ${editErrors.trailing_atr_multiplier ? 'is-invalid' : ''}`}
                                value={editFormData.trailing_atr_multiplier}
                                onChange={(e) => setEditFormData({ ...editFormData, trailing_atr_multiplier: e.target.value })}
                                step="0.1"
                              />
                              {editErrors.trailing_atr_multiplier && (
                                <div className="invalid-feedback">{editErrors.trailing_atr_multiplier}</div>
                              )}
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label">ATR Period</label>
                              <input
                                type="number"
                                className={`form-control ${editErrors.trailing_atr_period ? 'is-invalid' : ''}`}
                                value={editFormData.trailing_atr_period}
                                onChange={(e) => setEditFormData({ ...editFormData, trailing_atr_period: e.target.value })}
                                min="1"
                              />
                              {editErrors.trailing_atr_period && (
                                <div className="invalid-feedback">{editErrors.trailing_atr_period}</div>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="form-check form-switch mb-3">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={editFormData.enable_notifications}
                      onChange={(e) => setEditFormData({ ...editFormData, enable_notifications: e.target.checked })}
                    />
                    <label className="form-check-label">Bật thông báo</label>
                  </div>

                  <div className="form-check form-switch mb-3">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={editFormData.is_active}
                      onChange={(e) => setEditFormData({ ...editFormData, is_active: e.target.checked })}
                    />
                    <label className="form-check-label">Kích hoạt bot</label>
                  </div>

                  <hr className="my-4" />
                  <h6 className="mb-3">API Credentials (Tùy chọn)</h6>

                  <div className="mb-3">
                    <label className="form-label">API Key</label>
                    <input
                      type="text"
                      className="form-control"
                      value={editFormData.api_key}
                      onChange={(e) => setEditFormData({ ...editFormData, api_key: e.target.value })}
                      placeholder="Để trống nếu không thay đổi"
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Secret Key</label>
                    <input
                      type="password"
                      className="form-control"
                      value={editFormData.api_secret}
                      onChange={(e) => setEditFormData({ ...editFormData, api_secret: e.target.value })}
                      placeholder="Để trống nếu không thay đổi"
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>
                    Hủy
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={!editValidation.isValid || editSubmitting}>
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

