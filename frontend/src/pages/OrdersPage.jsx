import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Package } from 'lucide-react'
import { orderApi } from '../api'

const STATUS_COLORS = {
  pending:    'warning',
  confirmed:  'primary',
  processing: 'primary',
  shipped:    'primary',
  delivered:  'success',
  cancelled:  'danger',
}

const STATUS_LABELS = {
  pending:    'Chờ xác nhận',
  confirmed:  'Đã xác nhận',
  processing: 'Đang xử lý',
  shipped:    'Đang giao hàng',
  delivered:  'Đã giao',
  cancelled:  'Đã hủy',
}

export default function OrdersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: () => orderApi.list({ ordering: '-created_at' }).then(res => res.data)
  })

  if (isLoading) return <div className="loading-center"><div className="spinner" /></div>

  if (!data?.results || data.results.length === 0) {
    return (
      <div className="page container">
        <div className="card empty-state fade-in">
          <Package size={64} style={{ margin: '0 auto 1rem', opacity: 0.5, color: 'var(--primary)' }} />
          <h2>Chưa có đơn hàng nào</h2>
          <p className="text-muted mb-3 mt-1">Bạn chưa thực hiện giao dịch nào trên ShopVN.</p>
          <Link to="/products" className="btn btn-primary">Mua sắm ngay</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page container fade-in">
      <h1 className="mb-4" style={{ fontSize: '2rem', fontWeight: 800 }}>Đơn hàng của tôi</h1>
      
      <div className="flex" style={{ flexDirection: 'column', gap: '1rem' }}>
        {data.results.map(order => (
          <div key={order.id} className="card hover-effect" style={{ padding: '1.5rem' }}>
            <div className="flex-between mb-3 border-b pb-3" style={{ borderBottom: '1px solid var(--border)' }}>
              <div>
                <span className="font-bold text-lg mr-2">Đơn hàng #{order.id}</span>
                <span className="text-sm text-muted">
                  {new Date(order.created_at).toLocaleDateString('vi-VN', { hour: '2-digit', minute:'2-digit' })}
                </span>
              </div>
              <span className={`badge badge-${STATUS_COLORS[order.status] || 'muted'}`}>
                {STATUS_LABELS[order.status] || order.status}
              </span>
            </div>
            
            <div className="grid-3 mb-3 text-sm">
              <div>
                <div className="text-muted mb-1">Phương thức thanh toán</div>
                <div className="font-medium uppercase">{order.payment_method}</div>
              </div>
              <div>
                <div className="text-muted mb-1">Tổng cộng</div>
                <div className="font-bold text-primary-light">${order.total}</div>
              </div>
              <div className="text-right">
                <Link to={`/orders/${order.id}`} className="btn btn-secondary btn-sm">Xem chi tiết</Link>
              </div>
            </div>

            {/* Item preview */}
            <div className="flex gap-2" style={{ overflowX: 'auto', paddingBottom: '0.5rem' }}>
              {order.items?.map(item => (
                <div key={item.id} className="flex gap-2 items-center" style={{ background: 'var(--bg-2)', padding: '0.5rem', borderRadius: '8px', minWidth: '200px' }}>
                  <div style={{ width: '40px', height: '40px', background: 'var(--bg-card)', borderRadius: '4px', overflow: 'hidden', flexShrink: 0 }}>
                    {item.product_thumbnail ? <img src={item.product_thumbnail} alt="" style={{ width:'100%', height:'100%', objectFit:'contain' }} /> : null}
                  </div>
                  <div className="text-xs truncate">
                    <div className="font-medium truncate">{item.product_name}</div>
                    <div className="text-muted">x{item.quantity}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
