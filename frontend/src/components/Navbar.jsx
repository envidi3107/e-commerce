import { Link, useNavigate, useLocation } from 'react-router-dom'
import { ShoppingCart, Search, User, LogOut, Package, LayoutDashboard, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore, useCartStore } from '../store'
import { authApi } from '../api'
import toast from 'react-hot-toast'
import './Navbar.css'

export default function Navbar() {
  const user = useAuthStore(s => s.user)
  const token = useAuthStore(s => s.token)
  const logout = useAuthStore(s => s.logout)
  const isAuthenticated = !!token
  const isStaff = ['admin', 'staff'].includes(user?.role)
  const totalItems = useCartStore(s => s.totalItems())
  const navigate   = useNavigate()
  const location   = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [searchQ, setSearchQ]   = useState('')

  const handleLogout = async () => {
    const refresh = localStorage.getItem('refresh_token')
    try { await authApi.logout(refresh) } catch {}
    logout()
    toast.success('Đã đăng xuất')
    navigate('/')
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQ.trim()) navigate(`/products?search=${encodeURIComponent(searchQ.trim())}`)
  }

  const navLinks = [
    { to: '/',          label: 'Trang chủ' },
    { to: '/products',  label: 'Sản phẩm' },
  ]

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">ShopVN</span>
        </Link>

        {/* Search */}
        <form className="navbar-search" onSubmit={handleSearch}>
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Tìm kiếm sản phẩm..."
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
          />
        </form>

        {/* Nav links (desktop) */}
        <div className="navbar-links">
          {navLinks.map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={`nav-link ${location.pathname === l.to ? 'active' : ''}`}
            >
              {l.label}
            </Link>
          ))}
        </div>

        {/* Right actions */}
        <div className="navbar-actions">
          {isAuthenticated ? (
            <>
              {/* Cart */}
              <Link to="/cart" className="nav-icon-btn cart-btn">
                <ShoppingCart size={20} />
                {totalItems > 0 && (
                  <span className="cart-badge">{totalItems}</span>
                )}
              </Link>

              {/* Orders */}
              <Link to="/orders" className="nav-icon-btn" title="Đơn hàng">
                <Package size={20} />
              </Link>

              {/* Admin */}
              {isStaff && (
                <Link to="/admin" className="nav-icon-btn" title="Quản trị">
                  <LayoutDashboard size={20} />
                </Link>
              )}

              {/* User menu */}
              <div className="user-menu">
                <button className="user-btn">
                  <div className="user-avatar">
                    {user?.first_name?.[0] || user?.email?.[0] || 'U'}
                  </div>
                  <span className="user-name">{user?.first_name || user?.email?.split('@')[0]}</span>
                </button>
                <div className="user-dropdown">
                  <Link to="/profile" className="dropdown-item">
                    <User size={15} /> Profile
                  </Link>
                  <button onClick={handleLogout} className="dropdown-item danger">
                    <LogOut size={15} /> Đăng xuất
                  </button>
                </div>
              </div>
            </>
          ) : (
            <>
              <Link to="/login"    className="btn btn-secondary btn-sm">Đăng nhập</Link>
              <Link to="/register" className="btn btn-primary  btn-sm">Đăng ký</Link>
            </>
          )}

          {/* Mobile toggle */}
          <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="mobile-menu">
          {navLinks.map(l => (
            <Link key={l.to} to={l.to} className="mobile-link" onClick={() => setMenuOpen(false)}>
              {l.label}
            </Link>
          ))}
          {!isAuthenticated && (
            <>
              <Link to="/login"    className="mobile-link" onClick={() => setMenuOpen(false)}>Đăng nhập</Link>
              <Link to="/register" className="mobile-link" onClick={() => setMenuOpen(false)}>Đăng ký</Link>
            </>
          )}
        </div>
      )}
    </nav>
  )
}
