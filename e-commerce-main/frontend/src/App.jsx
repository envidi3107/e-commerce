import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import ChatBot from './components/ChatBot'
import { useAuthStore } from './store'

// Pages (lazy-loaded for performance)
import { lazy, Suspense } from 'react'

const HomePage       = lazy(() => import('./pages/HomePage'))
const ProductsPage   = lazy(() => import('./pages/ProductsPage'))
const ProductDetail  = lazy(() => import('./pages/ProductDetail'))
const CartPage       = lazy(() => import('./pages/CartPage'))
const CheckoutPage   = lazy(() => import('./pages/CheckoutPage'))
const OrdersPage     = lazy(() => import('./pages/OrdersPage'))
const OrderDetail    = lazy(() => import('./pages/OrderDetail'))
const LoginPage      = lazy(() => import('./pages/LoginPage'))
const RegisterPage   = lazy(() => import('./pages/RegisterPage'))
const ProfilePage    = lazy(() => import('./pages/ProfilePage'))
const AdminPage      = lazy(() => import('./pages/AdminPage'))
const NotFound       = lazy(() => import('./pages/NotFound'))

function PrivateRoute({ children }) {
  const token = useAuthStore(s => s.token)
  return token ? children : <Navigate to="/login" replace />
}

function StaffRoute({ children }) {
  const token = useAuthStore(s => s.token)
  const user = useAuthStore(s => s.user)
  if (!token) return <Navigate to="/login" replace />
  if (!['admin', 'staff'].includes(user?.role)) return <Navigate to="/" replace />
  return children
}

function GuestRoute({ children }) {
  const token = useAuthStore(s => s.token)
  return token ? <Navigate to="/" replace /> : children
}

function LoadingFallback() {
  return (
    <div className="loading-center" style={{ height: '60vh' }}>
      <div className="spinner" />
    </div>
  )
}

export default function App() {
  return (
    <>
      <Navbar />
      <ChatBot />
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* Public */}
          <Route path="/"             element={<HomePage />} />
          <Route path="/products"     element={<ProductsPage />} />
          <Route path="/products/:id" element={<ProductDetail />} />

          {/* Guest only */}
          <Route path="/login"    element={<GuestRoute><LoginPage /></GuestRoute>} />
          <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />

          {/* Authenticated */}
          <Route path="/cart"         element={<PrivateRoute><CartPage /></PrivateRoute>} />
          <Route path="/checkout"     element={<PrivateRoute><CheckoutPage /></PrivateRoute>} />
          <Route path="/orders"       element={<PrivateRoute><OrdersPage /></PrivateRoute>} />
          <Route path="/orders/:id"   element={<PrivateRoute><OrderDetail /></PrivateRoute>} />
          <Route path="/profile"      element={<PrivateRoute><ProfilePage /></PrivateRoute>} />

          {/* Staff/Admin */}
          <Route path="/admin/*" element={<StaffRoute><AdminPage /></StaffRoute>} />

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </>
  )
}
