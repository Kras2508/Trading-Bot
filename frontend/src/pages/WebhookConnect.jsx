import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

export default function WebhookConnect() {
  const { token } = useAuth();
  const { theme } = useTheme();
  
  // Webhook Info & Settings
  const [webhookInfo, setWebhookInfo] = useState({
    webhook_url: "",
    passphrase: "",
    passphrase_required: false,
    tradingview_ips: [],
    ip_whitelist_enabled: false,
    allowed_ips: "",
  });

  // Settings form states
  const [passphraseForm, setPassphraseForm] = useState("");
  const [ipWhitelistForm, setIpWhitelistForm] = useState(false);
  const [allowedIpsForm, setAllowedIpsForm] = useState("");
  const [savingSettings, setSavingSettings] = useState(false);
  const [settingsMessage, setSettingsMessage] = useState({ type: "", text: "" });

  const [configs, setConfigs] = useState([]);
  const [selectedBot, setSelectedBot] = useState("");
  const [customDomain, setCustomDomain] = useState("");
  const [triggerType, setTriggerType] = useState("dynamic"); // 'dynamic', 'buy', 'sell'
  
  // Clipboard copy states
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedPayload, setCopiedPayload] = useState(false);
  const [copiedCommand, setCopiedCommand] = useState(false);
  const [tunnelTool, setTunnelTool] = useState("localtunnel"); // 'localtunnel', 'ngrok'

  // Chart state
  const [scriptLoaded, setScriptLoaded] = useState(false);



  // Load TradingView script
  useEffect(() => {
    const scriptId = "tradingview-widget-script";
    let script = document.getElementById(scriptId);
    
    if (!script) {
      script = document.createElement("script");
      script.id = scriptId;
      script.src = "https://s3.tradingview.com/tv.js";
      script.async = true;
      script.onload = () => setScriptLoaded(true);
      document.head.appendChild(script);
    } else {
      setScriptLoaded(true);
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchWebhookInfo();
      fetchBotConfigs();
    }
  }, [token]);

  const fetchWebhookInfo = async () => {
    try {
      const response = await axios.get("/api/webhook/info", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setWebhookInfo(response.data);
      setPassphraseForm(response.data.passphrase || "");
      setIpWhitelistForm(response.data.ip_whitelist_enabled || false);
      setAllowedIpsForm(response.data.allowed_ips || "");
      
      // Auto-extract host to pre-populate customDomain if not localhost
      const url = new URL(response.data.webhook_url);
      if (!url.hostname.includes("localhost") && !url.hostname.includes("127.0.0.1")) {
        setCustomDomain(url.origin);
      }
    } catch (error) {
      console.error("Failed to fetch webhook info:", error);
    }
  };

  const fetchBotConfigs = async () => {
    try {
      const response = await axios.get("/api/config/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params: {
          active_only: true,
        },
      });
      setConfigs(response.data);
      if (response.data.length > 0) {
        setSelectedBot(response.data[0].name);
      }
    } catch (error) {
      console.error("Failed to fetch active bot configs:", error);
    }
  };

  const getFinalWebhookUrl = () => {
    if (customDomain) {
      const sanitizedDomain = customDomain.replace(/\/$/, "");
      return `${sanitizedDomain}/api/webhook/tradingview`;
    }
    return webhookInfo.webhook_url;
  };

  const getTradingViewSymbol = () => {
    const selectedBotDetails = configs.find((c) => c.name === selectedBot);
    if (!selectedBotDetails) return "BINANCE:BTCUSDT";
    const ex = (selectedBotDetails.exchange || "binance").toUpperCase();
    const sym = (selectedBotDetails.symbol || "BTCUSDT").replace("/", "").toUpperCase();
    return `${ex}:${sym}`;
  };

  // Embed TradingView Widget
  useEffect(() => {
    if (scriptLoaded && window.TradingView && configs.length > 0 && selectedBot) {
      const tvSymbol = getTradingViewSymbol();
      try {
        new window.TradingView.widget({
          autosize: true,
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
  }, [scriptLoaded, selectedBot, configs, theme]);

  const generateJsonPayload = () => {
    const selectedBotDetails = configs.find((c) => c.name === selectedBot);
    const symbolField = selectedBotDetails ? selectedBotDetails.symbol : "{{ticker}}";
    
    let actionVal = "{{strategy.order.action}}";
    if (triggerType === "buy") {
      actionVal = "buy";
    } else if (triggerType === "sell") {
      actionVal = "sell";
    }

    const payload = {
      symbol: triggerType === "dynamic" ? "{{ticker}}" : symbolField,
      action: actionVal,
      config: selectedBot || "Bot_Name",
    };

    if (passphraseForm) {
      payload.passphrase = passphraseForm;
    }

    return JSON.stringify(payload, null, 2);
  };

  const copyToClipboard = (text, setCopiedState) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedState(true);
      setTimeout(() => setCopiedState(false), 2000);
    });
  };

  // Update DB Settings
  const handleSaveSettings = async () => {
    setSavingSettings(true);
    setSettingsMessage({ type: "", text: "" });
    try {
      const response = await axios.post(
        "/api/webhook/settings",
        {
          webhook_passphrase: passphraseForm,
          enable_ip_whitelist: ipWhitelistForm,
          allowed_ips: allowedIpsForm,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      setWebhookInfo((prev) => ({
        ...prev,
        passphrase: response.data.webhook_passphrase,
        passphrase_required: Boolean(response.data.webhook_passphrase),
        ip_whitelist_enabled: response.data.enable_ip_whitelist,
        allowed_ips: response.data.allowed_ips,
      }));
      
      setSettingsMessage({ type: "success", text: "Lưu cấu hình bảo mật thành công!" });
      setTimeout(() => setSettingsMessage({ type: "", text: "" }), 3000);
    } catch (error) {
      console.error("Failed to save settings:", error);
      setSettingsMessage({ type: "danger", text: "Lưu cấu hình thất bại." });
    } finally {
      setSavingSettings(false);
    }
  };

  // Auto add TradingView IPs helper
  const handleAutoAddTV_IPs = () => {
    const currentIps = allowedIpsForm
      ? allowedIpsForm.split(",").map((ip) => ip.trim())
      : [];
    
    const tvIps = webhookInfo.tradingview_ips;
    
    // Merge without duplicates
    const mergedIps = Array.from(new Set([...currentIps, ...tvIps])).filter(Boolean);
    setAllowedIpsForm(mergedIps.join(", "));
  };



  return (
    <div className="container-fluid py-4" style={{ color: "var(--text-primary)" }}>
      {/* Header */}
      <div 
        className="mb-4 border-0 shadow-lg position-relative overflow-hidden"
        style={{
          background: "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)",
          color: "white",
          borderRadius: "16px",
          padding: "2.5rem"
        }}
      >
        <div className="row align-items-center">
          <div className="col-md-8">
            <h1 className="display-5 fw-bold mb-2 text-white">Kết nối TradingView Webhook</h1>
            <p className="lead mb-0 text-white opacity-75">
              Nhận tín hiệu đặt lệnh tự động từ TradingView Alert trực tiếp vào Binance thông qua Webhook bảo mật.
            </p>
          </div>
          <div className="col-md-4 text-md-end mt-3 mt-md-0">
            <i className="bi bi-link-45deg text-white" style={{ fontSize: "5rem", opacity: "0.2" }}></i>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Left Column: Config Generator & Setup */}
        <div className="col-lg-8">
          
          {/* Step 1: Tunnel Expose */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--card-bg)" }}>
            <div className="card-body p-4">
              <div className="d-flex align-items-center mb-3">
                <span className="badge bg-primary rounded-circle me-3 fs-6 p-2 d-flex align-items-center justify-content-center" style={{ width: "32px", height: "32px" }}>1</span>
                <h4 className="card-title mb-0">Mở cổng kết nối (Tunneling)</h4>
              </div>
              <p className="text-muted">
                TradingView chỉ có thể gửi tín hiệu tới một URL công khai (Public URL). Nếu bot đang chạy dưới máy cá nhân của bạn, hãy mở cổng <code>8000</code> bằng một trong hai cách dưới đây:
              </p>

              {/* Toggle Switch */}
              <div className="btn-group mb-3 w-100" role="group">
                <button
                  type="button"
                  className={`btn btn-sm ${tunnelTool === "localtunnel" ? "btn-primary" : "btn-outline-secondary"}`}
                  onClick={() => setTunnelTool("localtunnel")}
                >
                  <i className="bi bi-lightning-fill me-1"></i> Cách A: LocalTunnel (Chạy ngay, không cần cài đặt)
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${tunnelTool === "ngrok" ? "btn-primary" : "btn-outline-secondary"}`}
                  onClick={() => setTunnelTool("ngrok")}
                >
                  <i className="bi bi-terminal-fill me-1"></i> Cách B: Ngrok (Cần cài đặt)
                </button>
              </div>

              {tunnelTool === "localtunnel" ? (
                <>
                  <div className="bg-dark text-light p-3 rounded mb-3 position-relative" style={{ fontFamily: "monospace", fontSize: "0.95rem" }}>
                    <span className="text-secondary"># Chạy LocalTunnel ở cổng 8000</span>
                    <br />
                    npx localtunnel --port 8000
                    <button 
                      className="btn btn-sm btn-outline-secondary position-absolute end-0 top-50 translate-middle-y me-2"
                      onClick={() => copyToClipboard("npx localtunnel --port 8000", setCopiedCommand)}
                    >
                      {copiedCommand ? <i className="bi bi-check-lg text-success"></i> : <i className="bi bi-clipboard"></i>}
                    </button>
                  </div>
                  <div className="alert alert-info border-0 mb-0 d-flex align-items-start" style={{ background: "rgba(13, 202, 240, 0.08)", color: "#0dcaf0" }}>
                    <i className="bi bi-info-circle-fill me-2 mt-1"></i>
                    <div>
                      <strong>Cách sử dụng:</strong> Hãy copy dòng lệnh trên, dán vào terminal của bạn rồi nhấn Enter. Sau khi chạy, LocalTunnel sẽ cung cấp một link public có đuôi <code>.loca.lt</code>. Dán link đó vào Bước 2.
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="bg-dark text-light p-3 rounded mb-3 position-relative" style={{ fontFamily: "monospace", fontSize: "0.95rem" }}>
                    <span className="text-secondary"># Chạy Ngrok ở cổng 8000</span>
                    <br />
                    ngrok http 8000
                    <button 
                      className="btn btn-sm btn-outline-secondary position-absolute end-0 top-50 translate-middle-y me-2"
                      onClick={() => copyToClipboard("ngrok http 8000", setCopiedCommand)}
                    >
                      {copiedCommand ? <i className="bi bi-check-lg text-success"></i> : <i className="bi bi-clipboard"></i>}
                    </button>
                  </div>
                  <div className="alert alert-info border-0 mb-0 d-flex align-items-start" style={{ background: "rgba(13, 202, 240, 0.08)", color: "#0dcaf0" }}>
                    <i className="bi bi-info-circle-fill me-2 mt-1"></i>
                    <div>
                      <strong>Yêu cầu:</strong> Bạn cần tải Ngrok từ trang chủ, đăng ký tài khoản miễn phí và thêm authtoken trước khi chạy. Bạn sẽ nhận được link dạng <code>https://xxxx.ngrok-free.app</code>.
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Step 2: Custom domain input & webhook URL */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--card-bg)" }}>
            <div className="card-body p-4">
              <div className="d-flex align-items-center mb-3">
                <span className="badge bg-primary rounded-circle me-3 fs-6 p-2 d-flex align-items-center justify-content-center" style={{ width: "32px", height: "32px" }}>2</span>
                <h4 className="card-title mb-0">Thiết lập Webhook URL</h4>
              </div>
              <p className="text-muted">
                Nhập domain Public của bạn vào bên dưới để tự động sinh đường dẫn Webhook chính xác.
              </p>

              <div className="mb-3">
                <label className="form-label fw-bold small text-uppercase text-muted">Domain Public của bạn (Ngrok / Cloudflare / LocalTunnel)</label>
                <div className="input-group">
                  <span className="input-group-text bg-light text-secondary border-0"><i className="bi bi-globe"></i></span>
                  <input
                    type="text"
                    className="form-control border-0 bg-light-subtle text-light"
                    placeholder="Ví dụ: https://xxxx.loca.lt hoặc https://xxxx.ngrok-free.app"
                    value={customDomain}
                    onChange={(e) => setCustomDomain(e.target.value)}
                    style={{ background: "var(--bg-light)" }}
                  />
                </div>
              </div>

              <div className="p-3 border border-dashed rounded bg-light-subtle d-flex justify-content-between align-items-center" style={{ background: "rgba(255, 255, 255, 0.02)" }}>
                <div>
                  <span className="fw-bold d-block text-secondary small text-uppercase">Địa chỉ Webhook URL hoàn chỉnh</span>
                  <code className="fs-5 text-warning">{getFinalWebhookUrl()}</code>
                </div>
                <button
                  className="btn btn-outline-primary"
                  onClick={() => copyToClipboard(getFinalWebhookUrl(), setCopiedUrl)}
                >
                  {copiedUrl ? (
                    <>
                      <i className="bi bi-check-lg me-1"></i> Đã chép
                    </>
                  ) : (
                    <>
                      <i className="bi bi-clipboard me-1"></i> Sao chép
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Step 3: Payload generator */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--card-bg)" }}>
            <div className="card-body p-4">
              <div className="d-flex align-items-center mb-3">
                <span className="badge bg-primary rounded-circle me-3 fs-6 p-2 d-flex align-items-center justify-content-center" style={{ width: "32px", height: "32px" }}>3</span>
                <h4 className="card-title mb-0">Tạo mã tín hiệu (Alert Message Payload)</h4>
              </div>
              <p className="text-muted">
                Lựa chọn bot cấu hình và loại tín hiệu để tự động sinh nội dung JSON. Bạn sẽ dán nội dung này vào ô <strong>Message</strong> khi tạo Alert trên TradingView.
              </p>

              <div className="row g-3 mb-3">
                <div className="col-md-6">
                  <label className="form-label fw-bold small text-uppercase text-muted">1. Chọn Bot Config</label>
                  <select
                    className="form-select bg-light text-light border-0"
                    value={selectedBot}
                    onChange={(e) => setSelectedBot(e.target.value)}
                  >
                    {configs.length === 0 ? (
                      <option value="">-- Không có bot hoạt động --</option>
                    ) : (
                      configs.map((c) => (
                        <option key={c.id} value={c.name}>
                          {c.name} ({c.symbol} - {c.trading_mode})
                        </option>
                      ))
                    )}
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label fw-bold small text-uppercase text-muted">2. Loại hành động (Action)</label>
                  <select
                    className="form-select bg-light text-light border-0"
                    value={triggerType}
                    onChange={(e) => setTriggerType(e.target.value)}
                  >
                    <option value="dynamic">Động (Theo tín hiệu Indicator/Strategy)</option>
                    <option value="buy">Mua / Long (Lệnh BUY cứng)</option>
                    <option value="sell">Bán / Short (Lệnh SELL cứng)</option>
                  </select>
                </div>
              </div>

              <div className="position-relative">
                <span className="form-label fw-bold d-block mb-2 small text-uppercase text-muted">Nội dung Alert Message (JSON)</span>
                <pre 
                  className="bg-dark text-light p-3 rounded" 
                  style={{ fontSize: "0.9rem", maxHeight: "250px", overflowY: "auto" }}
                >
                  {generateJsonPayload()}
                </pre>
                <button
                  className="btn btn-sm btn-primary position-absolute end-0 top-0 mt-3 me-3"
                  onClick={() => copyToClipboard(generateJsonPayload(), setCopiedPayload)}
                  disabled={configs.length === 0 && !selectedBot}
                >
                  {copiedPayload ? (
                    <>
                      <i className="bi bi-check-lg me-1"></i> Đã chép
                    </>
                  ) : (
                    <>
                      <i className="bi bi-clipboard me-1"></i> Sao chép JSON
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Interactive TradingView Chart Widget */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--card-bg)" }}>
            <div className="card-body p-4">
              <div className="d-flex align-items-center mb-3">
                <i className="bi bi-graph-up text-primary fs-4 me-3"></i>
                <h4 className="card-title mb-0">Biểu đồ Kỹ thuật TradingView</h4>
              </div>
              <p className="text-muted">
                Dưới đây là biểu đồ thời gian thực tích hợp trực tiếp từ TradingView cho bot đang được lựa chọn (<strong>{getTradingViewSymbol()}</strong>).
              </p>
              
              <div 
                className="rounded overflow-hidden border"
                style={{ height: "450px", background: "rgba(0,0,0,0.1)" }}
              >
                {configs.length === 0 ? (
                  <div className="h-100 d-flex align-items-center justify-content-center text-muted">
                    Vui lòng cấu hình ít nhất một bot để xem biểu đồ.
                  </div>
                ) : !scriptLoaded ? (
                  <div className="h-100 d-flex align-items-center justify-content-center text-muted">
                    <div className="spinner-border text-primary me-2" role="status"></div>
                    Đang tải biểu đồ TradingView...
                  </div>
                ) : (
                  <div id="tradingview-chart" style={{ width: "100%", height: "100%" }}></div>
                )}
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Security config, testing, and info */}
        <div className="col-lg-4">


          
          {/* Dynamic Security Configurations (Interactive Form) */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--card-bg)" }}>
            <div className="card-body p-4">
              <h5 className="card-title fw-bold mb-3">
                <i className="bi bi-shield-lock me-2 text-primary"></i> Cấu hình Bảo mật Webhook
              </h5>

              {settingsMessage.text && (
                <div className={`alert alert-${settingsMessage.type} py-2 px-3 small mb-3`}>
                  {settingsMessage.text}
                </div>
              )}

              {/* Passphrase Input */}
              <div className="mb-3">
                <label className="form-label small fw-bold text-secondary text-uppercase mb-1">
                  Khóa Bảo mật (Passphrase)
                </label>
                <div className="input-group input-group-sm">
                  <input
                    type="text"
                    className="form-control bg-light-subtle text-light"
                    placeholder="Để trống hoặc nhấp tạo ngẫu nhiên"
                    value={passphraseForm}
                    onChange={(e) => setPassphraseForm(e.target.value)}
                  />
                  <button
                    className="btn btn-outline-secondary"
                    type="button"
                    onClick={() => {
                      const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
                      let randPass = "";
                      for (let i = 0; i < 16; i++) {
                        randPass += chars.charAt(Math.floor(Math.random() * chars.length));
                      }
                      setPassphraseForm(randPass);
                    }}
                  >
                    <i className="bi bi-arrow-clockwise me-1"></i> Tạo ngẫu nhiên
                  </button>
                </div>
                <small className="text-muted d-block mt-1" style={{ fontSize: "0.75rem" }}>
                  Mật khẩu đính kèm trong tin nhắn của TradingView. Nên đặt để tránh bị hack tài khoản.
                </small>
              </div>

              <hr />

              {/* IP Whitelist toggle */}
              <div className="form-check form-switch mb-3">
                <input
                  className="form-check-input"
                  type="checkbox"
                  role="switch"
                  id="enableIpWhitelistSwitch"
                  checked={ipWhitelistForm}
                  onChange={(e) => setIpWhitelistForm(e.target.checked)}
                />
                <label className="form-check-label small fw-bold" htmlFor="enableIpWhitelistSwitch">
                  Kích hoạt IP Whitelist
                </label>
                <small className="text-muted d-block mt-1" style={{ fontSize: "0.75rem" }}>
                  Chỉ tiếp nhận yêu cầu từ các địa chỉ IP được liệt kê bên dưới.
                </small>
              </div>

              {/* Allowed IPs text area */}
              {ipWhitelistForm && (
                <div className="mb-3">
                  <div className="d-flex justify-content-between align-items-center mb-1">
                    <label className="form-label small fw-bold text-secondary text-uppercase mb-0">
                      IP được phép (cách nhau bằng dấu phẩy)
                    </label>
                    <button
                      className="btn btn-sm btn-link text-decoration-none py-0 fs-7 text-primary"
                      onClick={handleAutoAddTV_IPs}
                      type="button"
                    >
                      <i className="bi bi-plus-circle me-1"></i>Add TV IPs
                    </button>
                  </div>
                  <textarea
                    rows="3"
                    className="form-control form-control-sm bg-light-subtle text-light font-monospace"
                    style={{ fontSize: "0.85rem" }}
                    placeholder="Ví dụ: 127.0.0.1, 52.89.214.238"
                    value={allowedIpsForm}
                    onChange={(e) => setAllowedIpsForm(e.target.value)}
                  ></textarea>
                </div>
              )}

              <button
                className="btn btn-sm btn-primary w-100 mt-2"
                onClick={handleSaveSettings}
                disabled={savingSettings}
              >
                {savingSettings ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                    Đang lưu cấu hình...
                  </>
                ) : (
                  <>
                    <i className="bi bi-save me-1"></i> Lưu cấu hình bảo mật
                  </>
                )}
              </button>
            </div>
          </div>



          {/* TradingView UI Alert Quick Guide */}
          <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: "12px", background: "var(--card-bg)" }}>
            <div className="card-body p-4">
              <h5 className="card-title fw-bold mb-3">
                <i className="bi bi-info-square me-2 text-primary"></i> Hướng dẫn TradingView
              </h5>
              <ol className="small ps-3 text-muted mb-0" style={{ lineHeight: "1.6" }}>
                <li className="mb-2">Mở đồ thị TradingView và nhấn <code>Alt + A</code> hoặc click nút Alert ở thanh trên.</li>
                <li className="mb-2">Chọn điều kiện kích hoạt (Ví dụ: giá cắt qua chỉ báo, EMA cross, v.v.).</li>
                <li className="mb-2">Chuyển qua tab <strong>Notifications</strong>, tích chọn <strong>Webhook URL</strong> và dán địa chỉ ở <span className="text-primary fw-bold">Bước 2</span> vào.</li>
                <li className="mb-2">Quay lại tab <strong>Settings</strong>, dán mã JSON sinh ở <span className="text-primary fw-bold">Bước 3</span> vào ô <strong>Message</strong>.</li>
                <li className="mb-2">Nhấn <strong>Create</strong> để bắt đầu nhận tín hiệu.</li>
              </ol>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
