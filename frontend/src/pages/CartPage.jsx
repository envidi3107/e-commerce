import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { Trash2, ArrowRight, Minus, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import { cartApi } from '../api'
import { useCartStore } from '../store'
import { useEffect } from 'react'

export default function CartPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const setCart = useCartStore(s => s.setCart)

  const { data: cart, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: () => cartApi.get().then(res => res.data)
  })

  // Sync to zustand store for badge
  useEffect(() => {
    if (cart) setCart(cart)
  }, [cart, setCart])

  const updateMut = useMutation({
    mutationFn: ({ id, qty }) => cartApi.updateItem(id, { quantity: qty }),
    onSuccess: () => queryClient.invalidateQueries(['cart']),
    onError: () => toast.error('Lỗi cập nhật giỏ hàng')
  })

  const removeMut = useMutation({
    mutationFn: (id) => cartApi.removeItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['cart'])
      toast.success('Đã xóa sản phẩm')
    }
  })

  const clearMut = useMutation({
    mutationFn: () => cartApi.clear(),
    onSuccess: () => {
      queryClient.invalidateQueries(['cart'])
      setCart(null)
      toast.success('Đã làm trống giỏ hàng')
    }
  })

  if (isLoading) return <div className="loading-center"><div className="spinner" /></div>

  if (!cart || !cart.items || cart.items.length === 0) {
    return (
      <div className="page container">
        <div className="card empty-state fade-in">
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🛒</div>
          <h2>Giỏ hàng trống</h2>
          <p className="text-muted mb-3 mt-1">Bạn chưa thêm sản phẩm nào vào giỏ hàng.</p>
          <Link to="/products" className="btn btn-primary">Mua sắm ngay</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page container fade-in">
      <h1 className="mb-3" style={{ fontSize: '2rem', fontWeight: 800 }}>Giỏ hàng của bạn</h1>
      
      <div className="grid-5" style={{ gridTemplateColumns: '1fr 350px' }}>
        {/* Cart Items */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-wrap" style={{ border: 'none', borderRadius: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Sản phẩm</th>
                  <th style={{ width: '120px', textAlign: 'center' }}>Đơn giá</th>
                  <th style={{ width: '150px', textAlign: 'center' }}>Số lượng</th>
                  <th style={{ width: '120px', textAlign: 'right' }}>Tổng</th>
                  <th style={{ width: '60px' }}></th>
                </tr>
              </thead>
              <tbody>
                {cart.items.map(item => (
                  <tr key={item.id}>
                    <td>
                      <div className="flex items-center gap-2">
                        <div style={{ width: '60px', height: '60px', background: 'var(--bg-2)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          {item.product_thumbnail ? (
                            <img src={item.product_thumbnail} alt={item.product_name} style={{ maxHeight: '100%', objectFit: 'contain' }} />
                          ) : (
                            <span className="text-xs text-muted">No IMG</span>
                          )}
                        </div>
                        <Link to={`/products/${item.product_id}`} className="font-medium hover:text-primary transition-colors">
                          {item.product_name}
                        </Link>
                      </div>
                    </td>
                    <td className="text-center font-medium">${item.product_price}</td>
                    <td>
                      <div className="flex items-center justify-center" style={{ background: 'var(--bg-2)', borderRadius: '6px', border: '1px solid var(--border)' }}>
                        <button 
                          className="btn-secondary" 
                          style={{ padding: '0.4rem 0.6rem', border: 'none', borderRadius: 0 }}
                          onClick={() => updateMut.mutate({ id: item.id, qty: item.quantity - 1 })}
                          disabled={item.quantity <= 1 || updateMut.isPending}
                        >
                          <Minus size={14} />
                        </button>
                        <span style={{ width: '30px', textAlign: 'center', fontSize: '0.9rem', fontWeight: 600 }}>{item.quantity}</span>
                        <button 
                          className="btn-secondary" 
                          style={{ padding: '0.4rem 0.6rem', border: 'none', borderRadius: 0 }}
                          onClick={() => updateMut.mutate({ id: item.id, qty: item.quantity + 1 })}
                          disabled={updateMut.isPending}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                    </td>
                    <td className="text-right font-bold text-primary-light">${item.item_price}</td>
                    <td className="text-right">
                      <button 
                        className="btn-secondary text-danger hover:bg-danger hover:text-white"
                        style={{ padding: '0.5rem', borderRadius: '6px' }}
                        onClick={() => removeMut.mutate(item.id)}
                        title="Xóa"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="p-3" style={{ borderTop: '1px solid var(--border)', background: 'var(--bg-card)' }}>
            <button 
               className="btn btn-secondary text-danger text-sm" 
               onClick={() => { if(window.confirm('Xóa toàn bộ giỏ hàng?')) clearMut.mutate() }}
            >
              Làm trống giỏ hàng
            </button>
          </div>
        </div>

        {/* Summary */}
        <div className="card" style={{ alignSelf: 'start', position: 'sticky', top: '80px' }}>
          <h3 className="mb-3">Tổng đơn hàng</h3>
          <div className="flex-between mb-2 text-sm text-muted">
            <span>Tạm tính ({cart.total_items} sp):</span>
            <span className="font-medium text-text">${cart.total_price}</span>
          </div>
          <div className="flex-between mb-3 text-sm text-muted">
            <span>Phí giao hàng:</span>
            <span>Chưa tính</span>
          </div>
          <div className="divider" style={{ margin: '1rem 0' }} />
          <div className="flex-between mb-4">
            <span className="font-bold">Tổng cộng:</span>
            <span className="price">${cart.total_price}</span>
          </div>
          <button 
            className="btn btn-primary w-full" 
            style={{ width: '100%', justifyContent: 'center' }}
            onClick={() => navigate('/checkout')}
          >
            Tiến hành đặt hàng <ArrowRight size={18} />
          </button>
          <div className="text-center mt-3">
             <Link to="/products" className="text-sm text-muted hover:text-primary">Tiếp tục mua sắm</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
