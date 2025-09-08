import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Visitors = () => {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ visitor_name: '', visitor_phone: '', purpose: '', visit_date: '', visit_time: '' })
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/visitors/?ordering=-created_at')
      setItems(res.data)
    } catch (e) {
      setError('Failed to load visitors')
    }
  }
  useEffect(() => { load() }, [])

  const requestPass = async (e) => {
    e.preventDefault()
    try {
      await axios.post('http://localhost:8000/api/visitors/', form)
      setForm({ visitor_name: '', visitor_phone: '', purpose: '', visit_date: '', visit_time: '' })
      load()
    } catch (e) {
      setError('Failed to request pass')
    }
  }

  const approve = async (id) => {
    try {
      await axios.patch(`http://localhost:8000/api/visitors/${id}/`, { status: 'approved' })
      load()
    } catch (e) {
      setError('Failed to approve')
    }
  }

  return (
    <div className="page">
      <h1>Visitors</h1>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={requestPass} style={{ maxWidth: 600, marginBottom: 16 }}>
        <div className="form-row">
          <div className="form-group">
            <label>Name</label>
            <input value={form.visitor_name} onChange={(e)=>setForm({ ...form, visitor_name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input value={form.visitor_phone} onChange={(e)=>setForm({ ...form, visitor_phone: e.target.value })} required />
          </div>
        </div>
        <div className="form-group">
          <label>Purpose</label>
          <input value={form.purpose} onChange={(e)=>setForm({ ...form, purpose: e.target.value })} required />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Date</label>
            <input type="date" value={form.visit_date} onChange={(e)=>setForm({ ...form, visit_date: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Time</label>
            <input type="time" value={form.visit_time} onChange={(e)=>setForm({ ...form, visit_time: e.target.value })} required />
          </div>
        </div>
        <button type="submit" className="register-btn">Request Pass</button>
      </form>

      <div className="recent-activities">
        <h3>Visitor Requests</h3>
        <div className="activity-list">
          {items.map(v => (
            <div key={v.id} className="activity-item">
              <div className="activity-content" style={{ width: '100%' }}>
                <p style={{ margin: 0 }}>{v.visitor_name} • {v.visit_date} {v.visit_time} — {v.status}</p>
                {v.status === 'pending' && (
                  <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                    <button className="register-btn" onClick={()=>approve(v.id)}>Approve</button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Visitors
