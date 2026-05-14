import React, { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";

export default function ActivityLogs() {
  const { token } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedLogs, setExpandedLogs] = useState(new Set());

  // Filters
  const [filters, setFilters] = useState({
    level: "",
    category: "",
    bot_config_id: "",
    limit: 100,
  });

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filters.level) params.append("level", filters.level);
      if (filters.category) params.append("category", filters.category);
      if (filters.bot_config_id)
        params.append("bot_config_id", filters.bot_config_id);
      params.append("limit", filters.limit);

      const response = await axios.get(
        `/api/monitoring/logs?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      setLogs(response.data || []);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
      setError(err.response?.data?.detail || "Không thể tải nhật ký hoạt động");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleApplyFilters = () => {
    fetchLogs();
  };

  const handleClearFilters = () => {
    setFilters({
      level: "",
      category: "",
      bot_config_id: "",
      limit: 100,
    });
    setTimeout(() => fetchLogs(), 100);
  };

  const getLevelBadge = (level) => {
    const badges = {
      error: "bg-danger",
      warning: "bg-warning",
      success: "bg-success",
      info: "bg-info",
    };
    return badges[level] || "bg-secondary";
  };

  const getLevelText = (level) => {
    const texts = {
      error: "Lỗi",
      warning: "Cảnh báo",
      success: "Thành công",
      info: "Thông tin",
    };
    return texts[level] || level;
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}-${String(date.getUTCDate()).padStart(2, "0")} ${String(date.getUTCHours()).padStart(2, "0")}:${String(date.getUTCMinutes()).padStart(2, "0")}:${String(date.getUTCSeconds()).padStart(2, "0")} UTC`;
  };

  return (
    <div className="container-fluid p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>
          <i className="bi bi-journal-text me-2"></i>
          Nhật Ký Hoạt Động / Lỗi
        </h2>
        <button
          className="btn btn-primary"
          onClick={fetchLogs}
          disabled={loading}
        >
          <i className="bi bi-arrow-clockwise me-2"></i>
          {loading ? "Đang tải..." : "Tải lại"}
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Bộ lọc</h5>
        </div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-3">
              <label className="form-label">Mức độ</label>
              <select
                className="form-select"
                value={filters.level}
                onChange={(e) => handleFilterChange("level", e.target.value)}
              >
                <option value="">Tất cả</option>
                <option value="error">Lỗi</option>
                <option value="warning">Cảnh báo</option>
                <option value="success">Thành công</option>
                <option value="info">Thông tin</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Danh mục</label>
              <select
                className="form-select"
                value={filters.category}
                onChange={(e) => handleFilterChange("category", e.target.value)}
              >
                <option value="">Tất cả</option>
                <option value="trading">Trading</option>
                <option value="webhook">Webhook</option>
                <option value="config">Config</option>
                <option value="system">System</option>
              </select>
            </div>
            <div className="col-md-2">
              <label className="form-label">Bot Config ID</label>
              <input
                type="number"
                className="form-control"
                value={filters.bot_config_id}
                onChange={(e) =>
                  handleFilterChange("bot_config_id", e.target.value)
                }
                placeholder="Tất cả"
              />
            </div>
            <div className="col-md-2">
              <label className="form-label">Số lượng</label>
              <input
                type="number"
                className="form-control"
                value={filters.limit}
                onChange={(e) => handleFilterChange("limit", e.target.value)}
                min="1"
                max="1000"
              />
            </div>
            <div className="col-md-2 d-flex align-items-end">
              <div className="d-flex gap-2 w-100">
                <button
                  className="btn btn-primary flex-fill"
                  onClick={handleApplyFilters}
                >
                  Áp dụng
                </button>
                <button
                  className="btn btn-outline-secondary"
                  onClick={handleClearFilters}
                >
                  Xóa
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div
          className="alert alert-danger alert-dismissible fade show"
          role="alert"
        >
          <strong>Lỗi:</strong> {error}
          <button
            type="button"
            className="btn-close"
            onClick={() => setError(null)}
          ></button>
        </div>
      )}

      {/* Logs Table */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Danh sách logs ({logs.length})</h5>
        </div>
        <div className="card-body p-0">
          {loading ? (
            <div className="text-center p-4">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Đang tải...</span>
              </div>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center p-4">
              <p className="text-secondary">Không có log nào</p>
            </div>
          ) : (
            <div
              className="table-responsive"
              style={{ maxHeight: "70vh", overflowY: "auto" }}
            >
              <table className="table table-hover table-striped mb-0">
                <thead className="sticky-top">
                  <tr>
                    <th style={{ width: "80px" }}>ID</th>
                    <th style={{ width: "100px" }}>Thời gian</th>
                    <th style={{ width: "100px" }}>Mức độ</th>
                    <th style={{ width: "120px" }}>Danh mục</th>
                    <th>Thông điệp</th>
                    <th style={{ width: "100px" }}>Bot Config</th>
                    <th style={{ width: "100px" }}>Order ID</th>
                    <th style={{ width: "150px" }}>Chi tiết</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td>{log.id}</td>
                      <td>
                        <small>{formatDateTime(log.created_at)}</small>
                      </td>
                      <td>
                        <span className={`badge ${getLevelBadge(log.level)}`}>
                          {getLevelText(log.level)}
                        </span>
                      </td>
                      <td>
                        <span className="badge bg-secondary">
                          {log.category}
                        </span>
                      </td>
                      <td>
                        <div
                          style={{ maxWidth: "400px", wordBreak: "break-word" }}
                        >
                          {log.message}
                        </div>
                      </td>
                      <td>
                        {log.bot_config_id ? (
                          <span className="badge bg-info">
                            {log.bot_config_id}
                          </span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        {log.order_id ? (
                          <span className="badge bg-primary">
                            {log.order_id}
                          </span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        {log.details ? (
                          <button
                            className="btn btn-sm btn-outline-info"
                            type="button"
                            onClick={() => {
                              const newExpanded = new Set(expandedLogs);
                              if (newExpanded.has(log.id)) {
                                newExpanded.delete(log.id);
                              } else {
                                newExpanded.add(log.id);
                              }
                              setExpandedLogs(newExpanded);
                            }}
                          >
                            <i
                              className={`bi ${expandedLogs.has(log.id) ? "bi-eye-slash" : "bi-eye"}`}
                            ></i>{" "}
                            {expandedLogs.has(log.id) ? "Ẩn" : "Xem"}
                          </button>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Details Expand */}
      {logs.map(
        (log) =>
          log.details &&
          expandedLogs.has(log.id) && (
            <div key={`details-${log.id}`} className="mt-2 mb-3">
              <div className="card card-body">
                <h6>Chi tiết:</h6>
                <pre
                  style={{
                    maxHeight: "300px",
                    overflowY: "auto",
                    whiteSpace: "pre-wrap",
                    fontSize: "0.9em",
                    backgroundColor: "var(--bg-secondary)",
                    color: "var(--text-primary)",
                    padding: "1rem",
                    borderRadius: "4px",
                  }}
                >
                  {JSON.stringify(log.details, null, 2)}
                </pre>
                {log.source_ip && (
                  <div className="mt-2">
                    <small className="text-muted">
                      <strong>IP:</strong> {log.source_ip}
                    </small>
                  </div>
                )}
              </div>
            </div>
          ),
      )}
    </div>
  );
}
