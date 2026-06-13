import uuid
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.shipping.models import Shipment, TrackingEvent


class Command(BaseCommand):
    help = 'Seed sample shipping data for testing'

    def handle(self, *args, **options):
        if Shipment.objects.exists():
            self.stdout.write(self.style.WARNING('Shipments already seeded. Skipping.'))
            return

        now = timezone.now()
        today = date.today()

        shipments_data = [
            # Shipment 1 - Order 1 (delivered)
            {
                'order_id': 1,
                'tracking_number': f'GHN{uuid.uuid4().hex[:10].upper()}',
                'provider': 'ghn', 'status': 'delivered',
                'shipping_address': {
                    'name': 'Nguyễn Văn A', 'phone': '0912345001',
                    'address': '12 Trần Hưng Đạo', 'district': 'Quận 5',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 7'
                },
                'estimated_delivery': today - timedelta(days=1),
                'actual_delivery': now - timedelta(days=1),
                'shipping_fee': 30000,
                'events': [
                    {'status': 'pending', 'location': 'Kho TP.HCM', 'description': 'Đơn hàng được tạo'},
                    {'status': 'picked_up', 'location': 'Kho TP.HCM', 'description': 'Shipper đã lấy hàng'},
                    {'status': 'in_transit', 'location': 'Trung tâm phân loại Q.Tân Bình', 'description': 'Đang vận chuyển'},
                    {'status': 'out_for_delivery', 'location': 'Quận 5, TP.HCM', 'description': 'Đang giao hàng'},
                    {'status': 'delivered', 'location': '12 Trần Hưng Đạo, Q.5', 'description': 'Giao hàng thành công'},
                ],
            },
            # Shipment 2 - Order 2 (in_transit)
            {
                'order_id': 2,
                'tracking_number': f'GHTK{uuid.uuid4().hex[:10].upper()}',
                'provider': 'ghtk', 'status': 'in_transit',
                'shipping_address': {
                    'name': 'Trần Thị B', 'phone': '0912345002',
                    'address': '34 Lý Thường Kiệt', 'district': 'Quận 10',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 14'
                },
                'estimated_delivery': today + timedelta(days=1),
                'shipping_fee': 0,
                'notes': 'Miễn phí vận chuyển đơn trên 5 triệu',
                'events': [
                    {'status': 'pending', 'location': 'Kho TP.HCM', 'description': 'Đơn hàng được tạo'},
                    {'status': 'picked_up', 'location': 'Kho Quận 1', 'description': 'Đã lấy hàng tại kho'},
                    {'status': 'in_transit', 'location': 'Trung tâm chia chọn Thủ Đức', 'description': 'Đang trung chuyển'},
                ],
            },
            # Shipment 3 - Order 4 (out_for_delivery)
            {
                'order_id': 4,
                'tracking_number': f'VNP{uuid.uuid4().hex[:10].upper()}',
                'provider': 'vnpost', 'status': 'out_for_delivery',
                'shipping_address': {
                    'name': 'Phạm Thị D', 'phone': '0912345004',
                    'address': '78 Nguyễn Văn Cừ', 'district': 'Quận 5',
                    'city': 'TP. Hồ Chí Minh', 'ward': 'Phường 4'
                },
                'estimated_delivery': today,
                'shipping_fee': 20000,
                'events': [
                    {'status': 'pending', 'location': 'Bưu cục Quận 1', 'description': 'Tiếp nhận đơn hàng'},
                    {'status': 'picked_up', 'location': 'Bưu cục Quận 1', 'description': 'Đã lấy hàng'},
                    {'status': 'in_transit', 'location': 'Bưu cục trung tâm', 'description': 'Đang xử lý tại bưu cục'},
                    {'status': 'out_for_delivery', 'location': 'Quận 5, TP.HCM', 'description': 'Bưu tá đang giao hàng'},
                ],
            },
        ]

        for data in shipments_data:
            events = data.pop('events')
            shipment = Shipment.objects.create(**data)

            for event in events:
                TrackingEvent.objects.create(shipment=shipment, **event)

            self.stdout.write(
                f'  Shipment#{shipment.id} order={shipment.order_id} '
                f'{shipment.provider} [{shipment.status}] tracking={shipment.tracking_number}'
            )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {Shipment.objects.count()} shipments with '
            f'{TrackingEvent.objects.count()} tracking events'
        ))
