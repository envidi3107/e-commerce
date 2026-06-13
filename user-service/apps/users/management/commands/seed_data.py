from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Seed sample users for testing'

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write(self.style.WARNING('Users already seeded. Skipping.'))
            return

        # Admin
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@ecommerce.vn',
            password='admin123',
            role='admin',
            phone='0901000001',
            address='123 Nguyễn Huệ, Quận 1, TP.HCM',
        )
        self.stdout.write(f'  Created admin: {admin.email}')

        # Staff
        staff_data = [
            {'username': 'staff1', 'email': 'staff1@ecommerce.vn', 'phone': '0901000002',
             'first_name': 'Minh', 'last_name': 'Trần', 'address': '456 Lê Lợi, Quận 1, TP.HCM'},
            {'username': 'staff2', 'email': 'staff2@ecommerce.vn', 'phone': '0901000003',
             'first_name': 'Hương', 'last_name': 'Nguyễn', 'address': '789 Hai Bà Trưng, Quận 3, TP.HCM'},
        ]
        for data in staff_data:
            u = User.objects.create_user(password='staff123', role='staff', **data)
            self.stdout.write(f'  Created staff: {u.email}')

        # Customers
        customers = [
            {'username': 'customer1', 'email': 'nguyenvana@gmail.com', 'phone': '0912345001',
             'first_name': 'Văn A', 'last_name': 'Nguyễn', 'address': '12 Trần Hưng Đạo, Quận 5, TP.HCM'},
            {'username': 'customer2', 'email': 'tranthib@gmail.com', 'phone': '0912345002',
             'first_name': 'Thị B', 'last_name': 'Trần', 'address': '34 Lý Thường Kiệt, Quận 10, TP.HCM'},
            {'username': 'customer3', 'email': 'levanc@gmail.com', 'phone': '0912345003',
             'first_name': 'Văn C', 'last_name': 'Lê', 'address': '56 Điện Biên Phủ, Quận Bình Thạnh, TP.HCM'},
            {'username': 'customer4', 'email': 'phamthid@gmail.com', 'phone': '0912345004',
             'first_name': 'Thị D', 'last_name': 'Phạm', 'address': '78 Nguyễn Văn Cừ, Quận 5, TP.HCM'},
            {'username': 'customer5', 'email': 'hoangvane@gmail.com', 'phone': '0912345005',
             'first_name': 'Văn E', 'last_name': 'Hoàng', 'address': '90 Cách Mạng Tháng 8, Quận 3, TP.HCM'},
            {'username': 'customer6', 'email': 'vuthif@gmail.com', 'phone': '0912345006',
             'first_name': 'Thị F', 'last_name': 'Vũ', 'address': '21 Pasteur, Quận 1, TP.HCM'},
            {'username': 'customer7', 'email': 'dangvang@gmail.com', 'phone': '0912345007',
             'first_name': 'Văn G', 'last_name': 'Đặng', 'address': '43 Võ Văn Tần, Quận 3, TP.HCM'},
            {'username': 'customer8', 'email': 'buithih@gmail.com', 'phone': '0912345008',
             'first_name': 'Thị H', 'last_name': 'Bùi', 'address': '65 Nam Kỳ Khởi Nghĩa, Quận 1, TP.HCM'},
        ]
        for data in customers:
            u = User.objects.create_user(password='customer123', role='customer', **data)
            self.stdout.write(f'  Created customer: {u.email}')

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {User.objects.count()} users '
            f'(1 admin, 2 staff, {len(customers)} customers)'
        ))
