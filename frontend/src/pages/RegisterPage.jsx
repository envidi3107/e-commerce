import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { authApi } from '../api'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    phone: '',
  })

  const registerMut = useMutation({
    mutationFn: (data) => authApi.register(data),
    onSuccess: () => {
      toast.success('Đăng ký thành công! Vui lòng đăng nhập.')
      navigate('/login')
    },
    onError: (err) => {
      const data = err.response?.data
      if (data && typeof data === 'object') {
        const errors = Object.values(data).flat().join(', ')
        toast.error(errors || 'Đăng ký thất bại')
      } else {
        toast.error('Đăng ký thất bại')
      }
    }
  })

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (formData.password !== formData.password_confirm) {
      toast.error('Mật khẩu xác nhận không khớp')
      return
    }
    // Auto-generate username from email if empty
    const data = { ...formData }
    if (!data.username) {
      data.username = data.email.split('@')[0]
    }
    registerMut.mutate(data)
  }

  return (
    <div className="page container flex-center fade-in">
      <div className="card" style={{ width: '100%', maxWidth: '450px', padding: '2rem' }}>
        <h1 className="text-center mb-4" style={{ fontSize: '1.75rem', fontWeight: 800 }}>Đăng ký tài khoản</h1>
        
        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Họ</label>
              <input name="last_name" value={formData.last_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label className="form-label">Tên</label>
              <input name="first_name" value={formData.first_name} onChange={handleChange} required />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Email</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label className="form-label">Số điện thoại (tùy chọn)</label>
            <input name="phone" value={formData.phone} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label className="form-label">Mật khẩu</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} required minLength="8" placeholder="Tối thiểu 8 ký tự" />
          </div>

          <div className="form-group mb-4">
            <label className="form-label">Xác nhận mật khẩu</label>
            <input type="password" name="password_confirm" value={formData.password_confirm} onChange={handleChange} required minLength="8" placeholder="Nhập lại mật khẩu" />
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary w-full" 
            style={{ width: '100%', justifyContent: 'center' }}
            disabled={registerMut.isPending}
          >
            {registerMut.isPending ? 'Đang đăng ký...' : 'Đăng ký'}
          </button>
        </form>

        <div className="text-center mt-4 text-sm text-muted">
          Đã có tài khoản? <Link to="/login" className="text-primary-light font-medium">Đăng nhập</Link>
        </div>
      </div>
    </div>
  )
}
