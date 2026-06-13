import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ShoppingCart } from 'lucide-react'
import toast from 'react-hot-toast'
import { productApi, cartApi } from '../api'
import { useAuthStore } from '../store'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isAuthenticated = useAuthStore(s => s.isAuthenticated())
  const [qty, setQty] = useState(1)

  const { data: p, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => productApi.detail(id).then(res => res.data)
  })

  const { data: recs } = useQuery({
    queryKey: ['recommendations', id],
    queryFn: () => fetch(`/api/recommendations/${id}/`).then(res => res.json()).catch(() => null),
    enabled: !!p
  })

  const addToCartMut = useMutation({
    mutationFn: (data) => cartApi.addItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['cart'])
      toast.success('Đã thêm vào giỏ hàng')
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Lỗi khi thêm vào giỏ hàng')
    }
  })

  const handleAddToCart = () => {
    if (!isAuthenticated) {
      toast.error('Vui lòng đăng nhập để mua hàng')
      navigate('/login')
      return
    }
    addToCartMut.mutate({ product_id: p.id, quantity: qty })
  }

  if (isLoading) return <div className="loading-center"><div className="spinner" /></div>
  if (!p) return <div className="empty-state container page"><h3>Sản phẩm không tồn tại</h3></div>

  const isOutOfStock = p.inventory?.available <= 0

  return (
    <div className="page container">
      <div className="grid-2 card fade-in">
        {/* Images */}
        <div style={{ background: 'var(--bg-2)', borderRadius: '12px', padding: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
          {p.thumbnail ? (
            <img src={p.thumbnail} alt={p.name} style={{ maxHeight: '400px', objectFit: 'contain' }} />
          ) : (
            <span className="text-muted">No Image</span>
          )}
        </div>

        {/* Info */}
        <div className="flex" style={{ flexDirection: 'column' }}>
          <div className="mb-2">
            <span className="badge badge-primary mb-1">{p.category_name}</span>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, lineHeight: 1.2 }}>{p.name}</h1>
            <p className="text-muted mt-1 text-sm">SKU: {p.sku}</p>
          </div>

          <div className="mb-3 flex items-center gap-2">
            <span className="price" style={{ fontSize: '1.75rem' }}>${p.price}</span>
            {p.compare_price && <span className="price-old">${p.compare_price}</span>}
          </div>

          <p className="mb-3 text-muted" style={{ lineHeight: 1.8 }}>
            {p.description || 'Chưa có mô tả cho sản phẩm này.'}
          </p>

          {/* Attributes */}
          {p.attributes && Object.keys(p.attributes).length > 0 && (
            <div className="mb-4 p-3" style={{ background: 'var(--bg-2)', borderRadius: '8px' }}>
              <h4 className="mb-2 text-sm text-muted uppercase">Thông số kỹ thuật</h4>
              <div className="grid-2 gap-1 text-sm">
                {Object.entries(p.attributes).map(([k, v]) => (
                  <div key={k} className="flex">
                    <span className="text-muted" style={{ width: '100px', textTransform: 'capitalize' }}>{k}:</span>
                    <span className="font-medium">{Array.isArray(v) ? v.join(', ') : v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-auto flex items-center gap-3">
             <div className="flex items-center" style={{ background: 'var(--bg-2)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden' }}>
               <button className="btn-secondary" style={{ padding: '0.625rem 1rem', border: 'none', borderRadius: 0 }} onClick={() => setQty(Math.max(1, qty - 1))} disabled={isOutOfStock}>-</button>
               <span style={{ width: '40px', textAlign: 'center', fontWeight: 600 }}>{qty}</span>
               <button className="btn-secondary" style={{ padding: '0.625rem 1rem', border: 'none', borderRadius: 0 }} onClick={() => setQty(qty + 1)} disabled={isOutOfStock}>+</button>
             </div>
             
             <button 
               className="btn btn-primary btn-lg" 
               style={{ flex: 1 }}
               onClick={handleAddToCart}
               disabled={isOutOfStock || addToCartMut.isPending}
             >
               <ShoppingCart size={20} />
               {isOutOfStock ? 'Hết hàng' : (addToCartMut.isPending ? 'Đang thêm...' : 'Thêm vào giỏ')}
             </button>
          </div>
          <div className="mt-2 text-sm text-center">
             {isOutOfStock ? (
                <span className="text-danger font-medium">Sản phẩm hiện đang hết hàng</span>
             ) : (
                <span className="text-muted">Còn lại {p.inventory?.available} sản phẩm trong kho</span>
             )}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {recs?.recommendations?.length > 0 && (
        <div className="mt-4">
          <h2 className="mb-2" style={{ fontSize: '1.5rem', fontWeight: 700 }}>Sản phẩm tương tự</h2>
          <div className="grid-4">
            {recs.recommendations.map(rp => (
               <div key={rp.id} className="card fade-in" style={{ padding: '1rem', cursor: 'pointer' }} onClick={() => { navigate(`/products/${rp.id}`); window.scrollTo(0,0) }}>
                 <div style={{ background: 'var(--bg-2)', borderRadius: '8px', padding: '1rem', marginBottom: '1rem', height: '150px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {rp.thumbnail ? <img src={rp.thumbnail} alt={rp.name} style={{ maxHeight: '100%', objectFit: 'contain' }} /> : <span className="text-xs text-muted">No Image</span>}
                 </div>
                 <h4 className="truncate text-sm mb-1">{rp.name}</h4>
                 <div className="price text-sm">${rp.price}</div>
               </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
