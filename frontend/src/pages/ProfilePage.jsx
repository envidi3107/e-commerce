import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { User, Shield, Lock } from 'lucide-react'
import toast from 'react-hot-toast'
import { authApi } from '../api'
import { useAuthStore } from '../store'

export default function ProfilePage() {
  const { user, setUser } = useAuthStore()
  const queryClient = useQueryClient()
  
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    address: ''
  })
  
  const [pwdData, setPwdData] = useState({
    old_password: '',
    new_password: ''
  })

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name:  user.last_name || '',
        phone:      user.phone || '',
        address:    user.address || ''
      })
    }
  }, [user])

  const updateMut = useMutation({
    mutationFn: (d) => authApi.updateProfile(d),
    onSuccess: (res) => {
      setUser(res.data)
      toast.success('Đã cập nhật thông tin')
    },
    onError: () => toast.error('Cập nhật thất bại')
  })

  const pwdMut = useMutation({
    mutationFn: (d) => authApi.changePassword(d),
    onSuccess: () => {
      toast.success('Đã đổi mật khẩu')
      setPwdData({ old_password: '', new_password: '' })
    },
    onError: (err) => {
      toast.error(err.response?.data?.old_password?.[0] || 'Đổi mật khẩu thất bại')
    }
  })

  return (
    <div className="page container fade-in">
      <h1 className="mb-4" style={{ fontSize: '2rem', fontWeight: 800 }}>Tài khoản của tôi</h1>

      <div className="grid-5" style={{ gridTemplateColumns: '1fr 350px' }}>
        
        {/* Profile Info */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4 pb-4 border-b" style={{ borderBottom: '1px solid var(--border)' }}>
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'var(--grad-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>
              {user?.first_name?.[0] || user?.email?.[0] || 'U'}
            </div>
            <div>
              <h2 className="font-bold text-lg">{user?.first_name} {user?.last_name}</h2>
              <div className="text-muted text-sm">{user?.email}</div>
              <div className="mt-1">
                <span className={`badge badge-${user?.role === 'admin' ? 'danger' : (user?.role === 'staff' ? 'warning' : 'primary')}`}>
                  {user?.role?.toUpperCase() || 'CUSTOMER'}
                </span>
              </div>
            </div>
          </div>

          <form onSubmit={e => { e.preventDefault(); updateMut.mutate(formData); }}>
            <h3 className="mb-3 flex items-center gap-2"><User size={18} /> Thông tin cá nhân</h3>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Họ</label>
                <input value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} required />
              </div>
              <div className="form-group">
                <label className="form-label">Tên</label>
                <input value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} required />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Số điện thoại</label>
              <input value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Địa chỉ</label>
              <textarea value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} rows="3" />
            </div>
            <button type="submit" className="btn btn-primary mt-2" disabled={updateMut.isPending}>
              {updateMut.isPending ? 'Đang lưu...' : 'Lưu thay đổi'}
            </button>
          </form>
        </div>

        {/* Security */}
        <div className="card" style={{ alignSelf: 'start' }}>
          <form onSubmit={e => { e.preventDefault(); pwdMut.mutate(pwdData); }}>
            <h3 className="mb-3 flex items-center gap-2"><Shield size={18} /> Đổi mật khẩu</h3>
            <div className="form-group">
              <label className="form-label">Mật khẩu hiện tại</label>
              <input type="password" value={pwdData.old_password} onChange={e => setPwdData({...pwdData, old_password: e.target.value})} required />
            </div>
            <div className="form-group mb-4">
              <label className="form-label">Mật khẩu mới</label>
              <input type="password" value={pwdData.new_password} onChange={e => setPwdData({...pwdData, new_password: e.target.value})} required minLength="6" />
            </div>
            <button type="submit" className="btn btn-secondary w-full" style={{ width: '100%', justifyContent: 'center' }} disabled={pwdMut.isPending}>
              <Lock size={16} /> {pwdMut.isPending ? 'Đang đổi...' : 'Đổi mật khẩu'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
