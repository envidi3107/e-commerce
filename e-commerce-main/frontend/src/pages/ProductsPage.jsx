import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { productApi } from '../api'

export default function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const page = parseInt(searchParams.get('page') || '1')
  const search = searchParams.get('search') || ''
  const category = searchParams.get('category') || ''
  const ordering = searchParams.get('ordering') || '-created_at'

  const { data: catData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => productApi.categories().then(res => res.data)
  })

  const { data, isLoading } = useQuery({
    queryKey: ['products', { page, search, category, ordering }],
    queryFn: () => productApi.list({ page, search, category, ordering }).then(res => res.data)
  })

  const updateParams = (updates) => {
    const newParams = Object.fromEntries(searchParams.entries())
    Object.assign(newParams, updates)
    if (updates.category !== undefined && updates.category !== category) newParams.page = '1'
    if (updates.search !== undefined && updates.search !== search) newParams.page = '1'
    if (updates.ordering !== undefined && updates.ordering !== ordering) newParams.page = '1'
    
    // Remove empty params
    Object.keys(newParams).forEach(k => {
      if (!newParams[k]) delete newParams[k]
    })
    setSearchParams(newParams)
  }

  return (
    <div className="page container">
      <div className="flex-between mb-3">
        <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>
          {search ? `Tìm kiếm: "${search}"` : 'Tất cả sản phẩm'}
        </h1>
        <div className="flex gap-2">
           <select 
              value={ordering} 
              onChange={e => updateParams({ ordering: e.target.value })}
              style={{ width: 'auto', minWidth: '150px' }}
            >
              <option value="-created_at">Mới nhất</option>
              <option value="price">Giá: Thấp đến cao</option>
              <option value="-price">Giá: Cao đến thấp</option>
              <option value="-rating_avg">Đánh giá cao</option>
           </select>
        </div>
      </div>

      <div className="grid-5" style={{ gridTemplateColumns: '250px 1fr' }}>
        {/* Sidebar Filters */}
        <div className="card" style={{ alignSelf: 'start', position: 'sticky', top: '80px' }}>
          <h3 className="mb-2" style={{ fontSize: '1.1rem' }}>Danh mục</h3>
          <div className="flex" style={{ flexDirection: 'column', gap: '0.5rem' }}>
            <button 
              className={`btn btn-sm ${!category ? 'btn-primary' : 'btn-secondary'}`}
              style={{ justifyContent: 'flex-start' }}
              onClick={() => updateParams({ category: '' })}
            >
              Tất cả
            </button>
            {catData?.map(c => (
              <button 
                key={c.code}
                className={`btn btn-sm ${category === c.code ? 'btn-primary' : 'btn-secondary'}`}
                style={{ justifyContent: 'flex-start' }}
                onClick={() => updateParams({ category: c.code })}
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>

        {/* Product List */}
        <div>
          {isLoading ? (
            <div className="grid-3">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="card skeleton" style={{ height: '320px' }} />
              ))}
            </div>
          ) : (
            <>
              <div className="grid-3">
                {data?.results?.map(p => (
                  <Link to={`/products/${p.id}`} key={p.id} className="card fade-in" style={{ padding: '1rem', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ background: 'var(--bg-2)', borderRadius: '8px', padding: '1rem', marginBottom: '1rem', height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {p.thumbnail ? (
                        <img src={p.thumbnail} alt={p.name} style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} />
                      ) : (
                        <span className="text-muted">No Image</span>
                      )}
                    </div>
                    <div className="mb-1">
                      <span className="badge badge-muted">{p.category_name}</span>
                    </div>
                    <h3 className="truncate" style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>{p.name}</h3>
                    <div className="flex-between mt-auto">
                      <div>
                        <span className="price">${p.price}</span>
                        {p.compare_price && <span className="price-old ml-1" style={{ marginLeft: '0.5rem' }}>${p.compare_price}</span>}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>

              {(!data?.results || data.results.length === 0) && (
                <div className="empty-state">
                  <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                  <h3>Không tìm thấy sản phẩm</h3>
                  <p>Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
                </div>
              )}

              {/* Pagination */}
              {data?.count > 20 && (
                 <div className="pagination">
                    <button 
                      className="page-btn" 
                      disabled={page <= 1}
                      onClick={() => updateParams({ page: (page - 1).toString() })}
                    >&larr;</button>
                    <span className="text-muted text-sm">Trang {page} / {Math.ceil(data.count / 20)}</span>
                    <button 
                      className="page-btn"
                      disabled={page >= Math.ceil(data.count / 20)}
                      onClick={() => updateParams({ page: (page + 1).toString() })}
                    >&rarr;</button>
                 </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
