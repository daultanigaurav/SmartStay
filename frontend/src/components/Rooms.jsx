import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Rooms = () => {
  const { user } = useAuth()
  const [rooms, setRooms] = useState([])
  const [active, setActive] = useState([])
  const [targetRoom, setTargetRoom] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const [avail, allocations] = await Promise.all([
        axios.get('http://localhost:8000/api/rooms/available/'),
        axios.get('http://localhost:8000/api/allocations/active/')
      ])
      setRooms(avail.data)
      setActive(allocations.data)
    } catch (e) {
      setError('Failed to load rooms')
    }
  }

  useEffect(() => { load() }, [])

  const book = async (roomId) => {
    try {
      await axios.post('http://localhost:8000/api/allocations/', { room: roomId, start_date: new Date().toISOString().slice(0,10), status: 'active' })
      load()
    } catch (e) {
      setError('Failed to book room')
    }
  }

  const transfer = async () => {
    if (!targetRoom) return
    try {
      await axios.post('http://localhost:8000/api/allocations/transfer/', { room: targetRoom })
      setTargetRoom('')
      load()
    } catch (e) {
      setError('Failed to transfer')
    }
  }

  return (
    <div className="page">
      <h1>Rooms</h1>
      {error && <div className="error-message">{error}</div>}

      <div className="recent-activities">
        <h3>Available rooms</h3>
        <div className="activity-list">
          {rooms.map(r => (
            <div key={r.id} className="activity-item">
              <div className="activity-content" style={{ width: '100%' }}>
                <p style={{ margin: 0 }}>#{r.number} • {r.room_type} • capacity {r.capacity}</p>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  <button className="register-btn" onClick={()=>book(r.id)}>Book</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="recent-activities" style={{ marginTop: 16 }}>
        <h3>My active allocation</h3>
        <div className="activity-list">
          {active.map(a => (
            <div key={a.id} className="activity-item">
              <div className="activity-content" style={{ width: '100%' }}>
                <p style={{ margin: 0 }}>Room #{a.room} since {a.start_date}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="form-row" style={{ marginTop: 8 }}>
          <input value={targetRoom} onChange={(e)=>setTargetRoom(e.target.value)} placeholder="Target room id" />
          <button className="register-btn" onClick={transfer}>Request transfer</button>
        </div>
      </div>
    </div>
  )
}

export default Rooms



