import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Notices = () => {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [filter, setFilter] = useState('all')
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/notices/?ordering=-created_at')
      setItems(res.data)
    } catch (e) {
      setError('Failed to load notices')
    }
  }

  useEffect(() => { load() }, [])

  const markRead = async (id, read) => {
    try {
      const path = read ? 'read' : 'unread'
      await axios.post(`http://localhost:8000/api/notices/${id}/${path}/`)
      load()
    } catch (e) {
      setError('Failed to update notice state')
    }
  }

  const filtered = items.filter(n => filter === 'all' ? true : (filter === 'read' ? n.is_read : !n.is_read))

  return (
    <div className="page">
      <h1>Notices</h1>
      {error && <div className="error-message">{error}</div>}

      <div className="form-row" style={{ marginBottom: 12 }}>
        <button className="register-btn" onClick={()=>setFilter('all')}>All</button>
        <button className="register-btn" onClick={()=>setFilter('unread')}>Unread</button>
        <button className="register-btn" onClick={()=>setFilter('read')}>Read</button>
      </div>

      <div className="recent-activities">
        <div className="activity-list">
          {filtered.map(n => (
            <div key={n.id} className="activity-item">
              <div className="activity-content" style={{ width: '100%' }}>
                <p style={{ margin: 0 }}>
                  <strong>{n.title}</strong> {n.is_read ? <span style={{ color:'#16a34a' }}>(read)</span> : <span style={{ color:'#dc2626' }}>(unread)</span>}
                </p>
                <span>{n.content}</span>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  {!n.is_read ? (
                    <button className="register-btn" onClick={()=>markRead(n.id, true)}>Mark read</button>
                  ) : (
                    <button className="register-btn" onClick={()=>markRead(n.id, false)}>Mark unread</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Notices



