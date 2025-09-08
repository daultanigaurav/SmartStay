import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Attendance = () => {
  const { user } = useAuth()
  const [days, setDays] = useState([])
  const [month, setMonth] = useState(() => new Date().toISOString().slice(0,7))
  const [error, setError] = useState('')

  const load = async () => {
    try {
      // naive: fetch all and filter client-side for the month
      const res = await axios.get('http://localhost:8000/api/attendance/?ordering=-date')
      setDays(res.data)
    } catch (e) {
      setError('Failed to load attendance')
    }
  }

  useEffect(() => { load() }, [])

  const markToday = async () => {
    try {
      await axios.post('http://localhost:8000/api/attendance/mark/')
      load()
    } catch (e) {
      setError('Failed to mark today')
    }
  }

  const monthDays = () => {
    const [y,m] = month.split('-').map(Number)
    const start = new Date(y, m-1, 1)
    const end = new Date(y, m, 0)
    const list = []
    for (let d=1; d<=end.getDate(); d++) {
      const date = new Date(y, m-1, d).toISOString().slice(0,10)
      const rec = days.find(x => x.date === date)
      list.push({ date, present: rec ? rec.present : false })
    }
    return list
  }

  return (
    <div className="page">
      <h1>Attendance</h1>
      {error && <div className="error-message">{error}</div>}

      <div className="form-row" style={{ marginBottom: 12 }}>
        <input type="month" value={month} onChange={(e)=>setMonth(e.target.value)} />
        <button className="register-btn" onClick={markToday}>Mark today</button>
      </div>

      <div className="recent-activities">
        <h3>{month}</h3>
        <div className="activity-list">
          {monthDays().map(d => (
            <div key={d.date} className="activity-item">
              <div className="activity-content" style={{ width: '100%' }}>
                <p style={{ margin: 0 }}>{d.date} — {d.present ? 'Present' : 'Absent'}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Attendance



