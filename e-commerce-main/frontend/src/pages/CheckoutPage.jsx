import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { cartApi, orderApi } from '../api'

export default function CheckoutPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [formData, setFormData] = useState({
    payment_method: 'cod',
    shipping_address: {
      fullname: '',
      phone: '',
      address: '',
      city: ''
    },
    notes: ''
  })

  const { data: cart, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: () => cartApi.get().then(res => res.data)
  })

  const checkoutMut = useMutation({
    mutationFn: (data) => orderApi.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries(['cart'])
      queryClient.invalidateQueries(['orders'])
      toast.success('Đặt hàng thành công!')
      navigate(`/orders/${res.data.id}`)
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Lỗi khi đặt hàng')
    }
  })

  if (isLoading) return <div className="loading-center"><div className="spinner" /></div>
  if (!cart || cart.items.length === 0) {
    return <Navigate to="/cart" replace />
  }

  const shippingFee = 5.00
  const total = parseFloat(cart.total_price) + shippingFee

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.shipping_address.fullname || !formData.shipping_address.phone || !formData.shipping_address.address || !formData.shipping_address.city) {
      toast.error('Vui lòng điền đầy đủ thông tin giao hàng')
      return
    }
    
    checkoutMut.mutate({
      payment_method: formData.payment_method,
      shipping_address: formData.shipping_address,
      notes: formData.notes,
      shipping_fee: shippingFee,
      discount: 0
    })
  }

  const handleAddrChange = (e) => {
    setFormData(prev => ({
      ...prev,
      shipping_address: { ...prev.shipping_address, [e.target.name]: e.target.value }
    }))
  }

  return (
    <div className="page container fade-in">
      <h1 className="mb-4" style={{ fontSize: '2rem', fontWeight: 800 }}>Thanh toán</h1>
      
      <form onSubmit={handleSubmit} className="grid-5" style={{ gridTemplateColumns: '1fr 400px' }}>
        {/* Form Fields */}
        <div className="flex" style={{ flexDirection: 'column', gap: '1.5rem' }}>
          
          <div className="card">
            <h3 className="mb-3 border-b pb-2" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem' }}>1. Thông tin giao hàng</h3>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Họ và tên</label>
                <input name="fullname" value={formData.shipping_address.fullname} onChange={handleAddrChange} required placeholder="VD: Nguyễn Văn A" />
              </div>
              <div className="form-group">
                <label className="form-label">Số điện thoại</label>
                <input name="phone" value={formData.shipping_address.phone} onChange={handleAddrChange} required placeholder="VD: 0912345678" />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Địa chỉ cụ thể (Số nhà, đường...)</label>
              <input name="address" value={formData.shipping_address.address} onChange={handleAddrChange} required placeholder="VD: 123 Đường ABC, Phường X" />
            </div>
            <div className="form-group mb-0">
              <label className="form-label">Tỉnh / Thành phố</label>
              <input name="city" value={formData.shipping_address.city} onChange={handleAddrChange} required placeholder="VD: Hà Nội" />
            </div>
          </div>

          <div className="card">
            <h3 className="mb-3 border-b pb-2" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem' }}>2. Phương thức thanh toán</h3>
            <div className="flex" style={{ flexDirection: 'column', gap: '0.75rem' }}>
              <label className="flex items-center gap-2" style={{ padding: '1rem', border: '1px solid var(--border)', borderRadius: '8px', cursor: 'pointer', background: formData.payment_method === 'cod' ? 'var(--glass-bg)' : 'transparent', borderColor: formData.payment_method === 'cod' ? 'var(--primary)' : 'var(--border)' }}>
                <input type="radio" name="payment" value="cod" checked={formData.payment_method === 'cod'} onChange={e => setFormData({...formData, payment_method: e.target.value})} style={{ width: 'auto' }} />
                <div>
                  <div className="font-medium">Thanh toán khi nhận hàng (COD)</div>
                  <div className="text-xs text-muted">Thanh toán bằng tiền mặt khi giao hàng</div>
                </div>
              </label>
              
              <label className="flex items-center gap-2" style={{ padding: '1rem', border: '1px solid var(--border)', borderRadius: '8px', cursor: 'pointer', background: formData.payment_method === 'bank' ? 'var(--glass-bg)' : 'transparent', borderColor: formData.payment_method === 'bank' ? 'var(--primary)' : 'var(--border)' }}>
                <input type="radio" name="payment" value="bank" checked={formData.payment_method === 'bank'} onChange={e => setFormData({...formData, payment_method: e.target.value})} style={{ width: 'auto' }} />
                <div>
                  <div className="font-medium">Chuyển khoản ngân hàng</div>
                  <div className="text-xs text-muted">Chuyển khoản trực tiếp tới tài khoản của chúng tôi</div>
                </div>
              </label>

              <label className="flex items-center gap-2" style={{ padding: '1rem', border: '1px solid var(--border)', borderRadius: '8px', cursor: 'pointer', background: formData.payment_method === 'ewallet' ? 'var(--glass-bg)' : 'transparent', borderColor: formData.payment_method === 'ewallet' ? 'var(--primary)' : 'var(--border)' }}>
                <input type="radio" name="payment" value="ewallet" checked={formData.payment_method === 'ewallet'} onChange={e => setFormData({...formData, payment_method: e.target.value})} style={{ width: 'auto' }} />
                <div>
                  <div className="font-medium">Ví điện tử (Momo / ZaloPay)</div>
                  <div className="text-xs text-muted">Thanh toán qua cổng ví điện tử</div>
                </div>
              </label>
            </div>
          </div>

          <div className="card">
            <h3 className="mb-3 border-b pb-2" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem' }}>3. Ghi chú đơn hàng</h3>
            <div className="form-group mb-0">
              <textarea 
                rows="3" 
                placeholder="Ghi chú về giao hàng, thời gian nhận..." 
                value={formData.notes} 
                onChange={e => setFormData({...formData, notes: e.target.value})}
              />
            </div>
          </div>

        </div>

        {/* Order Summary Sidebar */}
        <div className="card" style={{ alignSelf: 'start', position: 'sticky', top: '80px' }}>
          <h3 className="mb-3">Tóm tắt đơn hàng</h3>
          
          <div className="mb-3" style={{ maxHeight: '250px', overflowY: 'auto' }}>
            {cart.items.map(item => (
              <div key={item.id} className="flex gap-2 mb-2 pb-2" style={{ borderBottom: '1px dashed var(--border)' }}>
                <div style={{ width: '40px', height: '40px', background: 'var(--bg-2)', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyItems: 'center', overflow: 'hidden' }}>
                  {item.product_thumbnail ? <img src={item.product_thumbnail} alt="" /> : <span className="text-xs text-muted p-1">IMG</span>}
                </div>
                <div style={{ flex: 1 }}>
                  <div className="text-sm font-medium truncate" style={{ maxWidth: '200px' }}>{item.product_name}</div>
                  <div className="text-xs text-muted">{item.quantity} x ${item.product_price}</div>
                </div>
                <div className="text-sm font-bold">${item.item_price}</div>
              </div>
            ))}
          </div>

          <div className="flex-between mb-2 text-sm text-muted">
            <span>Tạm tính:</span>
            <span className="font-medium text-text">${cart.total_price}</span>
          </div>
          <div className="flex-between mb-3 text-sm text-muted">
            <span>Phí giao hàng:</span>
            <span className="font-medium text-text">${shippingFee.toFixed(2)}</span>
          </div>
          <div className="divider" style={{ margin: '1rem 0' }} />
          <div className="flex-between mb-4">
            <span className="font-bold text-lg">Tổng cộng:</span>
            <span className="price text-lg">${total.toFixed(2)}</span>
          </div>
          
          <button 
            type="submit"
            className="btn btn-primary w-full" 
            style={{ width: '100%', justifyContent: 'center' }}
            disabled={checkoutMut.isPending}
          >
            {checkoutMut.isPending ? 'Đang xử lý...' : 'Xác nhận Đặt hàng'}
          </button>
          <div className="text-center mt-3">
             <Link to="/cart" className="text-sm text-muted hover:text-primary">&larr; Quay lại giỏ hàng</Link>
          </div>
        </div>
      </form>
    </div>
  )
}
