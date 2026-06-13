from django.core.management.base import BaseCommand
from apps.products.models import Category, Product, ProductImage, Inventory


class Command(BaseCommand):
    help = 'Seed sample products for testing'

    def handle(self, *args, **options):
        if Product.objects.exists():
            self.stdout.write(self.style.WARNING('Products already seeded. Skipping.'))
            return

        # ── Categories ──────────────────────────────────────────
        categories_data = [
            {'name': 'Electronics',          'slug': 'electronics',   'code': 'electronics',
             'description': 'Điện thoại, laptop, phụ kiện công nghệ',
             'image': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400'},
            {'name': 'Fashion',              'slug': 'fashion',       'code': 'fashion',
             'description': 'Thời trang nam nữ, giày dép, phụ kiện',
             'image': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=400'},
            {'name': 'Home & Living',        'slug': 'home-living',   'code': 'home_living',
             'description': 'Nội thất, đồ gia dụng, trang trí nhà cửa',
             'image': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400'},
            {'name': 'Books',                'slug': 'books',         'code': 'books',
             'description': 'Sách văn học, kinh tế, kỹ năng sống',
             'image': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400'},
            {'name': 'Sports',               'slug': 'sports',        'code': 'sports',
             'description': 'Dụng cụ thể thao, gym, outdoor',
             'image': 'https://images.unsplash.com/photo-1461896836934-bd45ba8a0936?w=400'},
            {'name': 'Beauty & Personal Care','slug': 'beauty',       'code': 'beauty',
             'description': 'Mỹ phẩm, chăm sóc da, nước hoa',
             'image': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400'},
        ]
        cats = {}
        for data in categories_data:
            cat = Category.objects.create(**data)
            cats[cat.code] = cat
            self.stdout.write(f'  Category: {cat.name}')

        # ── Products ────────────────────────────────────────────
        products_data = [
            # Electronics
            {'category': cats['electronics'], 'name': 'iPhone 15 Pro Max 256GB', 'slug': 'iphone-15-pro-max-256gb',
             'price': 34990000, 'compare_price': 36990000, 'sku': 'ELEC-IP15PM-256',
             'description': 'iPhone 15 Pro Max với chip A17 Pro, camera 48MP, khung titanium.',
             'thumbnail': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400',
             'rating_avg': 4.8, 'rating_count': 256,
             'attributes': {'brand': 'Apple', 'warranty_months': 12, 'model': 'A3106', 'color': 'Natural Titanium', 'storage': '256GB'}},

            {'category': cats['electronics'], 'name': 'Samsung Galaxy S24 Ultra', 'slug': 'samsung-galaxy-s24-ultra',
             'price': 31990000, 'compare_price': 33990000, 'sku': 'ELEC-SGS24U-256',
             'description': 'Galaxy S24 Ultra với Galaxy AI, S Pen tích hợp, camera 200MP.',
             'thumbnail': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400',
             'rating_avg': 4.7, 'rating_count': 189,
             'attributes': {'brand': 'Samsung', 'warranty_months': 12, 'model': 'SM-S928B', 'color': 'Titanium Gray', 'storage': '256GB'}},

            {'category': cats['electronics'], 'name': 'MacBook Air M3 15 inch', 'slug': 'macbook-air-m3-15',
             'price': 37990000, 'compare_price': 39990000, 'sku': 'ELEC-MBA-M3-15',
             'description': 'MacBook Air 15 inch chip M3, 16GB RAM, 512GB SSD, pin 18 giờ.',
             'thumbnail': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
             'rating_avg': 4.9, 'rating_count': 134,
             'attributes': {'brand': 'Apple', 'warranty_months': 12, 'model': 'MXCQ3', 'ram': '16GB', 'storage': '512GB SSD'}},

            {'category': cats['electronics'], 'name': 'Sony WH-1000XM5 Headphones', 'slug': 'sony-wh1000xm5',
             'price': 8490000, 'compare_price': 9990000, 'sku': 'ELEC-SONY-XM5',
             'description': 'Tai nghe chống ồn hàng đầu với âm thanh Hi-Res, pin 30 giờ.',
             'thumbnail': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400',
             'rating_avg': 4.6, 'rating_count': 312,
             'attributes': {'brand': 'Sony', 'warranty_months': 12, 'type': 'Over-ear', 'connectivity': 'Bluetooth 5.2'}},

            {'category': cats['electronics'], 'name': 'iPad Air M2 11 inch', 'slug': 'ipad-air-m2-11',
             'price': 18990000, 'compare_price': 19990000, 'sku': 'ELEC-IPAD-AIR-M2',
             'description': 'iPad Air chip M2, màn hình Liquid Retina 11 inch, hỗ trợ Apple Pencil Pro.',
             'thumbnail': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400',
             'rating_avg': 4.7, 'rating_count': 98,
             'attributes': {'brand': 'Apple', 'warranty_months': 12, 'storage': '128GB', 'color': 'Space Gray'}},

            # Fashion
            {'category': cats['fashion'], 'name': 'Áo Polo Nam Premium Cotton', 'slug': 'ao-polo-nam-premium',
             'price': 450000, 'compare_price': 650000, 'sku': 'FASH-POLO-001',
             'description': 'Áo polo nam chất liệu cotton cao cấp, form regular fit thoải mái.',
             'thumbnail': 'https://images.unsplash.com/photo-1625910513413-5fc42d5b1900?w=400',
             'rating_avg': 4.5, 'rating_count': 423,
             'attributes': {'sizes': ['S', 'M', 'L', 'XL', 'XXL'], 'colors': ['Trắng', 'Đen', 'Navy', 'Xám'], 'material': '100% Cotton'}},

            {'category': cats['fashion'], 'name': 'Quần Jeans Nam Slim Fit', 'slug': 'quan-jeans-nam-slim',
             'price': 690000, 'compare_price': 890000, 'sku': 'FASH-JEAN-001',
             'description': 'Quần jeans nam slim fit co giãn 4 chiều, thoải mái vận động.',
             'thumbnail': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400',
             'rating_avg': 4.4, 'rating_count': 287,
             'attributes': {'sizes': ['28', '29', '30', '31', '32', '33', '34'], 'colors': ['Xanh đậm', 'Xanh nhạt', 'Đen'], 'material': 'Denim co giãn'}},

            {'category': cats['fashion'], 'name': 'Giày Sneaker Nữ Classic', 'slug': 'giay-sneaker-nu-classic',
             'price': 1290000, 'compare_price': 1590000, 'sku': 'FASH-SNKR-001',
             'description': 'Giày sneaker nữ phong cách classic, đế cao su chống trượt.',
             'thumbnail': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400',
             'rating_avg': 4.6, 'rating_count': 156,
             'attributes': {'sizes': ['36', '37', '38', '39', '40'], 'colors': ['Trắng', 'Đen', 'Hồng'], 'material': 'Da PU'}},

            {'category': cats['fashion'], 'name': 'Đầm Nữ Công Sở Thanh Lịch', 'slug': 'dam-nu-cong-so',
             'price': 890000, 'compare_price': 1190000, 'sku': 'FASH-DRESS-001',
             'description': 'Đầm công sở nữ thiết kế thanh lịch, chất liệu vải cao cấp.',
             'thumbnail': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400',
             'rating_avg': 4.3, 'rating_count': 178,
             'attributes': {'sizes': ['S', 'M', 'L', 'XL'], 'colors': ['Đen', 'Navy', 'Đỏ đô'], 'material': 'Polyester cao cấp'}},

            # Home & Living
            {'category': cats['home_living'], 'name': 'Nồi Chiên Không Dầu 6.5L', 'slug': 'noi-chien-khong-dau-6l',
             'price': 1890000, 'compare_price': 2490000, 'sku': 'HOME-AIRFR-001',
             'description': 'Nồi chiên không dầu dung tích 6.5L, 8 chế độ nấu, màn hình cảm ứng.',
             'thumbnail': 'https://images.unsplash.com/photo-1648664879170-a960e4b4aab0?w=400',
             'rating_avg': 4.5, 'rating_count': 534,
             'attributes': {'brand': 'Lock&Lock', 'power': '1800W', 'capacity': '6.5L', 'warranty_months': 24}},

            {'category': cats['home_living'], 'name': 'Bộ Chăn Ga Gối Cotton Lụa', 'slug': 'bo-chan-ga-goi-cotton-lua',
             'price': 1490000, 'compare_price': 1990000, 'sku': 'HOME-BEDSET-001',
             'description': 'Bộ chăn ga gối cotton lụa mềm mịn, nhiều họa tiết sang trọng.',
             'thumbnail': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400',
             'rating_avg': 4.7, 'rating_count': 245,
             'attributes': {'sizes': ['1m6', '1m8', '2m'], 'material': 'Cotton lụa 400TC'}},

            {'category': cats['home_living'], 'name': 'Đèn LED Thông Minh Xiaomi', 'slug': 'den-led-thong-minh-xiaomi',
             'price': 790000, 'compare_price': 990000, 'sku': 'HOME-LED-001',
             'description': 'Đèn LED thông minh điều khiển qua app, 16 triệu màu, tương thích Google Home.',
             'thumbnail': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
             'rating_avg': 4.4, 'rating_count': 167,
             'attributes': {'brand': 'Xiaomi', 'power': '9W', 'connectivity': 'WiFi + Bluetooth', 'warranty_months': 12}},

            # Books
            {'category': cats['books'], 'name': 'Đắc Nhân Tâm', 'slug': 'dac-nhan-tam',
             'price': 86000, 'compare_price': 108000, 'sku': 'BOOK-DNT-001',
             'description': 'Cuốn sách kinh điển về nghệ thuật giao tiếp và ứng xử của Dale Carnegie.',
             'thumbnail': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400',
             'rating_avg': 4.8, 'rating_count': 1523,
             'attributes': {'author': 'Dale Carnegie', 'publisher': 'NXB Tổng hợp TP.HCM', 'pages': 320, 'isbn': '978-604-74-6731-2'}},

            {'category': cats['books'], 'name': 'Nhà Giả Kim', 'slug': 'nha-gia-kim',
             'price': 69000, 'compare_price': 79000, 'sku': 'BOOK-NGK-001',
             'description': 'Tiểu thuyết triết lý nổi tiếng của Paulo Coelho về hành trình tìm kiếm ước mơ.',
             'thumbnail': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400',
             'rating_avg': 4.7, 'rating_count': 2108,
             'attributes': {'author': 'Paulo Coelho', 'publisher': 'NXB Hội Nhà Văn', 'pages': 228, 'isbn': '978-604-77-0257-6'}},

            {'category': cats['books'], 'name': 'Atomic Habits - Thay Đổi Tí Hon Hiệu Quả Bất Ngờ', 'slug': 'atomic-habits',
             'price': 149000, 'compare_price': 199000, 'sku': 'BOOK-AH-001',
             'description': 'Phương pháp xây dựng thói quen tốt và loại bỏ thói quen xấu của James Clear.',
             'thumbnail': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=400',
             'rating_avg': 4.9, 'rating_count': 876,
             'attributes': {'author': 'James Clear', 'publisher': 'NXB Thế Giới', 'pages': 360, 'isbn': '978-604-77-6466-6'}},

            # Sports
            {'category': cats['sports'], 'name': 'Bộ Tạ Tay Cao Su 20kg', 'slug': 'bo-ta-tay-20kg',
             'price': 890000, 'compare_price': 1190000, 'sku': 'SPRT-DUMB-20',
             'description': 'Bộ tạ tay bọc cao su cao cấp, bao gồm 2 đòn tạ và đĩa tạ 20kg.',
             'thumbnail': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400',
             'rating_avg': 4.5, 'rating_count': 289,
             'attributes': {'weight': '20kg', 'material': 'Thép bọc cao su', 'includes': '2 đòn tạ + 8 đĩa tạ'}},

            {'category': cats['sports'], 'name': 'Thảm Yoga TPE 6mm', 'slug': 'tham-yoga-tpe-6mm',
             'price': 390000, 'compare_price': 490000, 'sku': 'SPRT-YOGA-001',
             'description': 'Thảm yoga TPE 2 lớp chống trượt, thân thiện môi trường, kèm túi đựng.',
             'thumbnail': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400',
             'rating_avg': 4.6, 'rating_count': 445,
             'attributes': {'material': 'TPE', 'thickness': '6mm', 'size': '183x61cm', 'includes': 'Túi đựng + dây buộc'}},

            # Beauty
            {'category': cats['beauty'], 'name': 'Serum Vitamin C 20% Brightening', 'slug': 'serum-vitamin-c-20',
             'price': 350000, 'compare_price': 450000, 'sku': 'BEAU-SER-VC20',
             'description': 'Serum Vitamin C nồng độ 20% giúp sáng da, mờ thâm, chống oxy hóa.',
             'thumbnail': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400',
             'rating_avg': 4.5, 'rating_count': 678,
             'attributes': {'volume': '30ml', 'skin_type': 'Mọi loại da', 'origin': 'Hàn Quốc'}},

            {'category': cats['beauty'], 'name': 'Kem Chống Nắng SPF50+ PA++++', 'slug': 'kem-chong-nang-spf50',
             'price': 290000, 'compare_price': 380000, 'sku': 'BEAU-SUN-SPF50',
             'description': 'Kem chống nắng phổ rộng SPF50+ PA++++, kiềm dầu, không gây nhờn.',
             'thumbnail': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400',
             'rating_avg': 4.7, 'rating_count': 934,
             'attributes': {'volume': '50ml', 'spf': '50+', 'skin_type': 'Da dầu / Da hỗn hợp', 'origin': 'Nhật Bản'}},
        ]

        for data in products_data:
            product = Product.objects.create(**data)
            # Create inventory
            Inventory.objects.create(
                product=product,
                quantity=100,
                reserved=0,
                low_stock_threshold=10
            )
            self.stdout.write(f'  Product: {product.name} ({product.sku})')

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {Category.objects.count()} categories, '
            f'{Product.objects.count()} products with inventory'
        ))
