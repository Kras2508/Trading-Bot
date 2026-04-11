import React from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path) => location.pathname === path

  return (
    <div className="d-flex">
      <div className="sidebar" style={{ width: '250px', minHeight: '100vh' }}>
        <h3>
          <i className="bi bi-robot me-2"></i>
          Trading Bot
        </h3>
        <nav className="nav flex-column">
          <Link
            to="/"
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            <i className="bi bi-speedometer2 me-2"></i>
            Dashboard
          </Link>
          <Link
            to="/configs"
            className={`nav-link ${isActive('/configs') ? 'active' : ''}`}
          >
            <i className="bi bi-gear me-2"></i>
            Bot Configs
          </Link>
          <Link
            to="/trading"
            className={`nav-link ${isActive('/trading') ? 'active' : ''}`}
          >
            <i className="bi bi-graph-up-arrow me-2"></i>
            Đặt Lệnh
          </Link>
          <Link
            to="/orders"
            className={`nav-link ${isActive('/orders') ? 'active' : ''}`}
          >
            <i className="bi bi-list-ul me-2"></i>
            Orders
          </Link>
          <Link
            to="/monitoring"
            className={`nav-link ${isActive('/monitoring') ? 'active' : ''}`}
          >
            <i className="bi bi-activity me-2"></i>
            Monitoring
          </Link>
          <Link
            to="/activity-logs"
            className={`nav-link ${isActive('/activity-logs') ? 'active' : ''}`}
          >
            <i className="bi bi-journal-text me-2"></i>
            Nhật Ký / Lỗi
          </Link>
        </nav>
        <div className="mt-auto pt-4">
          <div className="mb-3">
            <small>Đăng nhập: {user?.username}</small>
          </div>
          <button className="btn btn-outline-light w-100" onClick={handleLogout}>
            Đăng xuất
          </button>
        </div>
      </div>
      <div className="main-content flex-grow-1">
        <Outlet />
      </div>
    </div>
  )
}

