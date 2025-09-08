import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Profile = () => {
  const { user } = useAuth()
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    address: ''
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [pwMsg, setPwMsg] = useState('')
  const [pwSaving, setPwSaving] = useState(false)
  const [avatarMsg, setAvatarMsg] = useState('')
  const [avatarPreview, setAvatarPreview] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/users/me/')
        setForm({
          first_name: res.data.first_name || '',
          last_name: res.data.last_name || '',
          phone_number: res.data.phone_number || '',
          address: res.data.address || ''
        })
      } catch (e) {
        console.error('Failed to load profile', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')
    try {
      await axios.patch('http://localhost:8000/api/users/me/', form)
      setMessage('Profile updated')
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to update'
      if (data && typeof data === 'object') {
        msg = Object.entries(data).map(([k,v]) => `${k}: ${Array.isArray(v)?v.join(', '):String(v)}`).join('\n')
      }
      setMessage(msg)
    } finally {
      setSaving(false)
    }
  }

  const changePassword = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const current_password = formData.get('current_password')
    const new_password = formData.get('new_password')
    const confirm_password = formData.get('confirm_password')
    setPwMsg('')
    setPwSaving(true)
    try {
      const res = await axios.post('http://localhost:8000/api/users/change-password/', {
        current_password, new_password, confirm_password
      })
      setPwMsg(res.data?.detail || 'Password updated')
      e.target.reset()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to change password'
      if (data && typeof data === 'object') {
        msg = Object.entries(data).map(([k,v]) => `${k}: ${Array.isArray(v)?v.join(', '):String(v)}`).join('\n')
      }
      setPwMsg(msg)
    } finally {
      setPwSaving(false)
    }
  }

  const onAvatarSelected = (e) => {
    setAvatarMsg('')
    const file = e.target.files?.[0]
    if (file) {
      setAvatarPreview(URL.createObjectURL(file))
    } else {
      setAvatarPreview(null)
    }
  }

  const uploadAvatar = async (e) => {
    e.preventDefault()
    const file = document.getElementById('avatar_file').files?.[0]
    if (!file) {
      setAvatarMsg('Please choose an image file')
      return
    }
    const fd = new FormData()
    fd.append('profile_picture', file)
    try {
      await axios.post('http://localhost:8000/api/users/me/avatar/', fd, { headers: { 'Content-Type': 'multipart/form-data' }})
      setAvatarMsg('Profile picture updated')
    } catch (error) {
      const data = error.response?.data
      setAvatarMsg(typeof data === 'string' ? data : 'Failed to upload')
    }
  }

  const removeAvatar = async () => {
    try {
      await axios.delete('http://localhost:8000/api/users/me/avatar/')
      setAvatarMsg('Profile picture removed')
      setAvatarPreview(null)
    } catch (error) {
      setAvatarMsg('Failed to remove')
    }
  }

  if (loading) {
    return (
      <div className="page">
        <h1>Profile</h1>
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div className="page">
      <h1>Profile</h1>
      {message && <div className="error-message" style={{ whiteSpace: 'pre-wrap' }}>{message}</div>}
      <form onSubmit={save} style={{ maxWidth: 480 }}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="first_name">First name</label>
            <input id="first_name" value={form.first_name} onChange={(e)=>setForm({ ...form, first_name: e.target.value })} />
          </div>
          <div className="form-group">
            <label htmlFor="last_name">Last name</label>
            <input id="last_name" value={form.last_name} onChange={(e)=>setForm({ ...form, last_name: e.target.value })} />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="phone_number">Phone number</label>
          <input id="phone_number" value={form.phone_number} onChange={(e)=>setForm({ ...form, phone_number: e.target.value })} />
        </div>
        <div className="form-group">
          <label htmlFor="address">Address</label>
          <input id="address" value={form.address} onChange={(e)=>setForm({ ...form, address: e.target.value })} />
        </div>
        <button type="submit" className="register-btn" disabled={saving}>{saving ? 'Saving...' : 'Save changes'}</button>
      </form>

      <div style={{ height: 24 }}></div>
      <h2 style={{ marginBottom: 8 }}>Change password</h2>
      {pwMsg && <div className="error-message" style={{ whiteSpace: 'pre-wrap' }}>{pwMsg}</div>}
      <form onSubmit={changePassword} style={{ maxWidth: 480 }}>
        <div className="form-group">
          <label htmlFor="current_password">Current password</label>
          <input id="current_password" name="current_password" type="password" required />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="new_password">New password</label>
            <input id="new_password" name="new_password" type="password" required />
          </div>
          <div className="form-group">
            <label htmlFor="confirm_password">Confirm</label>
            <input id="confirm_password" name="confirm_password" type="password" required />
          </div>
        </div>
        <button type="submit" className="register-btn" disabled={pwSaving}>{pwSaving ? 'Saving...' : 'Change password'}</button>
      </form>

      <div style={{ height: 24 }}></div>
      <h2 style={{ marginBottom: 8 }}>Profile picture</h2>
      {avatarMsg && <div className="error-message" style={{ whiteSpace: 'pre-wrap' }}>{avatarMsg}</div>}
      <form onSubmit={uploadAvatar} style={{ maxWidth: 480 }}>
        <div className="form-group">
          <label htmlFor="avatar_file">Choose image</label>
          <input id="avatar_file" name="avatar_file" type="file" accept="image/*" onChange={onAvatarSelected} />
        </div>
        {avatarPreview && (
          <div className="form-group">
            <img src={avatarPreview} alt="Preview" style={{ maxWidth: 160, borderRadius: 8 }} />
          </div>
        )}
        <div className="form-row">
          <button type="submit" className="register-btn">Upload</button>
          <button type="button" className="register-btn" onClick={removeAvatar}>Remove</button>
        </div>
      </form>
    </div>
  )
}

export default Profile



