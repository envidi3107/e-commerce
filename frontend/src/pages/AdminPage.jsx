import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Settings, Package, Users, ShoppingBag } from 'lucide-react'
import toast from 'react-hot-toast'
import { orderApi, adminApi, productApi } from '../api'

// Simple Admin Dashboard with tabs
export default function AdminPage() {
  const [tab, setTab] = useState('orders')

  return (
    <div className="page container fade-in">
      <div className="flex-between mb-4">
        <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Quản trị hệ thống</h1>
        <span className="badge badge-danger" style={{ padding: '0.4rem 1rem' }}>ADMIN MODE</span>
      </div>

      <div className="grid-5" style={{ gridTemplateColumns: '250px 1fr' }}>
        {/* Sidebar */}
        <div className="card" style={{ alignSelf: 'start', padding: '1rem' }}>
          <div className="flex" style={{ flexDirection: 'column', gap: '0.5rem' }}>
            <button className={`btn w-full ${tab === 'orders' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('orders')} style={{ justifyContent: 'flex-start' }}>
              <Package size={18} /> Quản lý Đơn hàng
            </button>
            <button className={`btn w-full ${tab === 'products' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('products')} style={{ justifyContent: 'flex-start' }}>
              <ShoppingBag size={18} /> Quản lý Sản phẩm
            </button>
            <button className={`btn w-full ${tab === 'users' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('users')} style={{ justifyContent: 'flex-start' }}>
              <Users size={18} /> Quản lý Người dùng
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="card" style={{ padding: '1.5rem', minHeight: '500px' }}>
          {tab === 'orders' && <OrdersManager />}
          {tab === 'products' && <ProductsManager />}
          {tab === 'users' && <UsersManager />}
        </div>
      </div>
    </div>
  )
}

function OrdersManager() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['admin-orders'],
    queryFn: () => orderApi.list({ ordering: '-created_at' }).then(res => res.data)
  })

  const updateStatusMut = useMutation({
    mutationFn: ({ id, status }) => orderApi.updateStatus(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-orders'])
      toast.success('Cập nhật trạng thái thành công')
    },
    onError: () => toast.error('Cập nhật thất bại')
  })

  if (isLoading) return <div className="spinner mx-auto mt-4" />

  return (
    <div>
      <h2 className="mb-4">Tất cả Đơn hàng</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Khách hàng</th>
              <th>Ngày đặt</th>
              <th>Tổng tiền</th>
              <th>Trạng thái</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {data?.results?.map(o => (
              <tr key={o.id}>
                <td className="font-medium">#{o.id}</td>
                <td>ID: {o.user_id}</td>
                <td>{new Date(o.created_at).toLocaleDateString('vi-VN')}</td>
                <td className="font-bold text-primary-light">${o.total}</td>
                <td>
                  <select 
                    value={o.status}
                    onChange={(e) => updateStatusMut.mutate({ id: o.id, status: e.target.value })}
                    disabled={updateStatusMut.isPending || o.status === 'cancelled'}
                    style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', borderRadius: '4px' }}
                  >
                    <option value="pending">Chờ xác nhận</option>
                    <option value="confirmed">Đã xác nhận</option>
                    <option value="processing">Đang xử lý</option>
                    <option value="shipped">Đang giao</option>
                    <option value="delivered">Đã giao</option>
                    <option value="cancelled">Đã hủy</option>
                  </select>
                </td>
                <td>
                  <Link to={`/orders/${o.id}`} className="text-primary text-sm hover:underline">Chi tiết</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ProductsManager() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-products'],
    queryFn: () => productApi.list().then(res => res.data)
  })

  if (isLoading) return <div className="spinner mx-auto mt-4" />

  return (
    <div>
      <div className="flex-between mb-4">
        <h2>Quản lý Sản phẩm</h2>
        <button className="btn btn-primary btn-sm">+ Thêm mới</button>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Hình ảnh</th>
              <th>Tên sản phẩm</th>
              <th>Giá</th>
              <th>Tồn kho</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {data?.results?.map(p => (
              <tr key={p.id}>
                <td className="font-medium">{p.id}</td>
                <td>
                  <div style={{ width: '40px', height: '40px', background: 'var(--bg-2)', borderRadius: '4px', overflow: 'hidden' }}>
                    {p.thumbnail && <img src={p.thumbnail} alt="" style={{ width:'100%', height:'100%', objectFit:'contain' }} />}
                  </div>
                </td>
                <td><div className="truncate" style={{ maxWidth: '200px' }}>{p.name}</div></td>
                <td className="font-medium">${p.price}</td>
                <td>{p.inventory?.available ?? 0}</td>
                <td>
                  <Link to={`/products/${p.id}`} className="text-primary text-sm hover:underline mr-2">Sửa</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function UsersManager() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.users().then(res => res.data)
  })

  if (isLoading) return <div className="spinner mx-auto mt-4" />

  return (
    <div>
      <h2 className="mb-4">Quản lý Người dùng</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Họ tên</th>
              <th>Vai trò</th>
              <th>Trạng thái</th>
            </tr>
          </thead>
          <tbody>
            {data?.results?.map(u => (
              <tr key={u.id}>
                <td className="font-medium">{u.id}</td>
                <td>{u.email}</td>
                <td>{u.first_name} {u.last_name}</td>
                <td>
                  <span className={`badge badge-${u.role === 'admin' ? 'danger' : (u.role === 'staff' ? 'warning' : 'primary')}`}>
                    {u.role.toUpperCase()}
                  </span>
                </td>
                <td>
                  <span className={`badge badge-${u.is_active ? 'success' : 'muted'}`}>
                    {u.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
