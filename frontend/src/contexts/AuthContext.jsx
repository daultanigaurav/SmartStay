import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }, [token])

  // Check if user is logged in on app start
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get('http://localhost:8000/api/users/me/')
          setUser(response.data)
        } catch (error) {
          console.error('Auth check failed:', error)
          localStorage.removeItem('token')
          setToken(null)
        }
      }
      setLoading(false)
    }
    checkAuth()
  }, [token])

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/api/auth/token/', {
        username,
        password
      })
      
      const { access, refresh } = response.data
      localStorage.setItem('token', access)
      localStorage.setItem('refresh', refresh)
      setToken(access)
      
      // Get user details
      const userResponse = await axios.get('http://localhost:8000/api/users/me/')
      setUser(userResponse.data)
      
      return { success: true }
    } catch (error) {
      console.error('Login failed:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
    setToken(null)
    setUser(null)
  }

  const register = async (userData) => {
    try {
      const response = await axios.post('http://localhost:8000/api/register/', userData)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Registration failed:', error)
      // Normalize backend error shapes to a human-readable string
      const data = error.response?.data
      let message = 'Registration failed'
      if (data) {
        if (typeof data === 'string') {
          message = data
        } else if (Array.isArray(data)) {
          message = data.join('\n')
        } else if (typeof data === 'object') {
          // DRF validation errors are often { field: ["msg", ...], non_field_errors: [...] }
          const parts = []
          for (const [key, value] of Object.entries(data)) {
            const text = Array.isArray(value) ? value.join(', ') : String(value)
            parts.push(key === 'non_field_errors' ? text : `${key}: ${text}`)
          }
          message = parts.join('\n') || message
        }
      }
      return { success: false, error: message }
    }
  }

  const value = {
    user,
    token,
    login,
    logout,
    register,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}



