import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Truck, CreditCard, PackageX } from 'lucide-react'
import toast from 'react-hot-toast'
import { orderApi, paymentApi, shippingApi } from '../api'

const STATUS_LABELS = {
  pending:    'Chờ xác nhận',
  confirmed:  'Đã xác nhận',
  processing: 'Đang xử lý',
  shipped:    'Đang giao hàng',
  delivered:  'Đã giao',
  cancelled:  'Đã hủy',
}

const STATUS_STEPS = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']

export default function OrderDetail() {
  const { id } = useParams()
  const queryClient = useQueryClient()

  const { data: order, isLoading } = useQuery({
    queryKey: ['order', id],
    queryFn: () => orderApi.detail(id).then(res => res.data)
  })

  // Fetch payment details if we have a payment_id
  const { data: payment } = useQuery({
    queryKey: ['payment', order?.payment_id],
    queryFn: () => paymentApi.detail(order.payment_id).then(res => res.data),
    enabled: !!order?.payment_id
  })

  // Fetch shipping/tracking if we have shipment_id
  const { data: shipment } = useQuery({
    queryKey: ['shipping', order?.shipment_id],
    queryFn: () => shippingApi.tracking(order.shipment_id).then(res => res.data),
    enabled: !!order?.shipment_id
  })

  const cancelMut = useMutation({
    mutationFn: () => orderApi.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['order', id])
      queryClient.invalidateQueries(['orders'])
      toast.success('Đã hủy đơn hàng')
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Không thể hủy đơn hàng lúc này')
  })

  const processPaymentMut = useMutation({
    mutationFn: () => paymentApi.process(order.payment_id, { bank_ref: 'MOCK_USER_PAY' }),
    onSuccess: () => {
      queryClient.invalidateQueries(['payment'])
      queryClient.invalidateQueries(['order'])
      toast.success('Thanh toán thành công (Mô phỏng)')
    },
    onError: () => toast.error('Lỗi thanh toán')
  })

  if (isLoading) return <div className="loading-center"><div className="spinner" /></div>
  if (!order) return <div className="empty-state container page"><h3>Không tìm thấy đơn hàng</h3></div>

  const currentStepIndex = STATUS_STEPS.indexOf(order.status)
  const isCancelled = order.status === 'cancelled'

  return (
    <div className="page container fade-in">
      <div className="mb-4">
        <Link to="/orders" className="text-sm text-muted hover:text-primary mb-2 inline-block">&larr; Quay lại Danh sách</Link>
        <div className="flex-between">
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Chi tiết Đơn hàng #{order.id}</h1>
          <span className={`badge badge-${isCancelled ? 'danger' : (order.status === 'delivered' ? 'success' : 'primary')}`} style={{ fontSize: '1rem', padding: '0.4rem 1rem' }}>
            {STATUS_LABELS[order.status] || order.status}
          </span>
        </div>
        <div className="text-muted mt-1">Ngày đặt: {new Date(order.created_at).toLocaleString('vi-VN')}</div>
      </div>

      {/* Progress Bar */}
      {!isCancelled && (
        <div className="card mb-4">
          <div className="flex-between relative" style={{ padding: '0 2rem' }}>
             <div style={{ position: 'absolute', top: '20px', left: '40px', right: '40px', height: '4px', background: 'var(--border)', zIndex: 0 }} />
             <div style={{ position: 'absolute', top: '20px', left: '40px', width: `${Math.max(0, currentStepIndex) / (STATUS_STEPS.length - 1) * 100}%`, height: '4px', background: 'var(--primary)', zIndex: 0, transition: 'width 0.5s' }} />
             
             {STATUS_STEPS.map((step, idx) => {
               const active = idx <= currentStepIndex
               return (
                 <div key={step} className="flex" style={{ flexDirection: 'column', alignItems: 'center', zIndex: 1, gap: '0.5rem' }}>
                   <div style={{ width: '44px', height: '44px', borderRadius: '50%', background: active ? 'var(--primary)' : 'var(--bg-card)', border: `2px solid ${active ? 'var(--primary-light)' : 'var(--border)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: active ? '#fff' : 'var(--text-muted)' }}>
                     <CheckCircle2 size={24} />
                   </div>
                   <div className={`text-xs font-medium ${active ? 'text-primary-light' : 'text-muted'}`}>{STATUS_LABELS[step]}</div>
                 </div>
               )
             })}
          </div>
        </div>
      )}

      <div className="grid-5" style={{ gridTemplateColumns: '1fr 350px' }}>
        <div className="flex" style={{ flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Items */}
          <div className="card">
            <h3 className="mb-3">Sản phẩm</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Sản phẩm</th>
                    <th className="text-center">Đơn giá</th>
                    <th className="text-center">SL</th>
                    <th className="text-right">Tổng</th>
                  </tr>
                </thead>
                <tbody>
                  {order.items.map(item => (
                    <tr key={item.id}>
                      <td>
                        <div className="flex items-center gap-2">
                          <div style={{ width: '50px', height: '50px', background: 'var(--bg-2)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            {item.product_thumbnail ? <img src={item.product_thumbnail} alt="" style={{ maxHeight: '100%', objectFit: 'contain' }} /> : <span className="text-xs text-muted">No IMG</span>}
                          </div>
                          <Link to={`/products/${item.product_id}`} className="font-medium hover:text-primary">
                            {item.product_name}
                          </Link>
                        </div>
                      </td>
                      <td className="text-center">${item.unit_price}</td>
                      <td className="text-center">{item.quantity}</td>
                      <td className="text-right font-bold text-primary-light">${(item.unit_price * item.quantity).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Tracking */}
          {shipment && shipment.events && shipment.events.length > 0 && (
            <div className="card">
              <h3 className="mb-3 flex items-center gap-2"><Truck size={20} className="text-primary" /> Hành trình vận chuyển</h3>
              <div className="text-sm mb-3">
                 <span className="text-muted">Đơn vị vận chuyển:</span> <span className="font-medium uppercase">{shipment.provider}</span>
                 <span className="text-muted ml-3 ml-2">Mã vận đơn:</span> <span className="font-medium">{shipment.tracking_number}</span>
              </div>
              <div style={{ borderLeft: '2px solid var(--border)', marginLeft: '1rem', paddingLeft: '1.5rem' }}>
                {shipment.events.map((ev, i) => (
                  <div key={i} className="mb-3 relative">
                    <div style={{ position: 'absolute', left: '-1.85rem', top: '4px', width: '12px', height: '12px', borderRadius: '50%', background: i === 0 ? 'var(--primary)' : 'var(--bg-2)', border: '2px solid var(--primary-light)' }} />
                    <div className="text-sm font-medium">{ev.description || ev.status}</div>
                    <div className="text-xs text-muted mt-1">{new Date(ev.timestamp).toLocaleString('vi-VN')} {ev.location ? `- ${ev.location}` : ''}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Sidebar info */}
        <div className="flex" style={{ flexDirection: 'column', gap: '1.5rem', alignSelf: 'start' }}>
          
          <div className="card">
            <h3 className="mb-3 border-b pb-2">Thanh toán</h3>
            <div className="flex-between text-sm mb-2">
               <span className="text-muted">Phương thức:</span>
               <span className="font-medium uppercase">{order.payment_method}</span>
            </div>
            <div className="flex-between text-sm mb-2">
               <span className="text-muted">Trạng thái:</span>
               <span className={`badge badge-${order.payment_status === 'paid' ? 'success' : 'warning'}`}>{order.payment_status === 'paid' ? 'Đã thanh toán' : 'Chưa thanh toán'}</span>
            </div>
            
            <div className="divider" />
            <div className="flex-between mb-2 text-sm text-muted"><span>Tạm tính:</span> <span>${order.subtotal}</span></div>
            <div className="flex-between mb-2 text-sm text-muted"><span>Phí giao hàng:</span> <span>${order.shipping_fee}</span></div>
            {parseFloat(order.discount) > 0 && <div className="flex-between mb-2 text-sm text-success"><span>Giảm giá:</span> <span>-${order.discount}</span></div>}
            <div className="flex-between mt-2 pt-2 border-t font-bold text-lg">
               <span>Tổng cộng:</span> <span className="price">${order.total}</span>
            </div>

            {order.payment_status !== 'paid' && order.status !== 'cancelled' && payment && (
               <div className="mt-4">
                 <button 
                   className="btn btn-primary w-full flex-center"
                   onClick={() => processPaymentMut.mutate()}
                   disabled={processPaymentMut.isPending}
                 >
                   <CreditCard size={18} className="mr-2" /> Thanh toán ngay
                 </button>
                 <div className="text-xs text-muted text-center mt-2">(Mô phỏng thanh toán)</div>
               </div>
            )}
          </div>

          <div className="card">
            <h3 className="mb-3 border-b pb-2">Giao hàng tới</h3>
            <div className="text-sm">
              <div className="font-bold mb-1">{order.shipping_address?.fullname || 'Khách hàng'}</div>
              <div className="text-muted mb-1">{order.shipping_address?.phone}</div>
              <div className="text-muted">{order.shipping_address?.address}</div>
              <div className="text-muted">{order.shipping_address?.city}</div>
            </div>
            {order.notes && (
              <div className="mt-3 p-2 bg-glass border rounded text-sm text-muted">
                <strong>Ghi chú:</strong> {order.notes}
              </div>
            )}
          </div>

          {['pending', 'confirmed'].includes(order.status) && (
            <div className="card border-danger">
               <button 
                 className="btn btn-danger w-full flex-center"
                 onClick={() => { if(window.confirm('Bạn chắc chắn muốn hủy đơn hàng này?')) cancelMut.mutate() }}
                 disabled={cancelMut.isPending}
               >
                 <PackageX size={18} className="mr-2" /> Hủy đơn hàng
               </button>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
