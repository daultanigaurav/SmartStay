import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'

const Dashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [recentActivities, setRecentActivities] = useState([])
  const [complaints, setComplaints] = useState([])
  const [newComplaint, setNewComplaint] = useState({ title: '', description: '' })
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState('')
  const [formSuccess, setFormSuccess] = useState('')

  useEffect(() => {
    fetchDashboardData()
    fetchMyComplaints()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, roomsResponse, paymentsResponse] = await Promise.all([
        axios.get('http://localhost:8000/api/dashboard/stats/'),
        axios.get('http://localhost:8000/api/rooms/stats/'),
        axios.get('http://localhost:8000/api/payments/stats/')
      ])
      
      setStats(statsResponse.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setLoading(false)
    }
  }

  const fetchMyComplaints = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/complaints/?ordering=-created_at')
      // Backend returns all complaints for admins; students only theirs. That's fine for demo.
      setComplaints(res.data)
    } catch (e) {
      console.error('Failed to fetch complaints', e)
    }
  }

  const submitComplaint = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setFormError('')
    setFormSuccess('')
    try {
      await axios.post('http://localhost:8000/api/complaints/', {
        title: newComplaint.title,
        description: newComplaint.description
      })
      setFormSuccess('Complaint submitted')
      setNewComplaint({ title: '', description: '' })
      fetchMyComplaints()
      fetchDashboardData()
    } catch (error) {
      const data = error.response?.data
      let message = 'Failed to submit complaint'
      if (data) {
        if (typeof data === 'string') message = data
        else if (typeof data === 'object') {
          const parts = []
          for (const [k, v] of Object.entries(data)) {
            parts.push(Array.isArray(v) ? `${k}: ${v.join(', ')}` : `${k}: ${String(v)}`)
          }
          message = parts.join('\n') || message
        }
      }
      setFormError(message)
    } finally {
      setSubmitting(false)
    }
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

  const roomTypeData = [
    { name: 'Single', value: 15, color: '#0088FE' },
    { name: 'Double', value: 25, color: '#00C49F' },
    { name: 'Triple', value: 20, color: '#FFBB28' },
    { name: 'Quad', value: 10, color: '#FF8042' }
  ]

  const monthlyRevenueData = [
    { month: 'Jan', revenue: 45000 },
    { month: 'Feb', revenue: 52000 },
    { month: 'Mar', revenue: 48000 },
    { month: 'Apr', revenue: 61000 },
    { month: 'May', revenue: 55000 },
    { month: 'Jun', revenue: 67000 }
  ]

  const attendanceData = [
    { day: 'Mon', present: 85, absent: 15 },
    { day: 'Tue', present: 90, absent: 10 },
    { day: 'Wed', present: 88, absent: 12 },
    { day: 'Thu', present: 92, absent: 8 },
    { day: 'Fri', present: 87, absent: 13 },
    { day: 'Sat', present: 80, absent: 20 },
    { day: 'Sun', present: 75, absent: 25 }
  ]

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome back, {user?.first_name || user?.username}!</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div className="stat-content">
            <h3>{stats?.total_students || 0}</h3>
            <p>Total Students</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9,22 9,12 15,12 15,22"></polyline>
            </svg>
          </div>
          <div className="stat-content">
            <h3>{stats?.total_rooms || 0}</h3>
            <p>Total Rooms</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="1" x2="12" y2="23"></line>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
          <div className="stat-content">
            <h3>₹{stats?.monthly_revenue || 0}</h3>
            <p>Monthly Revenue</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
            </svg>
          </div>
          <div className="stat-content">
            <h3>{stats?.pending_complaints || 0}</h3>
            <p>Pending Complaints</p>
          </div>
        </div>
      </div>

      {/* Quick Actions - Submit Complaint */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="actions-grid">
          <div className="action-btn" style={{ cursor: 'default' }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
            </svg>
            Submit Complaint
          </div>
        </div>
        <form onSubmit={submitComplaint} style={{ marginTop: '1rem' }}>
          {formError && <div className="error-message" style={{ whiteSpace: 'pre-wrap' }}>{formError}</div>}
          {formSuccess && <div className="error-message" style={{ color: '#065f46', background: '#ecfdf5', borderColor: '#a7f3d0' }}>{formSuccess}</div>}
          <div className="form-group">
            <label htmlFor="complaint_title">Title</label>
            <input
              id="complaint_title"
              type="text"
              value={newComplaint.title}
              onChange={(e) => setNewComplaint({ ...newComplaint, title: e.target.value })}
              placeholder="Complaint title"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="complaint_description">Description</label>
            <input
              id="complaint_description"
              type="text"
              value={newComplaint.description}
              onChange={(e) => setNewComplaint({ ...newComplaint, description: e.target.value })}
              placeholder="Describe the issue"
              required
            />
          </div>
          <button type="submit" className="register-btn" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit'}
          </button>
        </form>
      </div>

      {/* My Complaints */}
      <div className="recent-activities" style={{ marginTop: '1.5rem' }}>
        <h3>My Complaints</h3>
        {complaints.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>No complaints yet.</p>
        ) : (
          <div className="activity-list">
            {complaints.map((c) => (
              <div key={c.id} className="activity-item">
                <div className="activity-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                    <polyline points="14,2 14,8 20,8"></polyline>
                  </svg>
                </div>
                <div className="activity-content">
                  <p style={{ margin: 0 }}>{c.title}</p>
                  <span>Status: {c.status}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Room Occupancy</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={roomTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {roomTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Monthly Revenue</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyRevenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`₹${value}`, 'Revenue']} />
                <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Weekly Attendance</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={attendanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="present" fill="#00C49F" name="Present" />
                <Bar dataKey="absent" fill="#FF8042" name="Absent" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Activities (static examples kept) */}
      <div className="recent-activities">
        <h3>Recent Activities</h3>
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="23" y1="11" x2="17" y2="11"></line>
              </svg>
            </div>
            <div className="activity-content">
              <p>New student John Doe registered</p>
              <span>2 hours ago</span>
            </div>
          </div>
          <div className="activity-item">
            <div className="activity-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            </div>
            <div className="activity-content">
              <p>Payment of ₹5000 received from Room 101</p>
              <span>4 hours ago</span>
            </div>
          </div>
          <div className="activity-item">
            <div className="activity-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
              </svg>
            </div>
            <div className="activity-content">
              <p>New complaint submitted by Jane Smith</p>
              <span>6 hours ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

