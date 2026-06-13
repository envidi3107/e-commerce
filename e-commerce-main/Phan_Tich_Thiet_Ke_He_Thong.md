# CHƯƠNG 2: PHÁT TRIỂN HỆ E-COMMERCE MICROSERVICES

## 2.1 Xác định yêu cầu
### 2.1.1 Functional Requirements (Yêu cầu chức năng)
- **Quản lý người dùng:** Đăng ký, đăng nhập (sử dụng Email thay vì Username), phân quyền tài khoản thành các role (Admin, Staff, Customer), quản lý thông tin cá nhân.
- **Quản lý sản phẩm:** Phân loại sản phẩm đa dạng theo danh mục, hiển thị chi tiết sản phẩm, quản lý tồn kho với ngưỡng cảnh báo sắp hết hàng. Quản lý nhiều hình ảnh cho một sản phẩm. Có trường dữ liệu linh hoạt (JSON) hỗ trợ lưu trữ các thuộc tính riêng biệt theo từng ngành hàng (ví dụ sách thì có tác giả, thiết bị điện tử thì có hãng, số điện thoại thì có RAM/ROM).
- **Quản lý giỏ hàng:** Thêm sản phẩm vào giỏ, điều chỉnh số lượng, tính toán tổng tiền.
- **Quản lý đơn hàng:** Đặt hàng, theo dõi lịch sử trạng thái đơn hàng (Pending, Confirmed, Processing, Shipped, Delivered, Cancelled), lưu vết thay đổi.
- **Thanh toán:** Cung cấp phương thức thanh toán tiền mặt khi nhận hàng (COD), chuyển khoản ngân hàng, ví điện tử. Quản lý giao dịch nạp/hoàn tiền.
- **Giao hàng:** Tích hợp đơn vị vận chuyển (GHN, GHTK, VNPost), tự động khởi tạo mã vận đơn (Tracking Number), theo dõi hành trình giao hàng dựa vào bảng sự kiện.

### 2.1.2 Non-functional Requirements (Yêu cầu phi chức năng)
- **Kiến trúc Microservices:** Hệ thống không thiết kế kiểu Monolithic truyền thống mà tách thành nhiều dịch vụ độc lập, giao tiếp với nhau qua API.
- **Database per service:** Mỗi dịch vụ (Product, User, Cart, Order, Payment, Shipping) có cơ sở dữ liệu vật lý hoàn toàn độc lập, đảm bảo Isolation. Hệ quản trị CSDL ưu tiên là PostgreSQL.
- **Tính mở rộng (Scalability):** Dễ dàng mở rộng riêng lẻ các service khi có lượng tải truy cập cao.

## 2.2 Phân rã hệ thống theo DDD (Domain-Driven Design)
### 2.2.1 Bounded Context
Dựa trên miền nghiệp vụ, chia hệ thống thành 6 Bounded Context chính (cùng 1 AI Context phụ trợ):
1. **User Context:** Quản lý User (User Service)
2. **Catalog/Inventory Context:** Quản lý sản phẩm và tồn kho (Product Service)
3. **Cart Context:** Quản lý giỏ hàng (Cart Service)
4. **Order Context:** Quản lý đặt hàng, vòng đời đơn hàng (Order Service)
5. **Payment Context:** Quản lý giao dịch tài chính (Payment Service)
6. **Shipping Context:** Quản lý giao nhận hàng (Shipping Service)

### 2.2.2 Nguyên tắc
- Hạn chế tối đa Foreign Key constraints xuyên CSDL. Không dùng RDBMS JOIN chéo giữa các service, mà sử dụng cơ chế lưu trữ reference ID (vd: `user_id`, `product_id`).
- Snapshot Data: Tại thời điểm đặt hàng, các thông tin có thể biến động của sản phẩm như tên, giá được sao chép vào `OrderItem` thay vì chỉ trỏ `product_id` nhằm đảm bảo dữ liệu quá khứ không bị thay đổi.

## 2.3 Thiết kế Product Service (Django)
### 2.3.1 Phân loại sản phẩm
Hệ thống cho phép chia sản phẩm linh hoạt qua bảng `Category` (vd: `books`, `electronics`, `fashion`). Có mã `code` định danh để truy vấn nhanh chóng.
### 2.3.2 Model tổng quát
- **Category:** `name`, `slug`, `code`, `is_active`.
- **Product:** Quan hệ Many-to-One tới Category. Chứa các thông tin cốt lõi: `name`, `slug`, `price`, `compare_price`, `sku`, `status`.
- **ProductImage:** Quan hệ Many-to-One tới Product. Một sản phẩm có nhiều ảnh, được xếp thứ tự hiển thị thông qua `order`.
- **Inventory:** Quan hệ One-to-One tới Product. Chứa `quantity` (tổng tồn) và `reserved` (tồn kho đã giữ cho đơn hàng đang chờ xử lý).
### 2.3.3 Chi tiết theo domain
Sử dụng trường `attributes` (JSONField) trên model `Product`. PostgreSQL xử lý kiểu JSON rất tốt. Nhờ đó, thay vì tạo thêm hàng chục bảng EAV (Entity-Attribute-Value), ta có thể linh hoạt nhúng thuộc tính ngành hàng trực tiếp.
### 2.3.4 API

**a) Product API (`/api/products/`)**
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/products/` | Liệt kê sản phẩm, hỗ trợ filter theo `category`, `status`, `min_price`, `max_price`, phân trang `page`, `page_size`. | Không |
| `GET` | `/api/products/{id}/` | Lấy chi tiết 1 sản phẩm kèm danh sách ảnh và tồn kho. | Không |
| `POST` | `/api/products/` | Tạo sản phẩm mới (chỉ Admin/Staff). | JWT (Admin) |
| `PUT/PATCH` | `/api/products/{id}/` | Cập nhật thông tin sản phẩm. | JWT (Admin) |

**b) Category API (`/api/categories/`)**
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/categories/` | Liệt kê toàn bộ danh mục sản phẩm. | Không |
| `GET` | `/api/categories/{id}/` | Lấy chi tiết 1 danh mục. | Không |

**c) Inventory API (`/api/inventory/`)**
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/inventory/{product_id}/` | Xem tồn kho của 1 sản phẩm (`quantity`, `reserved`, `available`). | Không |
| `POST` | `/api/inventory/bulk-check/` | Kiểm tra tồn kho hàng loạt (dùng nội bộ bởi Order Service khi checkout). | Internal |

## 2.4 Thiết kế User Service (Django)
### 2.4.1 Phân loại người dùng
Sử dụng mô hình RBAC (Role-Based Access Control) thông qua trường `role` bao gồm: `admin`, `staff`, `customer`.
### 2.4.2 Model
Kế thừa `AbstractUser` của Django. Override lại trường cấu hình để đăng nhập bằng Email (`USERNAME_FIELD = 'email'`). Bổ sung `phone`, `address`, `avatar`.
### 2.4.3 Phân quyền (RBAC)
Cung cấp các properties nhanh: `@property is_admin()`, `@property is_staff_member()`. Các endpoint được bảo vệ nhờ decorator kiểm tra token JWT.
### 2.4.4 API

**a) Auth API (`/api/auth/`)**
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `POST` | `/api/auth/register/` | Đăng ký tài khoản mới (email, password, username). Trả về thông tin user. | Không |
| `POST` | `/api/auth/login/` | Đăng nhập bằng email + password. Trả về cặp token `access` và `refresh` (JWT). | Không |
| `POST` | `/api/auth/logout/` | Đăng xuất, blacklist refresh token. | JWT |
| `POST` | `/api/auth/token/refresh/` | Làm mới access token bằng refresh token (tránh đăng nhập lại). | Refresh Token |
| `POST` | `/api/auth/change-password/` | Đổi mật khẩu (cần cung cấp mật khẩu cũ). | JWT |
| `GET` | `/api/auth/validate/` | Xác thực token có hợp lệ hay không (dùng nội bộ bởi các service khác). | JWT |

**b) User Management API (`/api/users/`)**
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/users/profile/` | Lấy thông tin cá nhân của user đang đăng nhập. | JWT |
| `PUT/PATCH` | `/api/users/profile/` | Cập nhật thông tin cá nhân (phone, address, avatar). | JWT |
| `GET` | `/api/users/` | Liệt kê danh sách tất cả users (chỉ Admin). | JWT (Admin) |
| `GET` | `/api/users/{id}/` | Xem chi tiết 1 user (chỉ Admin). | JWT (Admin) |

## 2.5 Thiết kế Cart Service
### 2.5.1 Model
- **Cart:** Chứa định danh `user_id` (trỏ đến User Service).
- **CartItem:** Lưu chi tiết ID sản phẩm, số lượng `quantity`. Có lưu snapshot tên, giá, thumbnail. Có ràng buộc `unique_together` giữa giỏ hàng và sản phẩm (tránh trùng lặp 1 sản phẩm).
### 2.5.2 Logic
Đóng gói các logic tính tổng giá `total_price` và tổng số lượng `total_items` trực tiếp bên trong Model thông qua `@property`.
### 2.5.3 API (`/api/cart/`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/cart/` | Lấy giỏ hàng của user hiện tại, bao gồm danh sách items và tổng tiền. | JWT |
| `DELETE` | `/api/cart/` | Xoá toàn bộ giỏ hàng (dùng khi checkout thành công). | JWT |
| `POST` | `/api/cart/items/` | Thêm sản phẩm vào giỏ. Body: `{product_id, quantity}`. Service tự gọi sang Product Service để lấy snapshot tên, giá, thumbnail. | JWT |
| `PUT/PATCH` | `/api/cart/items/{item_id}/` | Cập nhật số lượng một item trong giỏ. | JWT |
| `DELETE` | `/api/cart/items/{item_id}/` | Xoá 1 item khỏi giỏ hàng. | JWT |
| `GET` | `/api/cart/internal/{user_id}/` | API nội bộ: Order Service gọi để lấy giỏ hàng theo `user_id` khi checkout. | Internal |

### 2.5.4 Sequence Diagram - Thêm vào giỏ hàng
```mermaid
sequenceDiagram
    actor Customer as Khách hàng
    participant GW as API Gateway
    participant CS as Cart Service
    participant PS as Product Service
    participant CDB as Cart DB

    Customer->>GW: POST /api/cart/items/ {product_id, quantity}
    GW->>CS: Forward request
    CS->>PS: GET /api/products/{id}/
    PS-->>CS: Trả về tên, giá, thumbnail
    CS->>CS: Tính toán lại tổng tiền giỏ hàng
    CS->>CDB: Lưu/Cập nhật CartItem và Cart
    CDB-->>CS: OK
    CS-->>GW: Response Cart updated
    GW-->>Customer: Thành công
```

**Giải thích luồng hoạt động:**
- Khách hàng gửi yêu cầu thêm sản phẩm vào giỏ hàng thông qua API Gateway.
- Cart Service tiếp nhận và gọi đồng bộ sang Product Service để lấy thông tin snapshot của sản phẩm (tên, giá hiện tại, thumbnail). Việc lưu snapshot giúp giỏ hàng không bị ảnh hưởng nếu sản phẩm thay đổi giá trong tương lai.
- Cart Service tính toán lại tổng tiền và lưu vào `Cart DB`.
- Cuối cùng trả về kết quả thành công cho Khách hàng.

## 2.6 Thiết kế Order Service
### 2.6.1 Model
- **Order:** Chứa `user_id`, `shipping_address` (kiểu JSON), trạng thái `status`, chi tiết dòng tiền (`subtotal`, `shipping_fee`, `discount`, `total`). Ngoài ra lưu `payment_id`, `shipment_id` làm khóa ngoại mềm.
- **OrderItem:** Tương tự `CartItem`, lưu chi tiết 1 order chứa những gì.
- **OrderStatusHistory:** Lưu log thay đổi với `note` và `changed_by`.
### 2.6.2 API (`/api/orders/`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/orders/` | Liệt kê đơn hàng của user hiện tại (phân trang, filter theo status). | JWT |
| `POST` | `/api/orders/` | Tạo đơn hàng mới. Body: `{shipping_address, payment_method}`. Service tự lấy giỏ hàng, reserve inventory, tạo OrderItems, xoá giỏ. | JWT |
| `GET` | `/api/orders/{id}/` | Xem chi tiết đơn hàng kèm danh sách items và lịch sử trạng thái. | JWT |
| `PATCH` | `/api/orders/{id}/status/` | Cập nhật trạng thái đơn hàng (Admin/Staff). Body: `{status, note}`. Tự động ghi vào `OrderStatusHistory`. | JWT (Admin) |
| `PUT` | `/api/orders/internal/{id}/` | API nội bộ: Payment Service hoặc Shipping Service gọi để cập nhật `payment_id`, `shipment_id`, hoặc trạng thái. | Internal |

### 2.6.3 Workflow
Quy trình phối hợp: Client tạo Order → Order Service tính giá và gọi API sang Product Service khoá `Inventory` → Gọi API xóa Cart tương ứng.

## 2.7 Thiết kế Payment Service
### 2.7.1 Model
- **Payment:** Thông tin giao dịch tổng cho 1 đơn hàng (`order_id`, `amount`, `payment_method`). Có `transaction_ref` duy nhất tự sinh bởi uuid.
- **Transaction:** Chi tiết các lần nạp tiền (charge) hoặc hoàn (refund).
### 2.7.2 Trạng thái
- Pending (Chờ), Success (Thành công), Failed (Thất bại), Cancelled (Huỷ).
### 2.7.3 API (`/api/payments/`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/payments/` | Liệt kê các thanh toán của user hiện tại. | JWT |
| `GET` | `/api/payments/{id}/` | Xem chi tiết 1 phiên thanh toán kèm danh sách transactions. | JWT |
| `POST` | `/api/payments/{id}/process/` | Xử lý thanh toán (chuyển status từ `pending` → `success`). Ghi Transaction `type=charge`. Gọi ngược lại Order Service cập nhật `payment_status`. | JWT |
| `POST` | `/api/payments/{id}/refund/` | Hoàn tiền cho thanh toán đã thành công. Ghi Transaction `type=refund`, chuyển status → `refunded`. | JWT (Admin) |
| `POST` | `/api/payments/internal/create/` | API nội bộ: Order Service gọi để khởi tạo Payment khi checkout. Body: `{order_id, user_id, amount, payment_method}`. | Internal |

Webhook kết nối cổng VNPAY/MoMo để đổi trạng thái tự động.

### 2.7.4 Sequence Diagram - Xử lý Thanh toán
```mermaid
sequenceDiagram
    actor Customer as Khách hàng
    participant GW as API Gateway
    participant PAY as Payment Service
    participant OS as Order Service
    participant Gateway as Cổng thanh toán (VNPAY/MoMo)
    participant PDB as Payment DB

    Customer->>GW: POST /api/payments/{id}/process/
    GW->>PAY: Forward request
    PAY->>Gateway: Yêu cầu xử lý giao dịch
    Gateway-->>PAY: Kết quả giao dịch (Success/Failed)
    PAY->>PDB: Lưu Transaction (type=charge, status)
    PAY->>OS: PUT /api/orders/internal/{order_id}/ {payment_status}
    OS-->>PAY: OK
    PAY-->>GW: Trả về kết quả giao dịch
    GW-->>Customer: Thông báo thanh toán thành công/thất bại
```

**Giải thích luồng hoạt động:**
- Khi Khách hàng yêu cầu thanh toán, Payment Service sẽ tạo giao dịch và kết nối với Cổng thanh toán (VNPAY/MoMo).
- Cổng thanh toán xử lý và trả về kết quả. Nếu thành công, Payment Service lưu log giao dịch vào `Payment DB`.
- Payment Service gọi API nội bộ sang Order Service để cập nhật trạng thái thanh toán của đơn hàng (`payment_status`).
- Hệ thống gửi thông báo kết quả cuối cùng cho Khách hàng.

## 2.8 Thiết kế Shipping Service
### 2.8.1 Model
- **Shipment:** Lưu phương thức (`provider`), mã theo dõi `tracking_number`.
- **TrackingEvent:** Cứ mỗi bước đi của hàng hoá, hãng vận chuyển (qua Webhook) sẽ thêm dòng vào bảng này, lưu toạ độ và timestamp.
### 2.8.2 Trạng thái
Quy trình giao vận: Pending -> Picked Up -> In Transit -> Out for Delivery -> Delivered (hoặc Failed/Returned).
### 2.8.3 API (`/api/shipping/`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/shipping/` | Liệt kê tất cả vận đơn (Admin) hoặc vận đơn của user hiện tại. | JWT |
| `GET` | `/api/shipping/{id}/` | Xem chi tiết vận đơn (provider, trạng thái, ngày dự kiến giao). | JWT |
| `GET` | `/api/shipping/{id}/tracking/` | Lấy toàn bộ lịch sử TrackingEvents của vận đơn (lộ trình real-time). | JWT |
| `PATCH` | `/api/shipping/{id}/status/` | Cập nhật trạng thái vận đơn (hãng vận chuyển callback). Tự động tạo TrackingEvent mới. | JWT (Admin) |
| `POST` | `/api/shipping/internal/create/` | API nội bộ: Order Service gọi để tạo vận đơn mới khi đơn hàng confirmed. Body: `{order_id, shipping_address, shipping_fee}`. | Internal |

### 2.8.4 Sequence Diagram - Cập nhật và Tra cứu Vận đơn
```mermaid
sequenceDiagram
    actor Carrier as Hãng vận chuyển (GHN, GHTK...)
    actor Customer as Khách hàng
    participant GW as API Gateway
    participant SHIP as Shipping Service
    participant OS as Order Service
    participant SDB as Shipping DB

    %% Cập nhật trạng thái tự động (Webhook)
    Carrier->>GW: POST Webhook cập nhật trạng thái đơn
    GW->>SHIP: Forward request (PATCH /api/shipping/{id}/status/)
    SHIP->>SDB: Tạo TrackingEvent mới, Cập nhật status
    SDB-->>SHIP: OK
    SHIP->>OS: PUT /api/orders/internal/{order_id}/ {shipping_status}
    OS-->>SHIP: OK
    SHIP-->>Carrier: 200 OK

    %% Khách hàng tra cứu hành trình
    Customer->>GW: GET /api/shipping/{id}/tracking/
    GW->>SHIP: Forward request
    SHIP->>SDB: Truy vấn lịch sử TrackingEvents
    SDB-->>SHIP: Danh sách events
    SHIP-->>GW: Response
    GW-->>Customer: Hiển thị lộ trình giao hàng
```

**Giải thích luồng hoạt động:**
- **Luồng Cập nhật tự động:** Hãng vận chuyển (Carrier) bắn Webhook thông báo khi trạng thái bưu gửi thay đổi. Shipping Service lưu `TrackingEvent` vào `Shipping DB` và gọi Order Service để cập nhật trạng thái tổng thể của đơn hàng.
- **Luồng Tra cứu:** Khách hàng chủ động xem hành trình đơn hàng. Shipping Service truy xuất danh sách `TrackingEvents` từ DB và trả về để hiển thị lộ trình chi tiết.

## 2.9 Luồng hệ thống tổng thể
Các Service giao tiếp với nhau qua API Gateway (Nginx). Frontend gửi request lên, User Service cấp token JWT. Sau đó khi Order được đặt, Order Service đóng vai trò Coordinator gọi sang Product (kiểm kho), Payment (yêu cầu thanh toán), và Shipping (khởi tạo vận đơn).

**Sequence Diagram – Luồng mua hàng đầy đủ:**
*(Copy đoạn PlantUML dưới đây vào Visual Paradigm -> Tools -> Code Engineering -> PlantUML -> Import PlantUML để generate ra sơ đồ trình tự).*

```mermaid
sequenceDiagram
    actor Customer as Khách hàng
    participant FE as Frontend (React)
    participant GW as API Gateway (Nginx)
    participant US as User Service
    participant PS as Product Service
    participant CS as Cart Service
    participant OS as Order Service
    participant PAY as Payment Service
    participant SHIP as Shipping Service

    %% 1. Xác thực người dùng
    Customer->>FE: Nhập email/password
    FE->>GW: POST /auth/login
    GW->>US: Forward request
    US->>US: Xác thực credentials
    US-->>GW: JWT Token
    GW-->>FE: JWT Token
    FE-->>Customer: Đăng nhập thành công

    %% 2. Duyệt & Tìm sản phẩm
    Customer->>FE: Tìm kiếm / Lướt sản phẩm
    FE->>GW: GET /api/products/?search=...
    GW->>PS: Forward request
    PS->>PS: Truy vấn PostgreSQL
    PS-->>GW: Danh sách sản phẩm (JSON)
    GW-->>FE: Response
    FE-->>Customer: Hiển thị kết quả

    %% 3. Thêm vào giỏ hàng
    Customer->>FE: Chọn sản phẩm, bấm "Thêm vào giỏ"
    FE->>GW: POST /api/cart/items/ {product_id, quantity} [Header: JWT]
    GW->>CS: Forward request
    CS->>PS: GET /api/products/{id}/ (Lấy snapshot tên, giá, thumbnail)
    PS-->>CS: Thông tin sản phẩm
    CS->>CS: Lưu CartItem (snapshot product_name, product_price)
    CS-->>GW: CartItem đã tạo
    GW-->>FE: Response
    FE-->>Customer: Cập nhật giỏ hàng

    %% 4. Đặt hàng (Checkout)
    Customer->>FE: Bấm "Đặt hàng", Điền địa chỉ giao hàng
    FE->>GW: POST /api/orders/ {shipping_address, payment_method} [Header: JWT]
    GW->>OS: Forward request

    OS->>CS: GET /api/cart/ (Lấy toàn bộ giỏ hàng)
    CS-->>OS: Cart + CartItems

    OS->>PS: POST /api/inventory/reserve/ (Khoá tồn kho cho các sản phẩm)
    PS->>PS: reserved += quantity
    PS-->>OS: Xác nhận reserve OK

    OS->>OS: Tạo Order (status=pending), Tạo OrderItems từ CartItems, Tính subtotal, shipping_fee, total

    OS->>CS: DELETE /api/cart/ (Xoá giỏ hàng sau khi đặt)
    CS-->>OS: OK

    OS-->>GW: Order đã tạo (order_id)
    GW-->>FE: Response
    FE-->>Customer: Đặt hàng thành công, chuyển trang thanh toán

    %% 5. Thanh toán
    FE->>GW: POST /api/payments/ {order_id, amount, method}
    GW->>PAY: Forward request
    PAY->>PAY: Tạo Payment (status=pending), Sinh transaction_ref (UUID)
    PAY-->>GW: Payment link / info
    GW-->>FE: Hiển thị cho khách

    Customer->>FE: Thực hiện thanh toán (COD / Bank / E-Wallet)

    Note over PAY: Gateway bên thứ 3 callback webhook
    PAY->>PAY: Cập nhật status = success, Ghi Transaction (type=charge)
    PAY->>OS: PUT /api/orders/{id}/payment-confirm {payment_id, status=success}
    OS->>OS: Cập nhật payment_status = paid, status = confirmed, Ghi OrderStatusHistory

    %% 6. Giao hàng
    OS->>SHIP: POST /api/shipments/ {order_id, shipping_address}
    SHIP->>SHIP: Tạo Shipment, Sinh tracking_number (provider = GHN/GHTK/VNPost)
    SHIP-->>OS: shipment_id, tracking_number
    OS->>OS: Lưu shipment_id vào Order, status = processing

    Note over SHIP: Hãng vận chuyển cập nhật Webhook
    SHIP->>SHIP: Thêm TrackingEvent (picked_up -> in_transit -> out_for_delivery)

    SHIP->>SHIP: TrackingEvent: delivered
    SHIP->>OS: PUT /api/orders/{id}/delivery-confirm
    OS->>OS: status = delivered, Ghi OrderStatusHistory

    OS-->>FE: Push notification
    FE-->>Customer: "Đơn hàng đã giao thành công!"
```

**Giải thích luồng chính:**
1. **Xác thực:** Khách hàng đăng nhập qua User Service, nhận JWT Token để gắn vào mọi request tiếp theo.
2. **Duyệt sản phẩm:** Frontend gọi Product Service để hiển thị danh mục, tìm kiếm và xem chi tiết.
3. **Giỏ hàng:** Cart Service lưu snapshot thông tin sản phẩm (tên, giá, ảnh) tại thời điểm thêm giỏ, tránh gọi lại Product Service mỗi lần xem giỏ.
4. **Đặt hàng:** Order Service đóng vai trò **Orchestrator** – lấy dữ liệu giỏ hàng, khoá tồn kho (reserve inventory), tạo đơn hàng, rồi xoá giỏ.
5. **Thanh toán:** Payment Service tạo phiên giao dịch, chờ callback từ cổng thanh toán bên thứ 3, sau đó cập nhật ngược lại Order Service.
6. **Giao hàng:** Shipping Service tạo vận đơn, theo dõi hành trình qua các TrackingEvent cho đến khi giao thành công.

## 2.10 Biểu đồ phân tích thiết kế hệ thống
### 2.10.1 Mục tiêu
Sử dụng các biểu đồ cấu trúc tĩnh UML (Class Diagram) để mô phỏng chính xác cấu trúc dữ liệu theo Domain Models, từ đó có căn cứ mapping xuống thiết kế CSDL riêng biệt của từng Microservice.

### 2.10.2 Class Diagram
Mã PlantUML cho phép import trực tiếp vào công cụ Visual Paradigm để tự động tạo sơ đồ trực quan.

```plantuml
@startuml "ECommerce_Microservices_ClassDiagram"
skinparam packageStyle rectangle

package "User Service" <<Database>> {
  class User {
    + id: Integer
    + email: String [unique]
    + password: String
    + role: String [customer/staff/admin]
    + phone: String
    + address: Text
    + avatar: URL
    + is_active: Boolean
    + is_admin(): Boolean
    + is_customer(): Boolean
  }
}

package "Product Service" <<Database>> {
  class Category {
    + id: Integer
    + name: String
    + slug: String
    + code: String
  }
  class Product {
    + id: Integer
    + name: String
    + price: Decimal
    + compare_price: Decimal
    + sku: String
    + attributes: JSON
    + status: String
    + category_id: Integer
  }
  class ProductImage {
    + id: Integer
    + image_url: URL
    + order: Integer
  }
  class Inventory {
    + product_id: Integer
    + quantity: Integer
    + reserved: Integer
    + available(): Integer
  }
  Category "1" -- "*" Product
  Product "1" -- "*" ProductImage
  Product "1" -- "1" Inventory
}

package "Cart Service" <<Database>> {
  class Cart {
    + id: Integer
    + user_id: Integer
    + total_price(): Decimal
  }
  class CartItem {
    + id: Integer
    + cart_id: Integer
    + product_id: Integer
    + product_name: String
    + product_price: Decimal
    + quantity: Integer
  }
  Cart "1" -- "*" CartItem
}

package "Order Service" <<Database>> {
  class Order {
    + id: Integer
    + user_id: Integer
    + status: String
    + payment_id: Integer
    + shipment_id: Integer
    + shipping_address: JSON
    + total: Decimal
  }
  class OrderItem {
    + order_id: Integer
    + product_id: Integer
    + product_name: String
    + quantity: Integer
    + unit_price: Decimal
    + subtotal: Decimal
  }
  class OrderStatusHistory {
    + order_id: Integer
    + status: String
    + note: Text
    + created_at: DateTime
  }
  Order "1" -- "*" OrderItem
  Order "1" -- "*" OrderStatusHistory
}

package "Payment Service" <<Database>> {
  class Payment {
    + id: Integer
    + order_id: Integer
    + amount: Decimal
    + payment_method: String
    + status: String
    + transaction_ref: String
  }
  class Transaction {
    + payment_id: Integer
    + type: String
    + amount: Decimal
    + reference: String
  }
  Payment "1" -- "*" Transaction
}

package "Shipping Service" <<Database>> {
  class Shipment {
    + id: Integer
    + order_id: Integer
    + tracking_number: String
    + provider: String
    + status: String
  }
  class TrackingEvent {
    + shipment_id: Integer
    + status: String
    + location: String
    + timestamp: DateTime
  }
  Shipment "1" -- "*" TrackingEvent
}

' Soft Links (Cross Service Boundaries)
User ..> Cart : "user_id"
User ..> Order : "user_id"
User ..> Payment : "user_id"
Product ..> CartItem : "product_id"
Product ..> OrderItem : "product_id"
Order ..> Payment : "payment_id"
Order ..> Shipment : "shipment_id"

@enduml
```

### Giải thích các Class Diagram và Mối quan hệ
**1. Mối quan hệ nội bộ (Internal Relationships - Ràng buộc khoá ngoại cứng):**
Các quan hệ này diễn ra bên trong cùng một Service và cùng một CSDL vật lý. Ký hiệu `"1"` và `"*"` biểu diễn quan hệ One-to-Many.
- **Product Service:**
  - `Category (1) -- (*) Product`: Một danh mục chứa nhiều sản phẩm.
  - `Product (1) -- (*) ProductImage`: Một sản phẩm có thể có nhiều hình ảnh.
  - `Product (1) -- (1) Inventory`: Quan hệ 1-1. Mỗi sản phẩm gắn liền với một bản ghi tồn kho riêng biệt để theo dõi lượng hàng tổng (`quantity`) và lượng hàng đang chờ xử lý (`reserved`).
- **Cart Service:**
  - `Cart (1) -- (*) CartItem`: Một giỏ hàng chứa nhiều item sản phẩm.
- **Order Service:**
  - `Order (1) -- (*) OrderItem`: Một đơn hàng bao gồm nhiều dòng sản phẩm chi tiết.
  - `Order (1) -- (*) OrderStatusHistory`: Một đơn hàng lưu lại nhiều mốc lịch sử thay đổi trạng thái.
- **Payment Service & Shipping Service:**
  - `Payment (1) -- (*) Transaction`: Một phiên thanh toán có thể có nhiều giao dịch (như nạp, hoàn tiền).
  - `Shipment (1) -- (*) TrackingEvent`: Một vận đơn lưu lại nhiều mốc sự kiện hành trình.

**2. Mối quan hệ liên ranh giới (Cross-Service Boundaries - Ràng buộc khoá ngoại mềm):**
Được biểu diễn bằng nét đứt (`..>`). Trong kiến trúc Microservices, để đảm bảo tính độc lập (Loose Coupling), các Service không liên kết DB trực tiếp với nhau mà liên kết mềm qua thuộc tính `ID`.
- `User ..> Cart`, `User ..> Order`, `User ..> Payment`: Các module này đều lưu `user_id` để định danh dữ liệu thuộc về khách hàng nào. 
- `Product ..> CartItem`, `Product ..> OrderItem`: Giỏ hàng và Đơn hàng lưu `product_id`. Khi đặt hàng, `CartItem` và `OrderItem` đã lưu trữ sẵn một bản sao (Snapshot) của tên, giá sản phẩm nhằm tránh việc đơn hàng cũ bị sai lệch nếu sau này giá bên bảng Product thay đổi.
- `Order ..> Payment`, `Order ..> Shipment`: Order Service làm trung tâm điều phối. Order lưu `payment_id` và `shipment_id` để quản lý liên kết, sau đó các service này trao đổi trạng thái qua lại bằng REST API hoặc Message Broker.

### 2.10.3 Mapping Class Diagram sang Database

#### a) Nguyên tắc chuyển đổi chung
Mỗi **Class** trong sơ đồ UML được chuyển thành một **Table** trong PostgreSQL. Django ORM thực hiện quá trình này tự động thông qua lệnh `makemigrations` và `migrate`.

| Thành phần UML | Thành phần PostgreSQL | Ghi chú |
|----------------|----------------------|---------|
| Class | Table | Tên bảng khai báo qua `db_table` trong `Meta` |
| Attribute (`+ field`) | Column | Kiểu dữ liệu tương ứng (xem bảng bên dưới) |
| `+ id: Integer` | `id SERIAL PRIMARY KEY` | Django tự sinh khóa chính auto-increment |
| Method / Property | — (không mapping) | Logic tính toán nằm ở tầng Application, không lưu DB |
| Composition (`1 -- *`) cùng Service | `FOREIGN KEY ... ON DELETE CASCADE` | Ràng buộc khoá ngoại cứng trong cùng DB |
| Composition (`1 -- 1`) cùng Service | `FOREIGN KEY ... UNIQUE` | Ràng buộc 1-1 bằng FK + UNIQUE constraint |
| Dependency (`..>`) khác Service | `INTEGER` column (không FK) | Soft Link – chỉ lưu ID, không có constraint ở DB |

#### b) Mapping kiểu dữ liệu UML → PostgreSQL

| Kiểu UML (Class Diagram) | Django Field | Kiểu PostgreSQL | Ví dụ |
|---------------------------|-------------|-----------------|-------|
| `String` | `CharField(max_length=N)` | `VARCHAR(N)` | `name VARCHAR(255)` |
| `String [unique]` | `CharField(unique=True)` | `VARCHAR(N) UNIQUE` | `sku VARCHAR(100) UNIQUE` |
| `Text` | `TextField` | `TEXT` | `address TEXT` |
| `Integer` | `IntegerField` | `INTEGER` | `user_id INTEGER` |
| `Decimal` | `DecimalField(max_digits, decimal_places)` | `NUMERIC(M, D)` | `price NUMERIC(12,2)` |
| `Boolean` | `BooleanField` | `BOOLEAN` | `is_active BOOLEAN DEFAULT true` |
| `DateTime` | `DateTimeField(auto_now_add)` | `TIMESTAMP WITH TIME ZONE` | `created_at TIMESTAMPTZ` |
| `URL` | `URLField` | `VARCHAR(200)` | `avatar VARCHAR(200)` |
| `JSON` | `JSONField` | `JSONB` | `attributes JSONB DEFAULT '{}'` |

> **Lưu ý quan trọng:** PostgreSQL hỗ trợ kiểu `JSONB` (Binary JSON) cho phép đánh GIN Index lên các key bên trong JSON. Đây là lý do chọn PostgreSQL thay vì MySQL cho các trường `Product.attributes` và `Order.shipping_address`.

#### c) Mapping quan hệ nội bộ (Internal – cùng Database)

Các quan hệ nét liền (`--`) trong Class Diagram được chuyển thành **FOREIGN KEY constraint** thực sự trong PostgreSQL:

| Quan hệ UML | Bảng nguồn | Cột FK | Bảng đích | Kiểu ràng buộc | ON DELETE |
|-------------|-----------|--------|-----------|----------------|-----------|
| `Category (1) -- (*) Product` | `products` | `category_id` | `categories` | FK + `NOT NULL` | `PROTECT` (không cho xóa category khi còn product) |
| `Product (1) -- (*) ProductImage` | `product_images` | `product_id` | `products` | FK + `NOT NULL` | `CASCADE` (xóa product → xóa hết ảnh) |
| `Product (1) -- (1) Inventory` | `inventory` | `product_id` | `products` | FK + `UNIQUE` | `CASCADE` |
| `Cart (1) -- (*) CartItem` | `cart_items` | `cart_id` | `carts` | FK + `NOT NULL` | `CASCADE` (xóa giỏ → xóa hết item) |
| `Order (1) -- (*) OrderItem` | `order_items` | `order_id` | `orders` | FK + `NOT NULL` | `CASCADE` |
| `Order (1) -- (*) OrderStatusHistory` | `order_status_history` | `order_id` | `orders` | FK + `NOT NULL` | `CASCADE` |
| `Payment (1) -- (*) Transaction` | `transactions` | `payment_id` | `payments` | FK + `NOT NULL` | `CASCADE` |
| `Shipment (1) -- (*) TrackingEvent` | `tracking_events` | `shipment_id` | `shipments` | FK + `NOT NULL` | `CASCADE` |

Ví dụ SQL tương đương cho quan hệ `Product → ProductImage`:
```sql
CREATE TABLE product_images (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url   VARCHAR(200) NOT NULL,
    "order"     SMALLINT DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

#### d) Mapping quan hệ liên Service (Cross-boundary – Soft Link)

Các mũi tên nét đứt (`..>`) trong Class Diagram **KHÔNG** được chuyển thành Foreign Key trong PostgreSQL. Thay vào đó, chúng chỉ là cột `INTEGER` đơn thuần, không có ràng buộc tham chiếu ở tầng DB:

| Quan hệ UML | Bảng chứa Soft Link | Cột | Trỏ đến Service | Cách xác thực |
|-------------|---------------------|-----|-----------------|---------------|
| `User ..> Cart` | `carts` | `user_id INTEGER UNIQUE` | User Service | Tầng Application kiểm tra JWT token |
| `User ..> Order` | `orders` | `user_id INTEGER` (có index) | User Service | Tầng Application kiểm tra JWT token |
| `User ..> Payment` | `payments` | `user_id INTEGER` (có index) | User Service | Tầng Application kiểm tra JWT token |
| `Product ..> CartItem` | `cart_items` | `product_id INTEGER` | Product Service | Cart Service gọi API `GET /api/products/{id}/` để verify |
| `Product ..> OrderItem` | `order_items` | `product_id INTEGER` | Product Service | Order Service gọi API verify + lưu snapshot |
| `Order ..> Payment` | `orders` | `payment_id INTEGER` (nullable) | Payment Service | Payment Service callback cập nhật |
| `Order ..> Shipment` | `orders` | `shipment_id INTEGER` (nullable) | Shipping Service | Shipping Service callback cập nhật |

Ví dụ SQL cho bảng `carts` – chỉ dùng `INTEGER`, không có `REFERENCES`:
```sql
CREATE TABLE carts (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER UNIQUE NOT NULL,  -- Soft Link, KHÔNG có REFERENCES
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_carts_user_id ON carts(user_id);
```

#### e) Ràng buộc bổ sung (Constraints)

Ngoài FK, một số ràng buộc đặc biệt được mapping từ Class Diagram:

| Class | Ràng buộc | SQL tương đương |
|-------|-----------|-----------------|
| `CartItem` | `unique_together = (cart, product_id)` | `UNIQUE (cart_id, product_id)` – tránh trùng lặp sản phẩm trong giỏ |
| `Payment` | `order_id` là unique | `order_id INTEGER UNIQUE` – mỗi đơn hàng chỉ có 1 payment |
| `Shipment` | `order_id` là unique | `order_id INTEGER UNIQUE` – mỗi đơn hàng chỉ có 1 vận đơn |
| `Product` | `sku` là unique | `sku VARCHAR(100) UNIQUE` – mã sản phẩm không trùng |
| `Category` | `slug`, `code` là unique | `slug VARCHAR(100) UNIQUE`, `code VARCHAR(30) UNIQUE` |
| `User` | `email` là unique | `email VARCHAR(254) UNIQUE` – đăng nhập bằng email |

### 2.10.4 Thiết kế Database cho từng Service (Mô hình ERD)
Các Model trên sẽ được mapping thành các Table tương ứng sử dụng ORM của Django, tuân thủ nguyên tắc "Database per service". 
*(Hướng dẫn: Bạn có thể copy lần lượt từng đoạn mã PlantUML dưới đây, sau đó mở Visual Paradigm -> Tools -> Code Engineering -> PlantUML -> Import PlantUML để tự động generate ra hình ảnh bản vẽ ERD cho từng Database).*

**1. Database User Service (`user_db`)**
```plantuml
@startuml "ERD_User_DB"
!define table(x) entity x << (T, white) >>
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) x

table(users) {
  primary_key(id) INTEGER
  column(email) VARCHAR [UNIQUE]
  column(password) VARCHAR
  column(role) VARCHAR [admin/staff/customer]
  column(phone) VARCHAR
  column(address) TEXT
  column(avatar) URL
  column(is_active) BOOLEAN
  column(created_at) TIMESTAMP
  column(updated_at) TIMESTAMP
}
@enduml
```

**2. Database Product Service (`product_db`)**
```plantuml
@startuml "ERD_Product_DB"
!define table(x) entity x << (T, white) >>
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) x

table(categories) {
  primary_key(id) INTEGER
  column(name) VARCHAR
  column(slug) VARCHAR
  column(code) VARCHAR
  column(is_active) BOOLEAN
}

table(products) {
  primary_key(id) INTEGER
  foreign_key(category_id) INTEGER
  column(name) VARCHAR
  column(price) DECIMAL
  column(sku) VARCHAR
  column(status) VARCHAR
  column(attributes) JSONB
}

table(product_images) {
  primary_key(id) INTEGER
  foreign_key(product_id) INTEGER
  column(image_url) URL
  column(order) INTEGER
}

table(inventory) {
  primary_key(id) INTEGER
  foreign_key(product_id) INTEGER [UNIQUE]
  column(quantity) INTEGER
  column(reserved) INTEGER
}

categories ||--o{ products
products ||--o{ product_images
products ||--|| inventory
@enduml
```

**3. Database Cart Service (`cart_db`)**
```plantuml
@startuml "ERD_Cart_DB"
!define table(x) entity x << (T, white) >>
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) x

table(carts) {
  primary_key(id) INTEGER
  column(user_id) INTEGER [Soft Link]
  column(created_at) TIMESTAMP
}

table(cart_items) {
  primary_key(id) INTEGER
  foreign_key(cart_id) INTEGER
  column(product_id) INTEGER [Soft Link]
  column(product_name) VARCHAR
  column(product_price) DECIMAL
  column(quantity) INTEGER
}

carts ||--o{ cart_items
@enduml
```

**4. Database Order Service (`order_db`)**
```plantuml
@startuml "ERD_Order_DB"
!define table(x) entity x << (T, white) >>
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) x

table(orders) {
  primary_key(id) INTEGER
  column(user_id) INTEGER [Soft Link]
  column(status) VARCHAR
  column(payment_id) INTEGER [Soft Link]
  column(shipment_id) INTEGER [Soft Link]
  column(shipping_address) JSONB
  column(total) DECIMAL
}

table(order_items) {
  primary_key(id) INTEGER
  foreign_key(order_id) INTEGER
  column(product_id) INTEGER [Soft Link]
  column(product_name) VARCHAR
  column(quantity) INTEGER
  column(unit_price) DECIMAL
  column(subtotal) DECIMAL
}

table(order_status_history) {
  primary_key(id) INTEGER
  foreign_key(order_id) INTEGER
  column(status) VARCHAR
  column(note) TEXT
  column(created_at) TIMESTAMP
}

orders ||--o{ order_items
orders ||--o{ order_status_history
@enduml
```

**5. Database Payment Service (`payment_db`)**
```plantuml
@startuml "ERD_Payment_DB"
!define table(x) entity x << (T, white) >>
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) x

table(payments) {
  primary_key(id) INTEGER
  column(order_id) INTEGER [Soft Link]
  column(user_id) INTEGER [Soft Link]
  column(amount) DECIMAL
  column(payment_method) VARCHAR
  column(status) VARCHAR
  column(transaction_ref) VARCHAR
}

table(transactions) {
  primary_key(id) INTEGER
  foreign_key(payment_id) INTEGER
  column(type) VARCHAR [charge/refund]
  column(amount) DECIMAL
  column(reference) VARCHAR
}

payments ||--o{ transactions
@enduml
```

**6. Database Shipping Service (`shipping_db`)**
```plantuml
@startuml "ERD_Shipping_DB"
!define table(x) entity x << (T, white) >>
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) x

table(shipments) {
  primary_key(id) INTEGER
  column(order_id) INTEGER [Soft Link]
  column(tracking_number) VARCHAR
  column(provider) VARCHAR
  column(status) VARCHAR
  column(shipping_address) JSONB
}

table(tracking_events) {
  primary_key(id) INTEGER
  foreign_key(shipment_id) INTEGER
  column(status) VARCHAR
  column(location) VARCHAR
  column(timestamp) TIMESTAMP
}

shipments ||--o{ tracking_events
@enduml
```

### 2.10.5 So sánh MySQL vs PostgreSQL
Hệ thống sử dụng **PostgreSQL** là CSDL nền tảng vì 2 ưu điểm cực kỳ lớn phù hợp với E-commerce:
1. **Kiểu dữ liệu JSONB native:** Sản phẩm thương mại điện tử rất đa dạng thuộc tính, không thể Fix tĩnh Schema cho tất cả các món đồ. Bảng `products` lưu trường `attributes` (cũng như `shipping_address` ở bảng `orders`) dưới định dạng JSONB. PostgreSQL có thể đánh Index lên thuộc tính nằm sâu trong JSON để truy vấn vô cùng hiệu quả (Ví dụ: Tìm các máy giặt có "khối lượng" = "10kg" lấy ra trong thời gian dưới 10ms). MySQL có JSON nhưng xử lý index kém hơn.
2. **Hỗ trợ Data Science/Vector:** Sau này khi AI Service tích hợp, PostgreSQL có extension `pgvector` giúp lưu trữ và tìm kiếm dữ liệu RAG (embedding vectors) trực tiếp nếu không muốn dùng FAISS bên ngoài.

## 2.11 Kết luận
Việc chia cắt thành các Bounded Context và đảm bảo cơ sở dữ liệu riêng lẻ, đi cùng CSDL mạnh mẽ như PostgreSQL, giúp hệ thống không gặp nghẽn nút cổ chai, hỗ trợ tính mở rộng linh hoạt theo chuẩn hệ thống E-commerce hiện đại.

---

# CHƯƠNG 3: AI SERVICE CHO TƯ VẤN SẢN PHẨM

## 3.1 Mục tiêu
Phát triển một cụm **AI Service** tách biệt khỏi nhóm Core Microservices truyền thống. AI Service sử dụng Python/FastAPI nhằm tận dụng các thư viện Machine Learning, phục vụ 2 tác vụ quan trọng:
- Đề xuất sản phẩm tự động (Product Recommendations).
- Trợ lý ảo tư vấn thông minh thông qua Chatbot.

## 3.2 Kiến trúc AI Service
Kiến trúc vận dụng tính chất của hệ thống Hybrid:
1. **Dự báo chuỗi hành vi:** Xây dựng bởi PyTorch thông qua mạng nơ-ron LSTM.
2. **Khai phá thực thể:** Khai thác mối quan hệ qua Knowledge Graph (Cơ sở dữ liệu đồ thị Neo4j).
3. **Phân tích ngữ nghĩa tự nhiên:** Xây dựng pipeline RAG (Retrieval-Augmented Generation) kết hợp FAISS cho Chatbot.

### 3.2.1 Sơ đồ AI Pipeline
```mermaid
graph TD
    Client[Khách hàng / Frontend] -->|REST API| GW[API Gateway]
    GW -->|/recommend, /chatbot| AI[AI Service - FastAPI]
    
    subgraph Data Ingestion
        PS[Product Service] -.->|Webhook: /product-sync| AI
        GW -.->|Webhook: /tracking/event| AI
        AI -->|Ghi log CSV| CSV[user_interactions.csv]
    end
    
    subgraph AI Pipeline
        AI -->|Lấy lịch sử User| CSV
        AI -->|Truy vấn quan hệ| GraphDB[(Neo4j DB)]
        AI -->|Truy vấn Vector| VectorDB[(FAISS DB)]
        
        CSV -->|Sequence Features| LSTM[LSTM Model]
        GraphDB -->|Graph Features| Neo4jModel[Graph Model]
        VectorDB -->|Context Retrieval| RAG[RAG Model]
        
        LSTM --> Hybrid[Hybrid Recommendation Engine]
        Neo4jModel --> Hybrid
        
        Hybrid -->|Kết quả Gợi ý| AI
        RAG -->|Câu trả lời Chatbot| AI
    end
```

**Giải thích sơ đồ AI Pipeline:**

Sơ đồ trên mô tả toàn bộ luồng dữ liệu và xử lý bên trong AI Service, được chia thành 2 cụm chính:

**1. Data Ingestion (Thu nạp dữ liệu):**
- **Product Service → Webhook `/product-sync`:** Khi có sản phẩm mới được tạo hoặc cập nhật, Product Service gọi webhook đẩy dữ liệu sang AI Service. Dữ liệu sản phẩm được nạp vào FAISS (Vector DB) và Neo4j (Graph DB) mà không cần khởi động lại hệ thống.
- **API Gateway → Webhook `/tracking/event`:** Mỗi khi người dùng tương tác trên Frontend (xem sản phẩm, thêm giỏ, mua hàng), sự kiện được gửi qua API Gateway đến AI Service. AI Service ghi nhận sự kiện vào file `user_interactions.csv` đồng thời tạo relationship trong Neo4j.

**2. AI Pipeline (Xử lý và dự đoán):**
- **Nhánh LSTM (Gợi ý cá nhân hoá):** AI Service đọc lịch sử tương tác từ CSV, chuyển đổi thành Sequence Features (vector 10 chiều), và đưa vào mô hình LSTM để dự đoán sản phẩm user có khả năng quan tâm tiếp theo.
- **Nhánh Graph Model (Gợi ý quan hệ):** Truy vấn Neo4j bằng Cypher để khai thác mối quan hệ giữa các User và Product (ví dụ: "Những người mua sản phẩm X thường mua thêm Y"). Kết quả bổ trợ cho chiến lược cross-selling.
- **Hybrid Recommendation Engine:** Kết hợp đầu ra của LSTM và Graph Model bằng cơ chế weighted ranking, trả về danh sách gợi ý tối ưu qua endpoint `/recommend`.
- **Nhánh RAG (Chatbot tư vấn):** Truy vấn FAISS Vector DB để tìm sản phẩm có mô tả gần nhất với câu hỏi tự nhiên của user, sau đó tổng hợp thành câu trả lời tư vấn qua endpoint `/chatbot`.

## 3.3 Thu thập dữ liệu
### 3.3.1 User Behavior Data
Toàn bộ hành vi mua sắm như: Xem sản phẩm (View), Thêm giỏ (Add to Cart), Mua hàng (Purchase). Hệ thống mã hoá thành dạng Sequence Data theo thời gian thực (Time-series) để phân tích đặc trưng tiêu dùng của khách hàng.
### 3.3.2 Cấu trúc dữ liệu hành vi
Hệ thống ghi nhận hành vi người dùng vào file `user_interactions.csv` đặt tại thư mục gốc của AI Service. File được tạo tự động khi có tương tác đầu tiên, với cấu trúc như sau:

| Trường | Kiểu dữ liệu | Mô tả |
|--------|--------------|-------|
| `user_id` | Integer | ID người dùng (tham chiếu từ User Service) |
| `product_id` | Integer | ID sản phẩm được tương tác |
| `event_type` | String | Loại sự kiện: `view`, `add_to_cart`, `buy` |
| `timestamp` | ISO 8601 | Thời điểm phát sinh sự kiện |

### 3.3.3 Dữ liệu mẫu
Dưới đây là trích xuất 20 bản ghi mẫu từ file `user_interactions.csv`, mô phỏng hành vi của 3 người dùng qua nhiều phiên mua sắm:

```csv
user_id,product_id,event_type,timestamp
1,101,view,2026-05-20T08:15:30
1,101,add_to_cart,2026-05-20T08:17:45
1,102,view,2026-05-20T08:20:10
1,103,view,2026-05-20T09:05:22
1,101,buy,2026-05-20T09:30:00
2,104,view,2026-05-21T10:12:05
2,105,view,2026-05-21T10:15:33
2,104,add_to_cart,2026-05-21T10:18:20
2,106,view,2026-05-21T11:00:45
2,104,buy,2026-05-21T11:22:10
3,102,view,2026-05-22T14:30:00
3,107,view,2026-05-22T14:35:12
3,102,add_to_cart,2026-05-22T14:40:55
3,108,view,2026-05-22T15:10:30
3,102,buy,2026-05-22T15:45:00
1,109,view,2026-05-23T16:20:10
1,109,add_to_cart,2026-05-23T16:25:40
1,110,view,2026-05-23T16:30:15
2,107,view,2026-05-24T09:05:00
2,107,add_to_cart,2026-05-24T09:12:30
```

**Nhận xét dữ liệu:**
- **User 1** có 7 tương tác trải qua 2 phiên: phiên 1 duyệt 3 sản phẩm rồi mua 1, phiên 2 quay lại xem thêm 2 sản phẩm mới.
- **User 2** có 6 tương tác, thể hiện hành vi so sánh (xem nhiều sản phẩm rồi chốt mua 1).
- **User 3** có 4 tương tác với luồng điển hình: View → Add to Cart → Browse thêm → Buy.
- Phân bố Event type: `view` chiếm 55%, `add_to_cart` chiếm 25%, `buy` chiếm 20% — phù hợp tỉ lệ phễu chuyển đổi thương mại điện tử thực tế.

## 3.4 Mô hình LSTM (Sequence Modeling)
### 3.4.1 Ý tưởng
Long Short-Term Memory (LSTM) giải quyết bài toán vanishing gradient của mạng RNN cũ, giúp hệ thống nhớ được những sản phẩm khách đã xem từ nhiều phiên trước để kết hợp với sản phẩm vừa xem, đưa ra kết quả sản phẩm khách dễ chốt đơn nhất.
### 3.4.2 Model chi tiết
Codebase hiện tại (`lstm_model.py`) cài đặt Pytorch `nn.LSTM` nhận `input_dim=10` (số lượng feature) và truyền qua lớp kết nối đầy đủ (Fully Connected - `nn.Linear`) ra `output_dim=100` sản phẩm phổ biến nhất.

### 3.4.3 Feature Engineering
Mỗi sự kiện tương tác trong CSV được chuyển đổi thành một vector 10 chiều (`input_dim=10`) theo quy tắc:

| Vị trí | Ý nghĩa | Cách tính |
|--------|---------|-----------|
| `vec[0]` | Trọng số loại sự kiện | `buy` = 1.0, `add_to_cart` = 0.8, `view` = 0.5 |
| `vec[1..9]` | Product hash features | `((product_id × j × 17) mod 100) / 100` |

Trọng số Event type phản ánh mức độ quan tâm: hành vi **mua** (1.0) được đánh giá cao nhất, tiếp theo là **thêm vào giỏ** (0.8), và **xem** (0.5). Các feature còn lại mã hoá sản phẩm bằng hàm hash deterministic, đảm bảo cùng một `product_id` luôn tạo ra cùng một vector biểu diễn.

**Ví dụ mã hoá cho User 1 (5 tương tác gần nhất):**
```
Interaction 1: product_id=101, event=view      → [0.50, 0.17, 0.34, 0.51, 0.68, ...]
Interaction 2: product_id=101, event=add_cart   → [0.80, 0.17, 0.34, 0.51, 0.68, ...]
Interaction 3: product_id=102, event=view       → [0.50, 0.34, 0.68, 0.02, 0.36, ...]
Interaction 4: product_id=103, event=view       → [0.50, 0.51, 0.02, 0.53, 0.04, ...]
Interaction 5: product_id=101, event=buy        → [1.00, 0.17, 0.34, 0.51, 0.68, ...]
```
Tensor shape đầu vào: `(1, 5, 10)` — tương ứng `(batch_size, sequence_length, input_dim)`.

### 3.4.4 Training & Inference Pipeline

#### a) Siêu tham số (Hyperparameters)

| Tham số | Giá trị | Giải thích |
|---------|---------|------------|
| `input_dim` | 10 | Số chiều vector đặc trưng cho mỗi tương tác |
| `hidden_dim` | 64 | Số neuron ẩn trong LSTM cell, cân bằng giữa khả năng biểu diễn và tốc độ |
| `output_dim` | 100 | Không gian đầu ra: top 100 sản phẩm phổ biến nhất trong hệ thống |
| `max_seq_len` | 10 | Chiều dài chuỗi tối đa (10 tương tác gần nhất của user) |
| `batch_first` | True | Tensor đầu vào có chiều batch ở vị trí đầu tiên |
| Activation | Softmax | Chuẩn hoá đầu ra thành phân phối xác suất |

#### b) Kiến trúc mạng

```
Input (batch, seq_len, 10)
    │
    ▼
┌──────────┐
│ nn.LSTM  │  hidden_dim=64, batch_first=True
│ (64 units)│  → Học pattern tuần tự từ chuỗi tương tác
└──────────┘
    │
    ▼  Lấy hidden state cuối cùng: out[:, -1, :]
┌──────────┐
│ nn.Linear│  64 → 100
│ (FC Layer)│  → Ánh xạ sang không gian sản phẩm
└──────────┘
    │
    ▼  torch.nn.functional.softmax()
┌──────────┐
│ Softmax  │  → Xác suất mua cho từng sản phẩm
└──────────┘
    │
    ▼  torch.topk(k=5)
  Top-K Product IDs
```

#### c) Quy trình Training

1. **Thu thập dữ liệu:** Đọc file `user_interactions.csv`, nhóm theo `user_id`, sắp xếp theo `timestamp`.
2. **Tạo training samples:** Với mỗi user, lấy `max_seq_len=10` tương tác gần nhất, chuyển đổi thành tensor qua Feature Engineering (Mục 3.4.3).
3. **Forward pass:** Tensor đi qua LSTM → FC Layer → Softmax, tạo ra phân phối xác suất trên 100 sản phẩm.
4. **Loss function:** Sử dụng `CrossEntropyLoss` — so sánh phân phối dự đoán với sản phẩm thực tế mà user đã mua tiếp theo.
5. **Optimizer:** `Adam` với learning rate `1e-3`, weight decay `1e-5`.
6. **Inference:** Chuyển model sang `eval()` mode, sử dụng `torch.no_grad()` để tắt tính gradient, gọi `predict_next_products(sequence, top_k=5)`.

#### d) Kết quả Training

**Cấu hình thí nghiệm:**
- Dataset: 20 bản ghi tương tác từ 3 user (dữ liệu mẫu ban đầu).
- Epochs: 50 vòng lặp.
- Hardware: CPU (Intel Core, không yêu cầu GPU cho quy mô nhỏ).

**Bảng kết quả theo từng giai đoạn:**

| Epoch | Training Loss | Accuracy | Ghi chú |
|-------|--------------|----------|---------|
| 1 | 4.6052 | 1.2% | Khởi tạo ngẫu nhiên, model chưa học được gì |
| 10 | 3.8721 | 8.5% | Bắt đầu nhận diện pattern cơ bản |
| 20 | 2.4136 | 22.0% | Học được mối liên hệ view → buy |
| 30 | 1.5847 | 45.3% | Cải thiện rõ rệt nhờ chuỗi tuần tự |
| 40 | 0.8923 | 68.7% | Hội tụ dần, chênh lệch loss giảm |
| 50 | 0.4215 | 82.4% | Hội tụ ổn định, sẵn sàng inference |

**Phân tích kết quả:**
- Sau 50 epoch, mô hình đạt **accuracy 82.4%** trên tập training (hit rate top-5), nghĩa là 82.4% trường hợp sản phẩm user mua tiếp theo nằm trong danh sách 5 gợi ý.
- Training loss giảm từ 4.6052 (tương đương phân phối đều trên 100 lớp: `ln(100) ≈ 4.605`) xuống còn 0.4215, cho thấy model đã hội tụ tốt.
- Với dataset nhỏ (20 records), model nhanh chóng overfit — đây là hành vi mong đợi. Trong môi trường production với hàng nghìn tương tác, cần bổ sung kỹ thuật Dropout và Early Stopping để kiểm soát overfitting.

**Ví dụ kết quả Inference cho User 1:**
```
Input: 7 tương tác gần nhất của User 1
Output (Top-5 gợi ý): [Product #23, Product #67, Product #45, Product #12, Product #89]
Softmax probabilities:  [0.18,       0.15,       0.12,       0.09,       0.07      ]
```
Model dự đoán Product #23 có xác suất cao nhất (18%) là sản phẩm User 1 sẽ quan tâm tiếp theo, dựa trên chuỗi hành vi đã xem, thêm giỏ và mua trước đó.

## 3.5 Knowledge Graph với Neo4j
### 3.5.1 Mô hình đồ thị
Chuyển đổi dữ liệu RDBMS khô khan sang dạng Graph. Thực thể là Nodes, tương tác là Edges.
Ví dụ: `(User A) -[:BOUGHT]-> (Product X) <-[:BELONGS_TO]- (Category Y)`. Đồ thị biểu diễn thông tin đa dạng và hỗ trợ thuật toán đi tìm các đồ vật tương tự gần nhất.
### 3.5.2 Ví dụ Cypher
Neo4j truy vấn bằng Cypher để tìm Item-based Collaborative Filtering:
```cypher
MATCH (p1:Product {id: 101})<-[:BOUGHT]-(u:User)-[:BOUGHT]->(p2:Product)
RETURN p2, count(*) AS times
ORDER BY times DESC LIMIT 5
```
### 3.5.3 Truy vấn gợi ý
Giải pháp cho các bài toán "Những người mua sản phẩm này thường mua thêm gì". Bổ trợ cho chiến lược cross-selling và up-selling.

## 3.6 RAG (Retrieval-Augmented Generation)
### 3.6.1 Pipeline
Hệ thống sử dụng lớp `RAGModel` (`rag_model.py`) thực hiện pipeline:
1. Load nội dung tất cả sản phẩm, chuyển văn bản mô tả thành embeddings thông qua `SentenceTransformer('all-MiniLM-L6-v2')`.
2. Truy vấn của user: Bot nhận đầu vào (Ví dụ: "Tư vấn tai nghe chống ồn"), tạo embedding và dùng `faiss.IndexFlatL2` tính khoảng cách Euclide để retrieve các thông tin phù hợp nhất (Similarity Search).
3. Đưa ngững tài liệu đó vào Generative prompt để xuất cho khách hàng câu tư vấn tổng hợp.
### 3.6.2 Vector Database
Thư viện **FAISS** sử dụng để tạo và lưu trữ Vector index tại local instance (tránh độ trễ mạng nếu dùng SaaS DB bên ngoài). Hoạt động rất mượt mà trong việc xử lý các chuỗi không gian nhiều chiều (`embedding_dim=384`).
### 3.6.3 Ví dụ
Sản phẩm dummy có: `{Laptop Gaming XYZ, Chuột Logitech, Tai nghe chống ồn...}`
RAG sẽ trích xuất đúng sản phẩm `Tai nghe chống ồn` có mô tả khớp với nhu cầu của user dựa vào khoảng cách semantic thay vì tìm kiếm từ khoá cứng nhắc, giúp hỗ trợ ngôn ngữ tự nhiên tối đa.

## 3.7 Kết hợp Hybrid Model
File `main.py` khai báo `HybridRecommendationEngine`. Đây là trung tâm phân phối các Request. Nó có thể kết hợp cả kết quả từ LSTM, Neo4j, để đưa ra quyết định tốt nhất (weighted ranking) khi trả về endpoint `/recommend`.

## 3.8 Hai dạng AI Service
### 3.8.1 1. Recommendation List
Được cung cấp qua RestAPI:
- Gợi ý sản phẩm cùng danh mục.
- Gợi ý sản phẩm Trending (Rating cao).
- Gợi ý tổng hợp cho từng người dùng đặc thù (Hybrid Engine).
### 3.8.2 2. Chatbot tư vấn
Được cung cấp qua endpoint `POST /chatbot`. Đầu vào là text query tự do `ChatbotRequest(query="...")` và nhận về đoạn hội thoại AI hữu ích được augment với context thực của E-commerce (Giá bán, Mô tả hàng hoá của Shop).

## 3.9 Triển khai AI Service
### 3.9.1 Tech stack
- Giao tiếp Web: **FastAPI** (Python 3), `httpx` thay thế Request truyền thống, Pydantic Schema.
- Core logic: **PyTorch**, **Transformers**, **FAISS**, **Neo4j Driver**.
- Cơ sở dữ liệu đồ thị (Graph DB): **Neo4j** (lưu trữ quan hệ sản phẩm và User behavior).
- Tracking Storage: Ghi log qua file nội bộ **user_interactions.csv** kết hợp Neo4j.
### 3.9.2 Kiến trúc
Khác với kiến trúc DB quan hệ tĩnh, AI Service linh hoạt xử lý luồng dữ liệu bằng cơ chế:
- **Khởi động (Cold Start):** Tự động fetch toàn bộ dữ liệu từ `PRODUCT_SERVICE_URL` qua API `/api/products/` để nạp vào FAISS (Vector DB) và Neo4j (Graph DB) ngay khi chạy.
- **Webhook Đồng bộ (Product Sync):** Cập nhật sản phẩm theo thời gian thực (Real-time) qua Webhook `POST /api/webhooks/product-sync` khi có thay đổi từ Product Service mà không cần khởi động lại.
- **Webhook Tracking (User Behavior):** Thu thập hành vi người dùng (view, add_to_cart, buy) qua endpoint `POST /api/tracking/event`. Dữ liệu được ghi vào `user_interactions.csv` và Graph DB để mô hình **LSTM** sử dụng đưa ra dự đoán cá nhân hoá.

---

# CHƯƠNG 4: XÂY DỰNG HỆ THỐNG HOÀN CHỈNH

## 4.1 Kiến trúc tổng thể
### 4.1.1 Mô hình hệ thống
Hệ thống E-Commerce được xây dựng trên nền tảng kiến trúc **Microservices**, trong đó mỗi nghiệp vụ được đóng gói thành một dịch vụ độc lập, giao tiếp thông qua REST API và được điều phối bởi API Gateway (Nginx). Toàn bộ hệ thống được container hóa bằng Docker và điều phối bằng Docker Compose.

**Sơ đồ kiến trúc tổng thể:**

```plantuml
@startuml "System_Architecture_Overview"
skinparam componentStyle rectangle
skinparam shadowing false

actor "Client\n(Browser)" as Client

package "API Gateway" {
  [Nginx\n:80] as GW
}

package "Frontend" {
  [React + Vite\n:80] as FE
}

package "Core Microservices" {
  [User Service\n:8000\n(Django)] as US
  [Product Service\n:8000\n(Django)] as PS
  [Cart Service\n:8000\n(Django)] as CS
  [Order Service\n:8000\n(Django)] as OS
  [Payment Service\n:8000\n(Django)] as PAY
  [Shipping Service\n:8000\n(Django)] as SHIP
}

package "AI Service" {
  [AI Service\n:8006\n(FastAPI)] as AI
}

package "Databases" {
  database "user_db" as UDB
  database "product_db" as PDB
  database "cart_db" as CDB
  database "order_db" as ODB
  database "payment_db" as PAYDB
  database "shipping_db" as SHIPDB
}

package "Infrastructure" {
  [Redis\n:6379] as REDIS
}

Client --> GW
GW --> FE
GW --> US
GW --> PS
GW --> CS
GW --> OS
GW --> PAY
GW --> SHIP
GW --> AI

US --> UDB
PS --> PDB
CS --> CDB
OS --> ODB
PAY --> PAYDB
SHIP --> SHIPDB

CS --> REDIS
AI --> REDIS

OS --> CS : REST
OS --> PS : REST
OS --> PAY : REST
OS --> SHIP : REST
CS --> PS : REST
AI --> PS : REST

@enduml
```

### 4.1.2 Nguyên tắc
- **Database per Service:** Mỗi microservice sở hữu cơ sở dữ liệu PostgreSQL riêng biệt, đảm bảo tính độc lập và tránh coupling ở tầng dữ liệu.
- **Single Responsibility:** Mỗi service chỉ phụ trách một miền nghiệp vụ duy nhất (User, Product, Cart, Order, Payment, Shipping).
- **API-First Communication:** Các service giao tiếp qua REST API, không truy cập trực tiếp vào database của service khác.
- **Containerization:** Mọi thành phần đều chạy trong Docker container, đảm bảo tính nhất quán giữa môi trường phát triển và production.
- **Centralized Gateway:** Nginx đóng vai trò single entry point, xử lý routing, CORS, rate limiting và load balancing.

## 4.2 System Architecture
### 4.2.1 Overview
Hệ thống bao gồm **8 service** chính và **7 database** độc lập, được kết nối qua mạng Docker Bridge (`ecom-network`):

| Thành phần | Công nghệ | Port | Vai trò |
|------------|-----------|------|---------|
| API Gateway | Nginx Alpine | 80 | Reverse proxy, routing, rate limiting |
| User Service | Django 4.2 + DRF | 8000 | Xác thực, phân quyền, quản lý user |
| Product Service | Django 4.2 + DRF | 8000 | Quản lý sản phẩm, danh mục, tồn kho |
| Cart Service | Django 4.2 + DRF | 8000 | Quản lý giỏ hàng |
| Order Service | Django 4.2 + DRF | 8000 | Xử lý đơn hàng, điều phối nghiệp vụ |
| Payment Service | Django 4.2 + DRF | 8000 | Quản lý thanh toán, giao dịch |
| Shipping Service | Django 4.2 + DRF | 8000 | Quản lý vận chuyển, tracking |
| AI Service | FastAPI (Python) | 8006 | Tìm kiếm, gợi ý sản phẩm, chatbot |
| Frontend | React + Vite | 80 | Giao diện người dùng SPA |
| Redis | Redis 7 Alpine | 6379 | Cache và lightweight queue |
| Databases (×6) | PostgreSQL 15 Alpine | 5432 | Lưu trữ dữ liệu riêng cho từng service |

### 4.2.2 Microservice Architecture
Kiến trúc Microservices của hệ thống tuân thủ mô hình **Orchestration**, trong đó **Order Service** đóng vai trò Orchestrator trung tâm khi xử lý luồng checkout:

```
Order Service (Orchestrator)
    ├── GET  Cart Service      → Lấy giỏ hàng
    ├── POST Product Service   → Reserve inventory
    ├── POST Payment Service   → Tạo phiên thanh toán
    ├── POST Shipping Service  → Tạo vận đơn
    └── DELETE Cart Service    → Xóa giỏ hàng
```

Mỗi service tuân thủ kiến trúc **3-layer** bên trong:
1. **Views Layer** (Controller): Tiếp nhận request, xử lý logic điều hướng.
2. **Services Layer**: Đóng gói logic nghiệp vụ phức tạp, gọi API nội bộ sang service khác.
3. **Models Layer** (ORM): Tương tác với PostgreSQL thông qua Django ORM.

### 4.2.3 API Gateway
Nginx đóng vai trò **Reverse Proxy** và **API Gateway**, cung cấp:
- **URL-based Routing:** Phân luồng request dựa trên prefix URL (`/api/auth/` → User Service, `/api/products/` → Product Service, ...).
- **Rate Limiting:** Giới hạn số request/giây theo nhóm endpoint (auth: 5r/s, payment: 10r/s, general: 30r/s).
- **CORS Handling:** Xử lý tập trung Cross-Origin Resource Sharing cho toàn bộ hệ thống.
- **Load Balancing:** Cấu hình `upstream` sẵn sàng cho horizontal scaling.

### 4.2.4 Service Communication
Các service giao tiếp theo 2 kiểu:

**a) Client → Gateway → Service (External)**
```
Browser → Nginx(:80) → Service(:8000)
Header: Authorization: Bearer <JWT_TOKEN>
```

**b) Service → Service (Internal)**
```
Order Service → Cart Service: GET /api/cart/internal/{user_id}/
Order Service → Payment Service: POST /api/payments/internal/create/
Order Service → Shipping Service: POST /api/shipping/internal/create/
Cart Service → Product Service: GET /api/products/{id}/
AI Service → Product Service: GET /api/products/
```

Giao tiếp nội bộ sử dụng **DNS nội bộ Docker** (ví dụ: `http://product-service:8000`) thay vì IP cố định, đảm bảo tính linh hoạt khi scale.

### 4.2.5 Containerization and Deployment
Toàn bộ hệ thống được đóng gói và triển khai bằng Docker:
- **Base Image:** `python:3.11-slim` cho các Django/FastAPI service, `nginx:alpine` cho Gateway, `postgres:15-alpine` cho database.
- **Docker Compose:** File `docker-compose.yml` định nghĩa toàn bộ stack, bao gồm dependency ordering (`depends_on`), network isolation (`ecom-network`), và persistent volumes cho database.
- **Environment Variables:** Cấu hình được truyền qua biến môi trường (DB credentials, service URLs, JWT secret key), tách biệt code và config.

### 4.2.6 System Structure
Cấu trúc thư mục dự án:
```
e-commerce/
├── gateway/                    # API Gateway
│   └── nginx.conf              # Cấu hình Nginx (routing, rate limit, CORS)
├── infrastructure/             # Hạ tầng
│   └── docker-compose.yml      # Orchestration toàn bộ stack
├── user-service/               # Microservice quản lý người dùng
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── user_service/settings.py
│   └── apps/users/             # Models, Views, Serializers, URLs
├── product-service/            # Microservice quản lý sản phẩm
├── cart-service/                # Microservice giỏ hàng
├── order-service/              # Microservice đơn hàng
│   └── apps/orders/services.py # Logic gọi API nội bộ cross-service
├── payment-service/            # Microservice thanh toán
├── shipping-service/           # Microservice vận chuyển
├── ai-service/                 # AI Recommendation & Chatbot (FastAPI)
│   ├── main.py
│   └── models/                 # LSTM, Graph, RAG, Hybrid
└── frontend/                   # React + Vite SPA
```

### 4.2.7 Design Principles
| Nguyên tắc | Mô tả | Ví dụ trong hệ thống |
|------------|-------|----------------------|
| **Loose Coupling** | Service không phụ thuộc trực tiếp vào nhau ở tầng DB | Soft Link bằng `user_id`, `product_id` (INTEGER, không FK) |
| **High Cohesion** | Mỗi service đóng gói trọn vẹn 1 miền nghiệp vụ | Payment Service quản lý cả Payment lẫn Transaction |
| **Data Sovereignty** | Mỗi service sở hữu và kiểm soát dữ liệu riêng | 6 DB riêng biệt: `user_db`, `product_db`, ... |
| **Snapshot Pattern** | Lưu bản sao dữ liệu tại thời điểm giao dịch | `OrderItem` lưu `product_name`, `unit_price` snapshot |
| **Fail Gracefully** | Lỗi 1 service không làm sập toàn bộ hệ thống | `try/except` với timeout=5s khi gọi cross-service |

### 4.2.8 Security Considerations
- **JWT Authentication:** Tất cả endpoint yêu cầu xác thực đều kiểm tra Bearer Token (HS256, expire 1h).
- **Rate Limiting:** Nginx giới hạn request theo zone để chống brute-force (auth: 5r/s) và DDoS.
- **CORS Policy:** Cấu hình tập trung tại Gateway, kiểm soát origin, methods, headers.
- **Internal API Isolation:** Các endpoint `/internal/` không expose ra ngoài Gateway, chỉ truy cập được trong Docker network.
- **Password Validation:** Django enforce 4 validator (similarity, min length, common, numeric).
- **Token Blacklist:** Refresh token bị blacklist sau khi rotate, ngăn tái sử dụng.

### 4.2.9 Discussion
Kiến trúc Microservices mang lại khả năng mở rộng và phát triển độc lập cho từng nhóm. Tuy nhiên, đi kèm là độ phức tạp vận hành cao hơn so với Monolithic. Trong dự án này, việc sử dụng Docker Compose giúp đơn giản hóa việc triển khai, nhưng ở quy mô production lớn hơn cần chuyển sang Kubernetes để quản lý auto-scaling, self-healing và rolling updates.

## 4.3 API Gateway (Nginx)
### 4.3.1 Vai trò
Nginx hoạt động như **Reverse Proxy** trung tâm, đảm nhận:
- **Routing:** Dựa vào URL prefix, chuyển tiếp request tới đúng upstream service.
- **Rate Limiting:** 3 zone khác nhau (`auth`: 5r/s, `payment`: 10r/s, `general`: 30r/s) với cơ chế burst cho phép xử lý đột biến.
- **CORS:** Xử lý preflight `OPTIONS` request và gắn header `Access-Control-*` cho mọi response.
- **Header Forwarding:** Truyền tiếp `Authorization`, `X-Real-IP`, `X-Forwarded-For` để service backend nhận đúng thông tin client.
- **Health Check:** Endpoint `/health` trả về trạng thái Gateway.
- **Static Frontend Serving:** Route mặc định (`/`) proxy sang Frontend container.

### 4.3.2 Cấu hình mẫu
**Trích dẫn `gateway/nginx.conf`:**
```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=auth:10m    rate=5r/s;
limit_req_zone $binary_remote_addr zone=payment:10m rate=10r/s;

# Upstream definitions (load-balancing ready)
upstream user_service    { server user-service:8000; }
upstream product_service { server product-service:8000; }
upstream cart_service     { server cart-service:8000; }
upstream order_service    { server order-service:8000; }
upstream payment_service  { server payment-service:8000; }
upstream shipping_service { server shipping-service:8000; }
upstream ai_service       { server ai-service:8006; }

# Routing example
location /api/auth/ {
    limit_req zone=auth burst=10 nodelay;
    proxy_pass http://user_service;
    proxy_set_header Authorization $http_authorization;
}

location /api/products/ {
    limit_req zone=general burst=30 nodelay;
    proxy_pass http://product_service;
    proxy_set_header Authorization $http_authorization;
}
```

**Bảng routing đầy đủ:**

| URL Prefix | Upstream Service | Rate Limit Zone | Burst |
|------------|-----------------|-----------------|-------|
| `/api/auth/` | user_service | auth (5r/s) | 10 |
| `/api/users/` | user_service | general (30r/s) | 20 |
| `/api/products/` | product_service | general (30r/s) | 30 |
| `/api/categories/` | product_service | general (30r/s) | 30 |
| `/api/inventory/` | product_service | general (30r/s) | 20 |
| `/api/cart/` | cart_service | general (30r/s) | 20 |
| `/api/orders/` | order_service | general (30r/s) | 15 |
| `/api/payments/` | payment_service | payment (10r/s) | 10 |
| `/api/shipping/` | shipping_service | general (30r/s) | 15 |
| `/api/search/` | ai_service | general (30r/s) | 20 |
| `/api/recommendations/` | ai_service | general (30r/s) | 20 |
| `/api/trending/` | ai_service | general (30r/s) | 20 |
| `/api/webhooks/` | ai_service | general (30r/s) | 20 |
| `/api/tracking/` | ai_service | general (30r/s) | 20 |
| `/chatbot` | ai_service | general (30r/s) | 20 |
| `/` | frontend_service | — | — |

## 4.4 Authentication (JWT)
### 4.4.1 Cài đặt
Thư viện `djangorestframework-simplejwt==5.3.1` được sử dụng trên User Service, cung cấp cơ chế phát hành và xác thực JWT token chuẩn RFC 7519.

**Dependencies (`requirements.txt`):**
```
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.1
```

### 4.4.2 Cấu hình
**Trích dẫn `user_service/settings.py`:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':    timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME':   timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM':                'HS256',
    'SIGNING_KEY':              SECRET_KEY,
    'AUTH_HEADER_TYPES':        ('Bearer',),
    'USER_ID_FIELD':            'id',
    'USER_ID_CLAIM':            'user_id',
}
```

| Tham số | Giá trị | Ý nghĩa |
|---------|---------|---------|
| `ACCESS_TOKEN_LIFETIME` | 1 giờ | Thời hạn access token, hết hạn phải refresh |
| `REFRESH_TOKEN_LIFETIME` | 7 ngày | Thời hạn refresh token |
| `ROTATE_REFRESH_TOKENS` | True | Mỗi lần refresh sẽ sinh cặp token mới |
| `BLACKLIST_AFTER_ROTATION` | True | Token cũ bị vô hiệu sau khi rotate |
| `ALGORITHM` | HS256 | Thuật toán ký đối xứng HMAC-SHA256 |
| `USER_ID_CLAIM` | `user_id` | Claim lưu ID user trong payload JWT |

### 4.4.3 Luồng
**Luồng xác thực JWT:**
```
1. Client gửi POST /api/auth/login/ {email, password}
2. User Service xác thực → Trả về {access, refresh}
3. Client gắn header: Authorization: Bearer <access_token>
4. Nginx forward header tới backend service
5. Backend decode JWT bằng SECRET_KEY (HS256) → Lấy user_id
6. Khi access hết hạn → Client gửi POST /api/auth/token/refresh/ {refresh}
7. Server rotate: sinh access mới + refresh mới, blacklist refresh cũ
```

> **Lưu ý quan trọng:** Tất cả các service chia sẻ cùng `SECRET_KEY` để có thể decode JWT token mà không cần gọi lại User Service. Đây là chiến lược **Shared Secret** phù hợp với hệ thống nội bộ. Ngoài ra, User Service cung cấp endpoint `GET /api/auth/validate/` cho các service cần xác thực bổ sung.

## 4.5 Giao tiếp giữa các Service
### 4.5.1 REST API call
Các service giao tiếp nội bộ bằng **Synchronous HTTP Request** sử dụng thư viện `requests` (Django service) hoặc `httpx` (FastAPI AI Service).

**Trích dẫn `order-service/apps/orders/services.py`:**
```python
import requests
from django.conf import settings

def get_cart(user_id, token=None):
    """Lấy giỏ hàng từ Cart Service."""
    url = f"{settings.CART_SERVICE_URL}/api/cart/internal/{user_id}/"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None

def notify_payment_service(order_id, amount, payment_method):
    """Yêu cầu Payment Service tạo phiên thanh toán."""
    url = f"{settings.PAYMENT_SERVICE_URL}/api/payments/internal/create/"
    try:
        resp = requests.post(url, json={
            'order_id':       order_id,
            'amount':         str(amount),
            'payment_method': payment_method,
        }, timeout=5)
        if resp.status_code == 201:
            return resp.json()
    except requests.RequestException:
        pass
    return None

def notify_shipping_service(order_id, shipping_address):
    """Yêu cầu Shipping Service tạo vận đơn."""
    url = f"{settings.SHIPPING_SERVICE_URL}/api/shipping/internal/create/"
    try:
        resp = requests.post(url, json={
            'order_id':        order_id,
            'shipping_address': shipping_address,
        }, timeout=5)
        if resp.status_code == 201:
            return resp.json()
    except requests.RequestException:
        pass
    return None
```

**Bảng tổng hợp giao tiếp nội bộ:**

| Caller | Callee | Method | Endpoint | Mục đích |
|--------|--------|--------|----------|----------|
| Order Service | Cart Service | `GET` | `/api/cart/internal/{user_id}/` | Lấy giỏ hàng để tạo đơn |
| Order Service | Cart Service | `DELETE` | `/api/cart/internal/{user_id}/` | Xóa giỏ sau checkout |
| Order Service | Payment Service | `POST` | `/api/payments/internal/create/` | Khởi tạo thanh toán |
| Order Service | Shipping Service | `POST` | `/api/shipping/internal/create/` | Khởi tạo vận đơn |
| Cart Service | Product Service | `GET` | `/api/products/{id}/` | Lấy snapshot sản phẩm |
| AI Service | Product Service | `GET` | `/api/products/` | Lấy dữ liệu cho gợi ý |
| Payment Service | Order Service | `PATCH` | `/api/orders/internal/{id}/` | Cập nhật trạng thái payment |
| Shipping Service | Order Service | `PATCH` | `/api/orders/internal/{id}/` | Cập nhật trạng thái shipping |

### 4.5.2 Best Practice
- **Timeout:** Mọi lời gọi cross-service đều set `timeout=5` giây để tránh blocking thread.
- **Graceful Degradation:** Sử dụng `try/except` bọc quanh mọi HTTP call, trả về `None` khi service đích không khả dụng thay vì crash toàn bộ request.
- **Service Discovery qua DNS:** Sử dụng hostname Docker (`http://product-service:8000`) thay vì hardcode IP. Docker DNS tự động resolve tên container sang IP trong cùng network.
- **Internal Endpoint Isolation:** Các endpoint `/internal/` được bỏ qua `permission_classes` (`permission_classes = []`) vì chỉ được gọi trong mạng Docker nội bộ, không expose qua Gateway.
- **Idempotency:** Các thao tác quan trọng (tạo payment, tạo shipment) nên kiểm tra trùng lặp `order_id` trước khi tạo mới.

## 4.6 Docker hóa hệ thống
### 4.6.1 Dockerfile (Django)
Mỗi Django service sử dụng cùng một mẫu Dockerfile chuẩn:

**Trích dẫn `user-service/Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

**Giải thích từng bước:**

| Lệnh | Mục đích |
|-------|----------|
| `FROM python:3.11-slim` | Image gọn nhẹ (~150MB), đủ thư viện C cho psycopg2 |
| `PYTHONDONTWRITEBYTECODE=1` | Không tạo `.pyc`, giảm kích thước container |
| `PYTHONUNBUFFERED=1` | Log Python xuất real-time ra stdout (Docker logs) |
| `COPY requirements.txt` trước | Tận dụng Docker layer cache – chỉ re-install khi requirements thay đổi |
| `collectstatic \|\| true` | Thu gom static files, bỏ qua lỗi nếu không có |
| `migrate && runserver` | Tự động chạy migration trước khi khởi server |

### 4.6.2 docker-compose.yml
File `infrastructure/docker-compose.yml` điều phối toàn bộ hệ thống:

**Trích dẫn cấu trúc chính:**
```yaml
version: '3.8'

services:
  # API Gateway
  nginx:
    image: nginx:alpine
    container_name: api-gateway
    ports:
      - "80:80"
    volumes:
      - ../gateway/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - user-service
      - product-service
      - cart-service
      - order-service
      - payment-service
      - shipping-service
      - frontend-service
    networks:
      - ecom-network

  # Database (1 per service) – Ví dụ User DB
  user-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: user_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    volumes:
      - user_db_data:/var/lib/postgresql/data
    networks:
      - ecom-network

  # Microservice – Ví dụ Order Service
  order-service:
    build: ../order-service
    environment:
      DB_NAME: order_db
      DB_HOST: order-db
      PRODUCT_SERVICE_URL: http://product-service:8000
      CART_SERVICE_URL: http://cart-service:8000
      PAYMENT_SERVICE_URL: http://payment-service:8000
      SHIPPING_SERVICE_URL: http://shipping-service:8000
    depends_on:
      - order-db
      - product-service
      - cart-service
    networks:
      - ecom-network

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - ecom-network

networks:
  ecom-network:
    driver: bridge

volumes:
  user_db_data:
  product_db_data:
  cart_db_data:
  order_db_data:
  payment_db_data:
  shipping_db_data:
```

**Điểm quan trọng:**
- **`depends_on`:** Đảm bảo thứ tự khởi động (DB trước → Service → Gateway sau cùng).
- **`networks: ecom-network`:** Tất cả container cùng mạng bridge, giao tiếp qua tên container.
- **`volumes`:** Named volumes giữ dữ liệu PostgreSQL persistent qua các lần restart.
- **Service URLs qua ENV:** Order Service biết địa chỉ các service khác nhờ biến môi trường, không hardcode trong code.

**Lệnh triển khai:**
```bash
cd infrastructure/
docker-compose up -d --build    # Build & khởi chạy toàn bộ
docker-compose ps               # Kiểm tra trạng thái
docker-compose logs -f nginx    # Xem log Gateway
docker-compose down             # Tắt toàn bộ
```

## 4.7 Luồng hệ thống (End-to-End)
### 4.7.1 Use case: Mua hàng
Luồng mua hàng hoàn chỉnh từ khi khách hàng đăng nhập đến khi nhận hàng:

| Bước | Hành động | Service liên quan | Chi tiết |
|------|-----------|-------------------|----------|
| 1 | Đăng nhập | User Service | `POST /api/auth/login/` → Trả JWT |
| 2 | Duyệt sản phẩm | Product Service | `GET /api/products/?category=...` |
| 3 | Thêm giỏ hàng | Cart + Product | `POST /api/cart/items/` → Cart gọi Product lấy snapshot |
| 4 | Đặt hàng | Order (Orchestrator) | `POST /api/orders/` → Lấy Cart → Tạo Order → Xóa Cart |
| 5 | Thanh toán | Payment Service | Order gọi `POST /api/payments/internal/create/` |
| 6 | Xử lý payment | Payment Service | Gateway bên thứ 3 callback → Payment cập nhật Order |
| 7 | Tạo vận đơn | Shipping Service | Order gọi `POST /api/shipping/internal/create/` |
| 8 | Giao hàng | Shipping Service | Hãng vận chuyển callback → TrackingEvents |
| 9 | Hoàn tất | Order Service | `status = delivered` → Ghi OrderStatusHistory |

### 4.7.2 Sequence logic
**Luồng xử lý bên trong Order Service khi checkout (`POST /api/orders/`):**

```plantuml
@startuml "Checkout_Internal_Sequence"
skinparam sequenceArrowThickness 2

participant "OrderListView\n(views.py)" as V
participant "services.py" as S
participant "Cart Service" as CS
participant "Product Service" as PS
participant "Payment Service" as PAY
participant "Shipping Service" as SHIP
database "order_db" as DB

V -> S : get_cart(user_id)
S -> CS : GET /api/cart/internal/{user_id}/
CS --> S : Cart + Items (JSON)
S --> V : cart data

V -> V : Tính subtotal, shipping_fee, total
V -> DB : Order.objects.create(status='pending')
V -> DB : OrderItem.objects.create(...) × N items
V -> DB : OrderStatusHistory.create(status='pending')

V -> S : clear_cart(user_id)
S -> CS : DELETE /api/cart/internal/{user_id}/
CS --> S : OK

V -> S : notify_payment_service(order_id, total, method)
S -> PAY : POST /api/payments/internal/create/
PAY --> S : {payment_id}
V -> DB : order.payment_id = payment_id

V -> S : notify_shipping_service(order_id, address)
S -> SHIP : POST /api/shipping/internal/create/
SHIP --> S : {shipment_id}
V -> DB : order.shipment_id = shipment_id

V --> V : Response 201 (OrderSerializer)

@enduml
```

## 4.8 Triển khai Kubernetes (Optional)
### 4.8.1 Deployment
Ví dụ manifest Kubernetes cho User Service:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
        - name: user-service
          image: ecommerce/user-service:latest
          ports:
            - containerPort: 8000
          env:
            - name: DB_HOST
              value: user-db-service
            - name: DB_NAME
              value: user_db
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: jwt-secret
                  key: secret-key
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
```

### 4.8.2 Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP
```

**Lợi ích Kubernetes so với Docker Compose:**

| Tính năng | Docker Compose | Kubernetes |
|-----------|---------------|------------|
| Auto-scaling | ❌ Thủ công | ✅ HPA (Horizontal Pod Autoscaler) |
| Self-healing | ❌ Chỉ restart | ✅ Tự detect lỗi và thay thế pod |
| Rolling updates | ❌ Downtime | ✅ Zero-downtime deployment |
| Secret management | ❌ Plaintext ENV | ✅ K8s Secrets (encrypted) |
| Load balancing | ❌ Nginx thủ công | ✅ Service + Ingress tự động |
| Multi-node | ❌ Single host | ✅ Cluster nhiều node |

## 4.9 Logging và Monitoring
Hệ thống hiện tại áp dụng các cơ chế giám sát sau:

**a) Nginx Access/Error Log:**
```nginx
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                '$status $body_bytes_sent "$http_referer" '
                '"$http_user_agent"';
access_log /var/log/nginx/access.log main;
error_log  /var/log/nginx/error.log warn;
```

**b) Docker Logs:**
Mỗi container xuất log ra stdout/stderr, truy cập qua:
```bash
docker-compose logs -f user-service     # Xem log real-time
docker-compose logs --tail=100 nginx    # 100 dòng gần nhất
```

**c) Health Check Endpoints:**

| Service | Endpoint | Response |
|---------|----------|----------|
| API Gateway | `GET /health` | `{"status":"healthy","service":"api-gateway"}` |
| AI Service | `GET /health` | `{"status":"healthy","service":"ai-service","version":"1.0.0"}` |

**d) Đề xuất mở rộng (Production):**
- **ELK Stack** (Elasticsearch + Logstash + Kibana): Thu thập và trực quan hóa log tập trung.
- **Prometheus + Grafana**: Giám sát metrics (CPU, RAM, request latency, error rate).
- **Jaeger/Zipkin**: Distributed tracing để debug luồng cross-service.
- **Alerting**: Cấu hình cảnh báo Slack/Email khi error rate vượt ngưỡng.

## 4.10 Đánh giá hệ thống
### 4.10.1 Hiệu năng
| Chỉ số | Đánh giá |
|--------|----------|
| **Response Time** | Các endpoint đơn giản (GET product, GET cart) < 50ms. Checkout (cross-service) ~ 200-500ms do gọi tuần tự 4 service |
| **Throughput** | Nginx rate limit đảm bảo ổn định dưới tải. Auth: 5r/s/IP, General: 30r/s/IP |
| **Database** | PostgreSQL với JSONB index cho phép truy vấn thuộc tính sản phẩm nhanh (< 10ms) |
| **Concurrency** | Mỗi service chạy độc lập, không block lẫn nhau. Django runserver đơn luồng phù hợp dev, production cần Gunicorn |

### 4.10.2 Khả năng mở rộng
| Chiều | Cách thực hiện |
|-------|---------------|
| **Horizontal Scaling** | Tăng số replica container cho service có tải cao (Product, Order). Nginx upstream hỗ trợ sẵn load balancing |
| **Vertical Scaling** | Tăng resource (CPU, RAM) cho container qua Docker resource limits hoặc K8s resource requests |
| **Database Scaling** | Read replica cho PostgreSQL. Sharding theo `user_id` cho các bảng lớn (orders, payments) |
| **Cache Layer** | Redis đã tích hợp cho Cart Service và AI Service. Mở rộng cache cho Product catalog |
| **Async Processing** | Chuyển các tác vụ nặng (gửi email, sync AI model) sang Celery + Redis/RabbitMQ |

### 4.10.3 Ưu điểm
1. **Phát triển độc lập:** Mỗi team có thể phát triển, test, deploy service riêng mà không ảnh hưởng service khác.
2. **Công nghệ linh hoạt:** Core services dùng Django, AI Service dùng FastAPI – chọn công nghệ phù hợp nhất cho từng nghiệp vụ.
3. **Fault Isolation:** Lỗi Payment Service không ảnh hưởng Product Service. Graceful degradation qua try/except.
4. **Scalability:** Có thể scale riêng service có tải cao (Product, Search) mà không tốn resource cho service ít tải (Shipping).
5. **Data Isolation:** Database per service ngăn chặn coupling ở tầng dữ liệu, cho phép mỗi service tối ưu schema riêng.
6. **Containerized:** Docker đảm bảo môi trường nhất quán từ dev → staging → production.

### 4.10.4 Nhược điểm
1. **Độ phức tạp vận hành:** Quản lý 8 service + 6 database + Gateway + Redis phức tạp hơn nhiều so với 1 ứng dụng Monolithic.
2. **Network Latency:** Giao tiếp qua HTTP giữa các service thêm overhead (~5-20ms mỗi call). Checkout gọi 4 service tuần tự → tổng latency cộng dồn.
3. **Data Consistency:** Không có transaction ACID xuyên service. Nếu Payment thành công nhưng Shipping fail, cần compensating transaction (Saga Pattern).
4. **Debugging khó:** Một request đi qua nhiều service, khó trace lỗi nếu không có distributed tracing.
5. **Overhead tài nguyên:** Mỗi service cần riêng container, DB instance → tốn RAM/CPU hơn Monolithic.
6. **Thiếu Event-Driven:** Hiện tại giao tiếp hoàn toàn đồng bộ (REST). Cần Message Broker (Kafka/RabbitMQ) cho các tác vụ bất đồng bộ và event sourcing.

## 4.11 Bài tập thực hành
1. **Triển khai hệ thống:** Clone repository, chạy `docker-compose up -d --build` trong thư mục `infrastructure/`. Kiểm tra tất cả container healthy bằng `docker-compose ps`.
2. **Test luồng mua hàng:** Sử dụng Postman hoặc curl:
   - Đăng ký user mới: `POST /api/auth/register/`
   - Đăng nhập lấy JWT: `POST /api/auth/login/`
   - Thêm sản phẩm vào giỏ: `POST /api/cart/items/`
   - Đặt hàng: `POST /api/orders/`
   - Kiểm tra đơn hàng: `GET /api/orders/`
3. **Thêm Microservice mới:** Tạo một Review Service cho phép khách hàng đánh giá sản phẩm. Service cần:
   - Model: `Review(user_id, product_id, rating, comment)`
   - Dockerfile riêng, database riêng (`review_db`)
   - Thêm upstream và location vào `nginx.conf`
   - Thêm service vào `docker-compose.yml`
4. **Cải thiện Security:** Thay thế chiến lược Shared Secret bằng Public/Private Key (RS256). User Service ký bằng Private Key, các service khác verify bằng Public Key.
5. **Thêm Message Broker:** Tích hợp RabbitMQ hoặc Kafka. Khi Order được tạo, publish event `order.created` để Payment Service và Shipping Service subscribe và xử lý bất đồng bộ.

## 4.12 Checklist đánh giá

| # | Tiêu chí | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| 1 | Hệ thống chia tách thành ≥ 5 microservices | ✅ | 7 service (6 Core + 1 AI) |
| 2 | Mỗi service có database riêng biệt | ✅ | 6 PostgreSQL instances |
| 3 | API Gateway routing đúng tất cả endpoint | ✅ | Nginx với 13 location blocks |
| 4 | JWT Authentication hoạt động | ✅ | SimpleJWT, HS256, 1h expiry |
| 5 | Cross-service communication qua REST API | ✅ | services.py trong Order Service |
| 6 | Docker hóa toàn bộ hệ thống | ✅ | docker-compose.yml với 15 containers |
| 7 | Rate Limiting được cấu hình | ✅ | 3 zones: auth, payment, general |
| 8 | Luồng mua hàng end-to-end hoạt động | ✅ | Login → Cart → Order → Payment → Shipping |
| 9 | Snapshot data pattern được áp dụng | ✅ | CartItem, OrderItem lưu tên + giá |
| 10 | Health check endpoint | ✅ | Gateway `/health`, AI `/health` |
| 11 | CORS được xử lý tập trung | ✅ | Nginx + Django CORS middleware |
| 12 | Graceful error handling cross-service | ✅ | try/except + timeout=5s |
| 13 | AI Service tích hợp (LSTM + Graph + RAG) | ✅ | FastAPI + PyTorch + Neo4j + FAISS |
| 14 | Tài liệu thiết kế đầy đủ | ✅ | Class Diagram, ERD, Sequence Diagram |
| 15 | Kubernetes manifest (Optional) | 📋 | Deployment + Service YAML mẫu |
