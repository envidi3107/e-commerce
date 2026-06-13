import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true

      // Check if the token used in the failed request is still the current one.
      // If a new login happened in the meantime, the stored token differs from
      // what was used in this request – just retry with the fresh token.
      const currentToken = localStorage.getItem('access_token')
      const usedToken = original.headers?.Authorization?.replace('Bearer ', '')

      if (currentToken && currentToken !== usedToken) {
        // A newer token exists (e.g. user just logged in). Retry with it.
        original.headers.Authorization = `Bearer ${currentToken}`
        return api(original)
      }

      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post('/api/auth/token/refresh/', { refresh })
          localStorage.setItem('access_token', data.access)
          if (data.refresh) {
            localStorage.setItem('refresh_token', data.refresh)
          }
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          // Also clear zustand persisted auth state to keep UI in sync
          try { localStorage.removeItem('auth-store') } catch {}
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)


export default api

// ── Auth ──────────────────────────────────
export const authApi = {
  register: (d)        => api.post('/auth/register/', d),
  login:    (d)        => api.post('/auth/login/', d),
  logout:   (refresh)  => api.post('/auth/logout/', { refresh }),
  profile:  ()         => api.get('/users/profile/'),
  updateProfile: (d)   => api.put('/users/profile/', d),
  changePassword: (d)  => api.post('/auth/change-password/', d),
}

// ── Products ──────────────────────────────
export const productApi = {
  list:       (params) => api.get('/products/', { params }),
  detail:     (id)     => api.get(`/products/${id}/`),
  create:     (d)      => api.post('/products/', d),
  update:     (id, d)  => api.put(`/products/${id}/`, d),
  delete:     (id)     => api.delete(`/products/${id}/`),
  categories: ()       => api.get('/categories/'),
  inventory:  (id)     => api.get(`/inventory/${id}/`),
  updateInventory: (id, d) => api.put(`/inventory/${id}/`, d),
}

// ── Cart ──────────────────────────────────
export const cartApi = {
  get:        ()       => api.get('/cart/'),
  addItem:    (d)      => api.post('/cart/items/', d),
  updateItem: (id, d)  => api.put(`/cart/items/${id}/`, d),
  removeItem: (id)     => api.delete(`/cart/items/${id}/`),
  clear:      ()       => api.delete('/cart/'),
}

// ── Orders ────────────────────────────────
export const orderApi = {
  list:         (params) => api.get('/orders/', { params }),
  detail:       (id)     => api.get(`/orders/${id}/`),
  create:       (d)      => api.post('/orders/', d),
  cancel:       (id)     => api.delete(`/orders/${id}/`),
  updateStatus: (id, d)  => api.put(`/orders/${id}/status/`, d),
}

// ── Payments ──────────────────────────────
export const paymentApi = {
  list:    (params) => api.get('/payments/', { params }),
  detail:  (id)     => api.get(`/payments/${id}/`),
  process: (id, d)  => api.post(`/payments/${id}/process/`, d),
  refund:  (id, d)  => api.post(`/payments/${id}/refund/`, d),
}

// ── Shipping ──────────────────────────────
export const shippingApi = {
  list:     (params) => api.get('/shipping/', { params }),
  detail:   (id)     => api.get(`/shipping/${id}/`),
  tracking: (id)     => api.get(`/shipping/${id}/tracking/`),
  updateStatus: (id, d) => api.put(`/shipping/${id}/status/`, d),
}

// ── Search / AI ───────────────────────────
export const searchApi = {
  search:  (params) => api.get('/search/', { params }),
  recommend: (id)   => api.get(`/recommendations/${id}/`),
  trending: (params) => api.get('/trending/', { params }),
}

// ── AI Chatbot ────────────────────────────
export const chatApi = {
  send: (query) => api.post('/chatbot/', { query }),
}

// ── Admin ─────────────────────────────────
export const adminApi = {
  users:        (params) => api.get('/users/', { params }),
  userDetail:   (id)     => api.get(`/users/${id}/`),
  createUser:   (d)      => api.post('/users/', d),
  updateUser:   (id, d)  => api.put(`/users/${id}/`, d),
  deleteUser:   (id)     => api.delete(`/users/${id}/`),
}
