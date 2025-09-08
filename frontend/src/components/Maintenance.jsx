import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Maintenance = () => {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [room, setRoom] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/maintenance/?ordering=-created_at')
      setItems(res.data)
    } catch (e) {
      setError('Failed to load maintenance requests')
    }
  }

  useEffect(() => { load() }, [])

  const createReq = async (e) => {
    e.preventDefault()
    try {
      await axios.post('http://localhost:8000/api/maintenance/', { title, description, room })
      setTitle(''); setDescription(''); setRoom('')
      load()
    } catch (e) {
      setError('Failed to create request')
    }
  }

  const setStatus = async (id, status) => {
    try {
      await axios.patch(`http://localhost:8000/api/maintenance/${id}/update_status/`, { status })
      load()
    } catch (e) {
      setError('Failed to update status')
    }
  }

  return (
    <div className="page">
      <h1>Maintenance</h1>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={createReq} style={{ maxWidth: 600, marginBottom: 16 }}>
        <div className="form-group">
          <label htmlFor="m_title">Title</label>
          <input id="m_title" value={title} onChange={(e)=>setTitle(e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="m_desc">Description</label>
          <input id="m_desc" value={description} onChange={(e)=>setDescription(e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="m_room">Room ID</label>
          <input id="m_room" value={room} onChange={(e)=>setRoom(e.target.value)} placeholder="room primary key" />
        </div>
        <button type="submit" className="register-btn">Submit request</button>
      </form>

      <div className="recent-activities">
        <h3>Requests</h3>
        <div className="activity-list">
          {items.map((r) => (
            <div key={r.id} className="activity-item">
              <div className="activity-content" style={{ width: '100%' }}>
                <p style={{ margin: 0 }}>{r.title} <span style={{ color: 'var(--text-secondary)' }}>({r.status})</span></p>
                <span>{r.description}</span>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  <button className="register-btn" onClick={()=>setStatus(r.id, 'pending')}>Pending</button>
                  <button className="register-btn" onClick={()=>setStatus(r.id, 'in_progress')}>In Progress</button>
                  <button className="register-btn" onClick={()=>setStatus(r.id, 'completed')}>Completed</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Maintenance



