import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { authApi } from '../api'
import { useAuthStore } from '../store'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  const login = useAuthStore(s => s.login)
  const queryClient = useQueryClient()

  const loginMut = useMutation({
    mutationFn: (data) => authApi.login(data),
    onSuccess: (res) => {
      const { user, tokens } = res.data
      login(user, tokens)
      queryClient.invalidateQueries(['cart'])
      toast.success('Đăng nhập thành công')
      navigate('/')
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Email hoặc mật khẩu không đúng')
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    loginMut.mutate({ email, password })
  }

  return (
    <div className="page container flex-center fade-in">
      <div className="card" style={{ width: '100%', maxWidth: '400px', padding: '2rem' }}>
        <h1 className="text-center mb-4" style={{ fontSize: '1.75rem', fontWeight: 800 }}>Đăng nhập</h1>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              name='email'
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Nhập email của bạn"
            />
          </div>
          <div className="form-group mb-4">
            <label className="form-label">Mật khẩu</label>
            <input
              name='password'
              type="password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full"
            style={{ width: '100%', justifyContent: 'center' }}
            disabled={loginMut.isPending}
          >
            {loginMut.isPending ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>

        <div className="text-center mt-4 text-sm text-muted">
          Chưa có tài khoản? <Link to="/register" className="text-primary-light font-medium">Đăng ký ngay</Link>
        </div>
      </div>
    </div>
  )
}
