# E-Commerce Microservices System

Hệ thống E-Commerce theo kiến trúc Microservices với Django, FastAPI, Nginx và Docker.

## Kiến trúc hệ thống

```
Client → Nginx (API Gateway :80)
              ├── /api/auth/         → user-service     (:8000)
              ├── /api/users/        → user-service     (:8000)
              ├── /api/products/     → product-service  (:8000)
              ├── /api/categories/   → product-service  (:8000)
              ├── /api/inventory/    → product-service  (:8000)
              ├── /api/cart/         → cart-service     (:8000)
              ├── /api/orders/       → order-service    (:8000)
              ├── /api/payments/     → payment-service  (:8000)
              ├── /api/shipping/     → shipping-service (:8000)
              ├── /api/search/       → ai-service       (:8006)
              └── /api/recommendations/ → ai-service   (:8006)
```

## Services

| Service          | Tech     | Port | Database     | Mô tả                            |
|------------------|----------|------|--------------|----------------------------------|
| api-gateway      | Nginx    | 80   | -            | Reverse proxy, rate limiting     |
| user-service     | Django   | 8000 | user_db      | Auth JWT, quản lý người dùng     |
| product-service  | Django   | 8000 | product_db   | Sản phẩm, 10 categories, tồn kho |
| cart-service     | Django   | 8000 | cart_db      | Giỏ hàng                         |
| order-service    | Django   | 8000 | order_db     | Đặt hàng, order lifecycle        |
| payment-service  | Django   | 8000 | payment_db   | Thanh toán (COD, bank, e-wallet) |
| shipping-service | Django   | 8000 | shipping_db  | Giao hàng, tracking              |
| ai-service       | FastAPI  | 8006 | -            | Tìm kiếm, gợi ý sản phẩm        |

## Cấu trúc thư mục

```
ecom-final/
├── gateway/
│   └── nginx.conf
├── user-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── user_service/          # Django project
│   └── apps/users/            # App
├── product-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── product_service/
│   └── apps/products/
├── cart-service/
├── order-service/
├── payment-service/
├── shipping-service/
├── ai-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
└── infrastructure/
    └── docker-compose.yml
```

## Chạy hệ thống

### Yêu cầu
- Docker Desktop
- Docker Compose v2

### Khởi động

```bash
cd infrastructure
docker-compose up --build
```

### Khởi động từng service riêng lẻ

```bash
# Chỉ databases + redis
docker-compose up user-db product-db cart-db order-db payment-db shipping-db redis

# Từng service
docker-compose up user-service
docker-compose up product-service
```

### Dừng hệ thống

```bash
docker-compose down

# Dừng và xóa volumes (reset databases)
docker-compose down -v
```

## API Endpoints

### Auth (user-service)
```
POST   /api/auth/register/        Đăng ký tài khoản
POST   /api/auth/login/           Đăng nhập → JWT
POST   /api/auth/logout/          Đăng xuất
POST   /api/auth/token/refresh/   Refresh access token
POST   /api/auth/change-password/ Đổi mật khẩu
GET    /api/auth/validate/        Validate token
```

### Users
```
GET    /api/users/profile/    Xem profile
PUT    /api/users/profile/    Cập nhật profile
GET    /api/users/            Danh sách users (admin/staff)
POST   /api/users/            Tạo user (admin)
GET    /api/users/<id>/       Chi tiết user
PUT    /api/users/<id>/       Cập nhật user
DELETE /api/users/<id>/       Vô hiệu hóa user
```

### Products
```
GET    /api/products/                  Danh sách sản phẩm (filter, sort, page)
POST   /api/products/                  Tạo sản phẩm (staff/admin)
GET    /api/products/<id>/             Chi tiết sản phẩm
PUT    /api/products/<id>/             Cập nhật (staff/admin)
DELETE /api/products/<id>/             Deactivate (staff/admin)
GET    /api/categories/                Danh sách 10 categories
GET    /api/inventory/<product_id>/    Tồn kho
PUT    /api/inventory/<product_id>/    Cập nhật tồn kho (staff/admin)
```

### Cart
```
GET    /api/cart/              Xem giỏ hàng
DELETE /api/cart/              Xóa toàn bộ giỏ
POST   /api/cart/items/        Thêm sản phẩm
PUT    /api/cart/items/<id>/   Cập nhật số lượng
DELETE /api/cart/items/<id>/   Xóa item
```

### Orders
```
GET    /api/orders/             Danh sách đơn hàng
POST   /api/orders/             Tạo đơn từ giỏ hàng
GET    /api/orders/<id>/        Chi tiết đơn hàng
DELETE /api/orders/<id>/        Hủy đơn hàng
PUT    /api/orders/<id>/status/ Cập nhật trạng thái (staff/admin)
```

### Payments
```
GET    /api/payments/             Lịch sử thanh toán
GET    /api/payments/<id>/        Chi tiết thanh toán
POST   /api/payments/<id>/process/ Xử lý thanh toán
POST   /api/payments/<id>/refund/  Hoàn tiền (staff/admin)
```

### Shipping
```
GET    /api/shipping/             Danh sách vận đơn
GET    /api/shipping/<id>/        Chi tiết vận đơn
GET    /api/shipping/<id>/tracking/ Tracking timeline
PUT    /api/shipping/<id>/status/   Cập nhật trạng thái (staff/admin)
```

### AI Service
```
GET    /api/search/?q=<query>                Tìm kiếm sản phẩm
GET    /api/recommendations/<product_id>/   Gợi ý tương tự
GET    /api/trending/                        Sản phẩm trending
POST   /api/recommendations/user/           Gợi ý theo user
```

## Swagger UI

Mỗi service đều có Swagger UI tại `/api/docs/`:

| Service         | Swagger URL                          |
|-----------------|--------------------------------------|
| user-service    | http://localhost/api/docs/ (via nginx) |
| Trực tiếp       | http://localhost:8000/api/docs/      |

## 10 Product Categories

| Code          | Tên                      |
|---------------|--------------------------|
| `books`       | Books                    |
| `electronics` | Electronics              |
| `fashion`     | Fashion                  |
| `home_living` | Home & Living            |
| `sports`      | Sports                   |
| `beauty`      | Beauty & Personal Care   |
| `toys`        | Toys & Games             |
| `automotive`  | Automotive               |
| `food`        | Food & Beverage          |
| `health`      | Health & Wellness        |

## Product Attributes (JSON field)

Multi-domain attributes lưu trong field `attributes` dạng JSON:

```json
// Books
{ "author": "Nam Cao", "isbn": "978-...", "publisher": "NXB", "pages": 300 }

// Electronics
{ "brand": "Samsung", "model": "Galaxy S24", "warranty_months": 12 }

// Fashion
{ "sizes": ["S", "M", "L", "XL"], "colors": ["red", "blue"], "material": "cotton" }
```

## User Roles

| Role       | Quyền hạn                                     |
|------------|-----------------------------------------------|
| `admin`    | Toàn quyền: CRUD users, products, orders, ... |
| `staff`    | Quản lý sản phẩm, xem orders, cập nhật status |
| `customer` | Mua hàng, xem đơn của mình                    |

## Order Lifecycle

```
pending → confirmed → processing → shipped → delivered
                ↓
            cancelled
```

## Inter-Service Communication

```
order-service  ──POST──→  cart-service     (lấy giỏ hàng)
order-service  ──POST──→  payment-service  (tạo payment)
order-service  ──POST──→  shipping-service (tạo shipment)
payment-service ──PATCH─→ order-service    (cập nhật payment_status)
shipping-service ──PATCH→ order-service    (cập nhật status)
cart-service   ──GET───→  product-service  (lấy thông tin sản phẩm)
ai-service     ──GET───→  product-service  (lấy sản phẩm để search/recommend)
```

## Development Notes

- Mỗi service có DB riêng → không share database
- JWT signing key phải giống nhau trên tất cả services (`SECRET_KEY`)
- Internal endpoints (`/internal/...`) không yêu cầu JWT (chỉ dùng nội bộ)
- Mock payment: COD tự động success, bank cần `bank_ref`, ewallet tự động success
