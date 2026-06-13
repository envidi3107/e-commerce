export default function NotFound() {
  return (
    <div className="page container flex-center fade-in">
      <div className="empty-state">
        <h1 style={{ fontSize: '6rem', fontWeight: 900, background: 'var(--grad-accent)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0, lineHeight: 1 }}>404</h1>
        <h2 className="mb-2 mt-2">Trang không tồn tại</h2>
        <p className="text-muted mb-4">URL bạn yêu cầu không được tìm thấy trên hệ thống.</p>
        <a href="/" className="btn btn-primary">Về Trang chủ</a>
      </div>
    </div>
  )
}
