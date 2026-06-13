import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user:  null,
      token: null,

      login: (user, tokens) => {
        localStorage.setItem('access_token',  tokens.access)
        localStorage.setItem('refresh_token', tokens.refresh)
        set({ user, token: tokens.access })
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, token: null })
      },

      setUser: (user) => set({ user }),

      isAuthenticated: () => !!get().token,
      isAdmin:         () => get().user?.role === 'admin',
      isStaff:         () => ['admin','staff'].includes(get().user?.role),
    }),
    { name: 'auth-store', partialize: (s) => ({ user: s.user, token: s.token }) }
  )
)

export const useCartStore = create((set, get) => ({
  cart: null,
  setCart: (cart) => set({ cart }),
  totalItems: () => get().cart?.total_items ?? 0,
  totalPrice: () => get().cart?.total_price ?? 0,
}))
