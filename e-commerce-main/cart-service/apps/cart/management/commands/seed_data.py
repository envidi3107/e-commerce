from django.core.management.base import BaseCommand
from apps.cart.models import Cart, CartItem


class Command(BaseCommand):
    help = 'Seed sample cart data for testing'

    def handle(self, *args, **options):
        if Cart.objects.exists():
            self.stdout.write(self.style.WARNING('Carts already seeded. Skipping.'))
            return

        carts_data = [
            {
                'user_id': 3,  # customer1
                'items': [
                    {'product_id': 1, 'product_name': 'iPhone 15 Pro Max 256GB',
                     'product_price': 34990000, 'product_thumbnail': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400', 'quantity': 1},
                    {'product_id': 18, 'product_name': 'Serum Vitamin C 20% Brightening',
                     'product_price': 350000, 'product_thumbnail': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400', 'quantity': 2},
                ],
            },
            {
                'user_id': 4,  # customer2
                'items': [
                    {'product_id': 6, 'product_name': 'Áo Polo Nam Premium Cotton',
                     'product_price': 450000, 'product_thumbnail': 'https://images.unsplash.com/photo-1625910513413-5fc42d5b1900?w=400', 'quantity': 3},
                    {'product_id': 7, 'product_name': 'Quần Jeans Nam Slim Fit',
                     'product_price': 690000, 'product_thumbnail': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400', 'quantity': 2},
                    {'product_id': 13, 'product_name': 'Đắc Nhân Tâm',
                     'product_price': 86000, 'product_thumbnail': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400', 'quantity': 1},
                ],
            },
            {
                'user_id': 5,  # customer3
                'items': [
                    {'product_id': 3, 'product_name': 'MacBook Air M3 15 inch',
                     'product_price': 37990000, 'product_thumbnail': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400', 'quantity': 1},
                    {'product_id': 17, 'product_name': 'Thảm Yoga TPE 6mm',
                     'product_price': 390000, 'product_thumbnail': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400', 'quantity': 1},
                ],
            },
        ]

        for cart_data in carts_data:
            cart = Cart.objects.create(user_id=cart_data['user_id'])
            for item_data in cart_data['items']:
                CartItem.objects.create(cart=cart, **item_data)
            self.stdout.write(f'  Cart for user_id={cart.user_id}: {cart.items.count()} items')

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {Cart.objects.count()} carts with {CartItem.objects.count()} items'
        ))
