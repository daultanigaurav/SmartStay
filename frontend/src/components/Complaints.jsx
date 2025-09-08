import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Complaints = () => {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const res = await axios.get('http://localhost:8000/api/complaints/?ordering=-created_at')
      setItems(res.data)
    } catch (e) {
      setError('Failed to load complaints')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const createComplaint = async (e) => {
    e.preventDefault()
    try {
      await axios.post('http://localhost:8000/api/complaints/', { title, description })
      setTitle('')
      setDescription('')
      load()
    } catch (e) {
      setError('Failed to create complaint')
    }
  }

  const addComment = async (complaintId, message) => {
    if (!message) return
    try {
      await axios.post(`http://localhost:8000/api/complaints/${complaintId}/comments/`, { message })
      load()
    } catch (e) {
      setError('Failed to add comment')
    }
  }

  if (loading) return (<div className="page"><div className="loading-spinner"></div></div>)

  return (
    <div className="page">
      <h1>Complaints</h1>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={createComplaint} style={{ maxWidth: 600, marginBottom: 16 }}>
        <div className="form-group">
          <label htmlFor="c_title">Title</label>
          <input id="c_title" value={title} onChange={(e)=>setTitle(e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="c_desc">Description</label>
          <input id="c_desc" value={description} onChange={(e)=>setDescription(e.target.value)} required />
        </div>
        <button type="submit" className="register-btn">Submit complaint</button>
      </form>

      <div className="recent-activities">
        <h3>My Complaints</h3>
        <div className="activity-list">
          {items.map((c) => (
            <div key={c.id} className="activity-item">
              <div className="activity-content" style={{ width: '100%' }}>
                <p style={{ margin: 0 }}>{c.title} <span style={{ color: 'var(--text-secondary)' }}>({c.status})</span></p>
                <span>{c.description}</span>
                <div style={{ marginTop: 8 }}>
                  {(c.comments || []).map(cm => (
                    <div key={cm.id} style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                      {cm.user_name}: {cm.message}
                    </div>
                  ))}
                </div>
                <CommentInput onSubmit={(msg)=>addComment(c.id, msg)} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const CommentInput = ({ onSubmit }) => {
  const [v, setV] = useState('')
  return (
    <form onSubmit={(e)=>{e.preventDefault(); onSubmit(v); setV('')}} style={{ display: 'flex', gap: 8, marginTop: 8 }}>
      <input value={v} onChange={(e)=>setV(e.target.value)} placeholder="Add a comment" style={{ flex: 1 }} />
      <button className="register-btn" type="submit">Add</button>
    </form>
  )
}

export default Complaints



