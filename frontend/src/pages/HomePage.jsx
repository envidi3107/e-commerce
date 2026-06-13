import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { productApi } from '../api'

export default function HomePage() {
  const { data, isLoading } = useQuery({
    queryKey: ['featured-products'],
    queryFn: () => productApi.list({ ordering: '-rating_avg', page_size: 8 }).then(res => res.data)
  })

  return (
    <div className="page">
      {/* Hero Section */}
      <section className="container mb-4">
        <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center', background: 'var(--grad-primary)', border: 'none' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', fontWeight: 900 }}>Chào mừng đến với ShopVN</h1>
          <p style={{ fontSize: '1.1rem', opacity: 0.9, maxWidth: '600px', margin: '0 auto 2rem' }}>
            Nền tảng mua sắm trực tuyến hiện đại với hàng triệu sản phẩm đa dạng, chất lượng cao và giao hàng siêu tốc.
          </p>
          <Link to="/products" className="btn btn-secondary btn-lg" style={{ background: '#fff', color: 'var(--primary)', border: 'none' }}>
            Khám phá ngay
          </Link>
        </div>
      </section>

      {/* Trending Products */}
      <section className="container">
        <div className="flex-between mb-2">
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Sản phẩm nổi bật</h2>
          <Link to="/products" className="text-muted" style={{ fontSize: '0.9rem', fontWeight: 500 }}>Xem tất cả &rarr;</Link>
        </div>

        {isLoading ? (
          <div className="grid-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="card skeleton" style={{ height: '300px' }} />
            ))}
          </div>
        ) : (
          <div className="grid-4">
            {data?.results?.map(p => (
              <Link to={`/products/${p.id}`} key={p.id} className="card fade-in" style={{ padding: '1rem', display: 'flex', flexDirection: 'column' }}>
                <div style={{ background: 'var(--bg-2)', borderRadius: '8px', padding: '1rem', marginBottom: '1rem', height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {p.thumbnail ? (
                    <img src={p.thumbnail} alt={p.name} style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} />
                  ) : (
                    <span className="text-muted">No Image</span>
                  )}
                </div>
                <h3 className="truncate" style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>{p.name}</h3>
                <div className="flex-between mt-auto">
                  <span className="price">{Number(p.price).toLocaleString('vi-VN')}₫</span>
                  {p.rating_avg > 0 && <span className="badge badge-warning">★ {p.rating_avg}</span>}
                </div>
              </Link>
            ))}
            {(!data?.results || data.results.length === 0) && (
              <div className="empty-state" style={{ gridColumn: '1 / -1' }}>
                Không có sản phẩm nào
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  )
}
