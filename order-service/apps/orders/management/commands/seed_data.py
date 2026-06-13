from django.core.management.base import BaseCommand
from apps.orders.models import Order, OrderItem, OrderStatusHistory


class Command(BaseCommand):
    help = 'Seed sample order data for testing'

    def handle(self, *args, **options):
        if Order.objects.exists():
            self.stdout.write(self.style.WARNING('Orders already seeded. Skipping.'))
            return

        orders_data = [
            # Order 1 - Delivered
            {
                'user_id': 3, 'status': 'delivered', 'payment_method': 'bank', 'payment_status': 'paid',
                'shipping_address': {
                    'name': 'Nguyễn Văn A', 'phone': '0912345001',
                    'address': '12 Trần Hưng Đạo', 'district': 'Quận 5',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 7'
                },
                'subtotal': 9480000, 'shipping_fee': 30000, 'discount': 200000, 'total': 9310000,
                'payment_id': 1, 'shipment_id': 1,
                'items': [
                    {'product_id': 4, 'product_name': 'Sony WH-1000XM5 Headphones', 'product_sku': 'ELEC-SONY-XM5',
                     'unit_price': 8490000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400'},
                    {'product_id': 7, 'product_name': 'Quần Jeans Nam Slim Fit', 'product_sku': 'FASH-JEAN-001',
                     'unit_price': 690000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'},
                    {'product_id': 19, 'product_name': 'Kem Chống Nắng SPF50+ PA++++', 'product_sku': 'BEAU-SUN-SPF50',
                     'unit_price': 290000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400'},
                ],
                'history': [
                    {'status': 'pending', 'note': 'Đơn hàng được tạo'},
                    {'status': 'confirmed', 'note': 'Đã xác nhận thanh toán'},
                    {'status': 'processing', 'note': 'Đang chuẩn bị hàng'},
                    {'status': 'shipped', 'note': 'Đã giao cho đơn vị vận chuyển'},
                    {'status': 'delivered', 'note': 'Giao hàng thành công'},
                ],
            },
            # Order 2 - Processing
            {
                'user_id': 4, 'status': 'processing', 'payment_method': 'ewallet', 'payment_status': 'paid',
                'shipping_address': {
                    'name': 'Trần Thị B', 'phone': '0912345002',
                    'address': '34 Lý Thường Kiệt', 'district': 'Quận 10',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 14'
                },
                'subtotal': 38880000, 'shipping_fee': 0, 'discount': 500000, 'total': 38380000,
                'payment_id': 2, 'shipment_id': 2,
                'items': [
                    {'product_id': 3, 'product_name': 'MacBook Air M3 15 inch', 'product_sku': 'ELEC-MBA-M3-15',
                     'unit_price': 37990000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400'},
                    {'product_id': 6, 'product_name': 'Áo Polo Nam Premium Cotton', 'product_sku': 'FASH-POLO-001',
                     'unit_price': 450000, 'quantity': 2,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1625910513413-5fc42d5b1900?w=400'},
                ],
                'history': [
                    {'status': 'pending', 'note': 'Đơn hàng được tạo'},
                    {'status': 'confirmed', 'note': 'Thanh toán MoMo thành công'},
                    {'status': 'processing', 'note': 'Đang đóng gói'},
                ],
            },
            # Order 3 - Pending (COD)
            {
                'user_id': 5, 'status': 'pending', 'payment_method': 'cod', 'payment_status': 'unpaid',
                'shipping_address': {
                    'name': 'Lê Văn C', 'phone': '0912345003',
                    'address': '56 Điện Biên Phủ', 'district': 'Quận Bình Thạnh',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 15'
                },
                'subtotal': 1976000, 'shipping_fee': 25000, 'discount': 0, 'total': 2001000,
                'items': [
                    {'product_id': 10, 'product_name': 'Nồi Chiên Không Dầu 6.5L', 'product_sku': 'HOME-AIRFR-001',
                     'unit_price': 1890000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1648664879170-a960e4b4aab0?w=400'},
                    {'product_id': 13, 'product_name': 'Đắc Nhân Tâm', 'product_sku': 'BOOK-DNT-001',
                     'unit_price': 86000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400'},
                ],
                'history': [
                    {'status': 'pending', 'note': 'Đơn hàng COD được tạo'},
                ],
            },
            # Order 4 - Shipped
            {
                'user_id': 6, 'status': 'shipped', 'payment_method': 'bank', 'payment_status': 'paid',
                'shipping_address': {
                    'name': 'Phạm Thị D', 'phone': '0912345004',
                    'address': '78 Nguyễn Văn Cừ', 'district': 'Quận 5',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 4'
                },
                'subtotal': 2180000, 'shipping_fee': 20000, 'discount': 100000, 'total': 2100000,
                'payment_id': 3, 'shipment_id': 3,
                'items': [
                    {'product_id': 8, 'product_name': 'Giày Sneaker Nữ Classic', 'product_sku': 'FASH-SNKR-001',
                     'unit_price': 1290000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400'},
                    {'product_id': 9, 'product_name': 'Đầm Nữ Công Sở Thanh Lịch', 'product_sku': 'FASH-DRESS-001',
                     'unit_price': 890000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400'},
                ],
                'history': [
                    {'status': 'pending', 'note': 'Đơn hàng được tạo'},
                    {'status': 'confirmed', 'note': 'Đã xác nhận chuyển khoản'},
                    {'status': 'processing', 'note': 'Đang chuẩn bị hàng'},
                    {'status': 'shipped', 'note': 'Đã giao cho GHN'},
                ],
            },
            # Order 5 - Cancelled
            {
                'user_id': 7, 'status': 'cancelled', 'payment_method': 'ewallet', 'payment_status': 'refunded',
                'shipping_address': {
                    'name': 'Hoàng Văn E', 'phone': '0912345005',
                    'address': '90 Cách Mạng Tháng 8', 'district': 'Quận 3',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 5'
                },
                'subtotal': 31990000, 'shipping_fee': 0, 'discount': 0, 'total': 31990000,
                'payment_id': 4,
                'items': [
                    {'product_id': 2, 'product_name': 'Samsung Galaxy S24 Ultra', 'product_sku': 'ELEC-SGS24U-256',
                     'unit_price': 31990000, 'quantity': 1,
                     'product_thumbnail': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400'},
                ],
                'history': [
                    {'status': 'pending', 'note': 'Đơn hàng được tạo'},
                    {'status': 'confirmed', 'note': 'Thanh toán ZaloPay thành công'},
                    {'status': 'cancelled', 'note': 'Khách hàng yêu cầu hủy đơn'},
                ],
            },
        ]

        for data in orders_data:
            items = data.pop('items')
            history = data.pop('history')
            order = Order.objects.create(**data)

            for item_data in items:
                item_data['subtotal'] = item_data['unit_price'] * item_data['quantity']
                OrderItem.objects.create(order=order, **item_data)

            for h in history:
                OrderStatusHistory.objects.create(order=order, **h)

            self.stdout.write(f'  Order#{order.id} user={order.user_id} status={order.status} total={order.total:,.0f}đ')

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {Order.objects.count()} orders with '
            f'{OrderItem.objects.count()} items'
        ))
