import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

export default function Trading() {
  const { token } = useAuth()
  const [configs, setConfigs] = useState([])
  const [selectedConfig, setSelectedConfig] = useState(null)
  const [orderForm, setOrderForm] = useState({
    side: 'buy',
    symbol: '',
    amount: '',
    price: '',
    order_type: 'market'
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '', details: null })
  const [symbols, setSymbols] = useState([])
  const [symbolSearch, setSymbolSearch] = useState('')
  const [showSymbolDropdown, setShowSymbolDropdown] = useState(false)
  const [loadingSymbols, setLoadingSymbols] = useState(false)

  const { theme } = useTheme()
  const [chartSymbol, setChartSymbol] = useState('BTC/USDT')

  useEffect(() => {
    if (token) {
      fetchConfigs()
      // Load common symbols by default
      setSymbols(getCommonSymbols())
    } else {
      setMessage({ type: 'danger', text: 'Vui lòng đăng nhập trước' })
    }
  }, [token])

  const getTradingViewSymbol = () => {
    const ex = (selectedConfig?.exchange || "binance").toUpperCase()
    const sym = (chartSymbol || "BTCUSDT").replace("/", "").toUpperCase()
    return `${ex}:${sym}`
  }

  // Embed TradingView Widget
  useEffect(() => {
    if (window.TradingView) {
      const tvSymbol = getTradingViewSymbol()
      try {
        new window.TradingView.widget({
          width: "100%",
          height: "100%",
          symbol: tvSymbol,
          interval: "60",
          timezone: "Asia/Ho_Chi_Minh",
          theme: theme === "Tối" ? "dark" : "light",
          style: "1",
          locale: "vi",
          enable_publishing: false,
          hide_side_toolbar: false,
          allow_symbol_change: true,
          container_id: "tradingview-chart",
        });
      } catch (err) {
        console.error("Failed to init TradingView widget:", err);
      }
    }
    return () => {
      const container = document.getElementById("tradingview-chart");
      if (container) {
        container.innerHTML = "";
      }
    };
  }, [selectedConfig, chartSymbol, theme]);



  const getCommonSymbols = () => {
    return [
      'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
      'ADA/USDT', 'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT', 'AVAX/USDT',
      'LINK/USDT', 'UNI/USDT', 'LTC/USDT', 'ATOM/USDT', 'ETC/USDT',
      'NEAR/USDT', 'ALGO/USDT', 'FIL/USDT', 'TRX/USDT', 'EOS/USDT',
      'AAVE/USDT', 'SAND/USDT', 'MANA/USDT', 'AXS/USDT', 'THETA/USDT',
      'ICP/USDT', 'FTM/USDT', 'HBAR/USDT', 'EGLD/USDT', 'FLOW/USDT',
      'BCH/USDT', 'XLM/USDT', 'VET/USDT', 'APT/USDT', 'ARB/USDT',
      'OP/USDT', 'SUI/USDT', 'INJ/USDT', 'TIA/USDT', 'SEI/USDT'
    ]
  }

  const fetchConfigs = async () => {
    try {
      // Ensure token is in headers
      const response = await axios.get('/api/config/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.data && Array.isArray(response.data)) {
        setConfigs(response.data.filter(c => c.is_active))
        setMessage({ type: '', text: '' })
      } else {
        setMessage({ type: 'warning', text: 'Không có config nào' })
      }
    } catch (error) {
      console.error('Failed to fetch configs:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Không thể tải danh sách configs'
      
      if (error.response?.status === 403 || error.response?.status === 401) {
        setMessage({ 
          type: 'danger', 
          text: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.' 
        })
      } else {
        setMessage({ 
          type: 'danger', 
          text: `Lỗi: ${errorMsg}. Kiểm tra backend đã chạy và đã đăng nhập chưa.` 
        })
      }
    }
  }

  const handleConfigSelect = (configId) => {
    const config = configs.find(c => c.id === configId)
    setSelectedConfig(config)
    if (config) {
      const defaultSymbol = config.symbol || ''
      setOrderForm({
        ...orderForm,
        symbol: defaultSymbol,
        amount: config.amount || ''
      })
      setSymbolSearch(defaultSymbol)
      setChartSymbol(defaultSymbol)
      // Load symbols from exchange if config has API credentials
      if (config.api_key_encrypted) {
        fetchSymbols(config.id)
      }
      // Otherwise keep common symbols
    }
  }

  const fetchSymbols = async (configId) => {
    setLoadingSymbols(true)
    try {
      const response = await axios.get(`/api/trading/symbols/${configId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.data.symbols && response.data.symbols.length > 0) {
        setSymbols(response.data.symbols)
      }
    } catch (error) {
      console.error('Failed to fetch symbols from exchange:', error)
      // Keep common symbols if API fails
    } finally {
      setLoadingSymbols(false)
    }
  }

  const filteredSymbols = symbols.filter(symbol => 
    symbol.toLowerCase().includes(symbolSearch.toLowerCase())
  ).slice(0, 20) // Limit to 20 results

  const handleSymbolSelect = (symbol) => {
    setOrderForm({ ...orderForm, symbol })
    setSymbolSearch(symbol)
    setChartSymbol(symbol)
    setShowSymbolDropdown(false)
  }

  const submitOrder = async (side) => {
    // Cập nhật side hiện tại để hiển thị trạng thái
    setOrderForm((prev) => ({ ...prev, side }))

    if (!selectedConfig) {
      setMessage({ type: 'danger', text: 'Vui lòng chọn bot config' })
      return
    }

    if (orderForm.order_type === 'limit' && !orderForm.price) {
      setMessage({ type: 'danger', text: 'Vui lòng nhập giá cho limit order' })
      return
    }

    if (!orderForm.amount || parseFloat(orderForm.amount) <= 0) {
      setMessage({ type: 'danger', text: 'Vui lòng nhập số lượng hợp lệ' })
      return
    }

    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const payload = {
        bot_config_id: selectedConfig.id,
        side,
        order_type: orderForm.order_type,
        amount: parseFloat(orderForm.amount)
      }

      // Add symbol if provided (override config symbol)
      if (orderForm.symbol && orderForm.symbol.trim()) {
        payload.symbol = orderForm.symbol.trim()
      }

      if (orderForm.order_type === 'limit' && orderForm.price) {
        payload.price = parseFloat(orderForm.price)
      }

      const response = await axios.post('/api/trading/place-order', payload, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      // Tạo message với thông tin chi tiết
      const messageText = `Đặt lệnh ${side.toUpperCase()} thành công! Order ID: ${response.data.order_id}`
      const orderDetails = response.data
      
      setMessage({
        type: 'success',
        text: messageText,
        details: orderDetails
      })

      // Không reset Side, chỉ reset giá/amount/symbol về mặc định
      const resetSymbol = selectedConfig.symbol || ''
      setOrderForm((prev) => ({
        ...prev,
        symbol: resetSymbol,
        amount: selectedConfig.amount || '',
        price: '',
        order_type: 'market'
      }))
      setSymbolSearch(resetSymbol)

    } catch (error) {
      let errorText = 'Đặt lệnh thất bại'
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (typeof detail === 'string') {
          errorText = detail
        } else if (Array.isArray(detail)) {
          errorText = detail.map(err => {
            if (typeof err === 'string') return err
            if (err.msg) return err.msg
            return JSON.stringify(err)
          }).join(', ')
        } else if (typeof detail === 'object') {
          errorText = JSON.stringify(detail, null, 2)
        } else {
          errorText = String(detail)
        }
      } else if (error.message) {
        errorText = error.message
      }
      
      // Format error message for better display
      if (errorText.includes('timestamp') || errorText.includes('-1021')) {
        errorText = `⏰ Lỗi đồng bộ thời gian: ${errorText}\n\n💡 Giải pháp: Vui lòng sync thời gian máy tính. Chạy script FIX_TIMESTAMP_BINANCE.bat (cần quyền Admin)`
      }
      
      setMessage({
        type: 'danger',
        text: errorText,
        details: null
      })
    } finally {
      setLoading(false)
    }
  }

  // Sync symbolSearch with orderForm.symbol
  useEffect(() => {
    if (orderForm.symbol && !symbolSearch) {
      setSymbolSearch(orderForm.symbol)
    }
  }, [orderForm.symbol])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.position-relative')) {
        setShowSymbolDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="container-fluid py-4" style={{ color: "var(--text-primary)" }}>
      {/* Header */}
      <div 
        className="mb-4 border-0 shadow-lg position-relative overflow-hidden"
        style={{
          background: "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
          color: "white",
          borderRadius: "16px",
          padding: "2.5rem"
        }}
      >
        <div className="row align-items-center">
          <div className="col-md-8">
            <h1 className="display-5 fw-bold mb-2 text-white">Đặt Lệnh Trading</h1>
            <p className="lead mb-0 text-white opacity-75">
              Đặt lệnh giao dịch thủ công nhanh chóng hoặc gửi tín hiệu giả lập trực tiếp lên sàn giao dịch.
            </p>
          </div>
          <div className="col-md-4 text-md-end mt-3 mt-md-0">
            <i className="bi bi-graph-up-arrow text-white" style={{ fontSize: "5rem", opacity: "0.2" }}></i>
          </div>
        </div>
      </div>

      {message.text && (
        <div className={`alert alert-${message.type} alert-dismissible fade show`} role="alert">
          <div style={{ whiteSpace: 'pre-wrap' }}>
            <strong>{message.text}</strong>
            {message.details && (message.details.stop_loss || message.details.take_profit) && (
              <div className="mt-2">
                <small>
                  <strong>📊 TP/SL đã được đặt tự động:</strong><br />
                  {message.details.filled_price && (
                    <>💰 <strong>Giá khớp:</strong> {parseFloat(message.details.filled_price).toFixed(2)}<br /></>
                  )}
                  {message.details.stop_loss && (
                    <>🛑 <strong>Stop Loss:</strong> {parseFloat(message.details.stop_loss).toFixed(2)}<br /></>
                  )}
                  {message.details.take_profit && (
                    <>🎯 <strong>Take Profit:</strong> {parseFloat(message.details.take_profit).toFixed(2)}</>
                  )}
                </small>
              </div>
            )}
          </div>
          <button
            type="button"
            className="btn-close"
            onClick={() => setMessage({ type: '', text: '', details: null })}
          ></button>
        </div>
      )}

      <div className="row g-4">
        {/* Left Column: Config, Manual Order Form, Webhook Test */}
        <div className="col-lg-5 col-md-12">
          {/* Card: Chọn Bot Config */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--bg-secondary)" }}>
            <div className="card-header border-0 bg-transparent pt-4 pb-0">
              <h5 className="card-title fw-bold mb-0">
                <i className="bi bi-gear-fill text-primary me-2"></i> Chọn Bot Config
              </h5>
            </div>
            <div className="card-body">
              <select
                className="form-select"
                value={selectedConfig?.id || ''}
                onChange={(e) => handleConfigSelect(parseInt(e.target.value))}
              >
                <option value="">-- Chọn Bot Config --</option>
                {configs.map((config) => (
                  <option key={config.id} value={config.id}>
                    {config.exchange?.toUpperCase() || 'BINANCE'} - {config.name}
                  </option>
                ))}
              </select>

              {selectedConfig && (
                <div className="mt-3 p-3 rounded bg-light-subtle" style={{ background: "rgba(255,255,255,0.02)" }}>
                  <small className="text-muted d-block" style={{ lineHeight: "1.6" }}>
                    <strong>Sàn:</strong> {selectedConfig.exchange?.toUpperCase() || 'BINANCE'}<br />
                    <strong>Trade Mode:</strong>{' '}
                    {selectedConfig.trading_mode === 'futures' ? 'Futures' : 'Spot'}<br />
                    <strong>Symbol mặc định:</strong> {selectedConfig.symbol}<br />
                    <strong>Amount mặc định:</strong> {selectedConfig.amount}<br />
                    <strong>SL / TP:</strong> {selectedConfig.stop_loss_percent}% / {selectedConfig.take_profit_percent}%
                  </small>
                </div>
              )}
            </div>
          </div>

          {/* Card: Đặt lệnh thủ công */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--bg-secondary)" }}>
            <div className="card-header border-0 bg-transparent pt-4 pb-0">
              <h5 className="card-title fw-bold mb-0">
                <i className="bi bi-wallet2 text-success me-2"></i> Đặt Lệnh Thủ Công
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={(e) => e.preventDefault()}>
                <div className="mb-3">
                  <label className="form-label small fw-bold text-secondary text-uppercase mb-1">Symbol</label>
                  <div className="position-relative">
                    <input
                      type="text"
                      className="form-control"
                      value={symbolSearch}
                      onChange={(e) => {
                        const value = e.target.value
                        setSymbolSearch(value)
                        setShowSymbolDropdown(value.length > 0 && filteredSymbols.length > 0)
                      }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          setChartSymbol(symbolSearch)
                          setOrderForm((prev) => ({ ...prev, symbol: symbolSearch }))
                          setShowSymbolDropdown(false)
                        }
                      }}
                      onBlur={() => {
                        setChartSymbol(symbolSearch)
                        setOrderForm((prev) => ({ ...prev, symbol: symbolSearch }))
                        setShowSymbolDropdown(false)
                      }}
                      onFocus={() => {
                        if (symbolSearch.length > 0 && filteredSymbols.length > 0) {
                          setShowSymbolDropdown(true)
                        }
                      }}
                      placeholder={selectedConfig?.symbol || "BTC/USDT"}
                    />
                    {loadingSymbols && (
                      <span className="position-absolute end-0 top-50 translate-middle-y me-2">
                        <span className="spinner-border spinner-border-sm text-primary" role="status"></span>
                      </span>
                    )}
                    {showSymbolDropdown && filteredSymbols.length > 0 && (
                      <div 
                        className="list-group position-absolute w-100 border shadow-sm" 
                        style={{ 
                          zIndex: 1000, 
                          maxHeight: '200px', 
                          overflowY: 'auto',
                          backgroundColor: 'var(--bg-secondary)',
                          border: '1px solid var(--border-color)',
                          marginTop: '2px'
                        }}
                      >
                        {filteredSymbols.map((symbol) => (
                          <button
                            key={symbol}
                            type="button"
                            className="list-group-item list-group-item-action border-0"
                            onMouseDown={(e) => {
                              e.preventDefault()
                              handleSymbolSelect(symbol)
                            }}
                            style={{ cursor: 'pointer', background: 'transparent', color: 'var(--text-primary)' }}
                          >
                            {symbol}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <small className="text-muted d-block mt-1">
                    {selectedConfig ? (
                      <>
                        Gõ để tìm kiếm. Để trống sẽ dùng symbol từ config ({selectedConfig.symbol})
                      </>
                    ) : (
                      `Gõ để tìm kiếm. ${symbols.length} symbols phổ biến`
                    )}
                  </small>
                </div>

                <div className="mb-3">
                  <label className="form-label small fw-bold text-secondary text-uppercase mb-1">Order Type</label>
                  <select
                    className="form-select"
                    value={orderForm.order_type}
                    onChange={(e) => setOrderForm({ ...orderForm, order_type: e.target.value })}
                  >
                    <option value="market">Market (Giá thị trường)</option>
                    <option value="limit">Limit (Giá chỉ định)</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label className="form-label small fw-bold text-secondary text-uppercase mb-1">Amount</label>
                  <input
                    type="number"
                    className="form-control"
                    step="0.0001"
                    value={orderForm.amount}
                    onChange={(e) => setOrderForm({ ...orderForm, amount: e.target.value })}
                    placeholder="Nhập số lượng"
                    required
                  />
                  <small className="text-muted d-block mt-1">
                    Để trống sẽ dùng amount từ config
                  </small>
                </div>

                {orderForm.order_type === 'limit' && (
                  <div className="mb-3">
                    <label className="form-label small fw-bold text-secondary text-uppercase mb-1">Price</label>
                    <input
                      type="number"
                      className="form-control"
                      step="0.01"
                      value={orderForm.price}
                      onChange={(e) => setOrderForm({ ...orderForm, price: e.target.value })}
                      placeholder="Nhập giá"
                      required={orderForm.order_type === 'limit'}
                    />
                  </div>
                )}

                <div className="alert alert-warning text-center small py-2 border-0 mb-3" style={{ background: "rgba(255, 193, 7, 0.1)", color: "#ffc107" }}>
                  <strong>⚠️ Cảnh báo:</strong> Đây là lệnh THẬT trên {selectedConfig?.exchange?.toUpperCase() || 'SÀN GIAO DỊCH'}!
                </div>

                <div className="d-flex gap-2">
                  <button
                    type="button"
                    className="btn btn-success w-50"
                    disabled={loading || !selectedConfig}
                    onClick={() => submitOrder('buy')}
                  >
                    {loading && orderForm.side === 'buy' ? 'Đang BUY...' : 'Đặt lệnh BUY'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-danger w-50"
                    disabled={loading || !selectedConfig}
                    onClick={() => submitOrder('sell')}
                  >
                    {loading && orderForm.side === 'sell' ? 'Đang SELL...' : 'Đặt lệnh SELL'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Right Column: TradingView Technical Chart Widget */}
        <div className="col-lg-7 col-md-12">
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--bg-secondary)", height: "calc(100% - 20px)", minHeight: "600px" }}>
            <div className="card-header border-0 bg-transparent pt-4 pb-0">
              <h5 className="card-title fw-bold mb-0">
                <i className="bi bi-graph-up text-primary me-2"></i> Biểu đồ Kỹ thuật TradingView
              </h5>
            </div>
            <div className="card-body d-flex flex-column h-100">
              <p className="text-muted small">
                Biểu đồ thời gian thực cho symbol đang được chọn (<strong>{getTradingViewSymbol()}</strong>). Bạn có thể đổi symbol trực tiếp trong biểu đồ hoặc chọn config khác.
              </p>
              
              <div 
                className="rounded overflow-hidden border flex-grow-1 d-flex flex-column"
                style={{ background: "rgba(0,0,0,0.1)", minHeight: "450px" }}
              >
                <div id="tradingview-chart" className="flex-grow-1" style={{ width: "100%" }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

