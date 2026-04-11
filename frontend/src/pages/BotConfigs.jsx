import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function BotConfigs() {
  const { token } = useAuth()
  const [configs, setConfigs] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
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
  })

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
      setFormData({
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
      })
    } catch (error) {
      alert('Lỗi: ' + (error.response?.data?.detail || 'Tạo config thất bại'))
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

  return (
    <div>
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
                  </td>
                  <td>
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
    </div>
  )
}

