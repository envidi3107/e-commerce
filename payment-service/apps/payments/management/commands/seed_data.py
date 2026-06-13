import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.payments.models import Payment, Transaction


class Command(BaseCommand):
    help = 'Seed sample payment data for testing'

    def handle(self, *args, **options):
        if Payment.objects.exists():
            self.stdout.write(self.style.WARNING('Payments already seeded. Skipping.'))
            return

        now = timezone.now()

        payments_data = [
            # Payment 1 - Order 1 (delivered, bank transfer, success)
            {
                'order_id': 1, 'user_id': 3, 'amount': 9310000,
                'payment_method': 'bank', 'status': 'success',
                'transaction_ref': f'PAY-{uuid.uuid4().hex[:12].upper()}',
                'gateway_response': {'bank': 'Vietcombank', 'account': '****6789', 'transfer_id': 'VCB20260510001'},
                'paid_at': now - timedelta(days=5),
                'transactions': [
                    {'type': 'charge', 'amount': 9310000, 'note': 'Chuyển khoản Vietcombank thành công'},
                ],
            },
            # Payment 2 - Order 2 (processing, ewallet, success)
            {
                'order_id': 2, 'user_id': 4, 'amount': 38380000,
                'payment_method': 'ewallet', 'status': 'success',
                'transaction_ref': f'PAY-{uuid.uuid4().hex[:12].upper()}',
                'gateway_response': {'wallet': 'MoMo', 'phone': '****5002', 'momo_ref': 'MOMO20260511001'},
                'paid_at': now - timedelta(days=3),
                'transactions': [
                    {'type': 'charge', 'amount': 38380000, 'note': 'Thanh toán MoMo thành công'},
                ],
            },
            # Payment 3 - Order 4 (shipped, bank transfer, success)
            {
                'order_id': 4, 'user_id': 6, 'amount': 2100000,
                'payment_method': 'bank', 'status': 'success',
                'transaction_ref': f'PAY-{uuid.uuid4().hex[:12].upper()}',
                'gateway_response': {'bank': 'Techcombank', 'account': '****1234', 'transfer_id': 'TCB20260512001'},
                'paid_at': now - timedelta(days=2),
                'transactions': [
                    {'type': 'charge', 'amount': 2100000, 'note': 'Chuyển khoản Techcombank thành công'},
                ],
            },
            # Payment 4 - Order 5 (cancelled, ewallet, refunded)
            {
                'order_id': 5, 'user_id': 7, 'amount': 31990000,
                'payment_method': 'ewallet', 'status': 'refunded',
                'transaction_ref': f'PAY-{uuid.uuid4().hex[:12].upper()}',
                'gateway_response': {'wallet': 'ZaloPay', 'phone': '****5005', 'zalo_ref': 'ZLP20260511002'},
                'paid_at': now - timedelta(days=4),
                'transactions': [
                    {'type': 'charge', 'amount': 31990000, 'note': 'Thanh toán ZaloPay thành công'},
                    {'type': 'refund', 'amount': 31990000, 'note': 'Hoàn tiền do khách hủy đơn'},
                ],
            },
        ]

        for data in payments_data:
            txns = data.pop('transactions')
            payment = Payment.objects.create(**data)

            for txn in txns:
                txn['reference'] = f'TXN-{uuid.uuid4().hex[:12].upper()}'
                Transaction.objects.create(payment=payment, **txn)

            self.stdout.write(
                f'  Payment#{payment.id} order={payment.order_id} '
                f'{payment.payment_method} {payment.status} {payment.amount:,.0f}đ'
            )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {Payment.objects.count()} payments with '
            f'{Transaction.objects.count()} transactions'
        ))
