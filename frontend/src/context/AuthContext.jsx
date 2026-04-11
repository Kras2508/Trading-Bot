import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [user, setUser] = useState(null)

  const fetchUser = async (authToken) => {
    if (!authToken) return
    try {
      const response = await axios.get('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      if (error.response?.status === 401 || error.response?.status === 403) {
        // Token invalid or expired, clear it
        setToken(null)
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        setUser(null)
      }
    }
  }

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser(token)
    } else {
      delete axios.defaults.headers.common['Authorization']
      setUser(null)
    }
    // fetchUser is defined above and uses token parameter, so it's safe to ignore
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login', null, {
        params: { username, password }
      })
      const { access_token } = response.data
      setToken(access_token)
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      await fetchUser(access_token)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Đăng nhập thất bại'
      }
    }
  }

  const register = async (username, email, password) => {
    try {
      await axios.post('/api/auth/register', {
        username,
        email,
        password
      })
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Đăng ký thất bại'
      }
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const value = {
    token,
    user,
    login,
    register,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


