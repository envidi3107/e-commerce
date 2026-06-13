from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.text import slugify
import uuid

from .models import Category, Product, Inventory
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductWriteSerializer, InventorySerializer, InventoryUpdateSerializer,
)


def is_staff_or_admin(user):
    return user.is_authenticated and getattr(user, 'role', None) in ('admin', 'staff')


# ─────────────────────────────────────────────
# Category Views
# ─────────────────────────────────────────────

class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cats = Category.objects.filter(is_active=True)
        return Response(CategorySerializer(cats, many=True).data)

    def post(self, request):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        cat = self.get_object(pk)
        if not cat:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CategorySerializer(cat).data)

    def put(self, request, pk):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        cat = self.get_object(pk)
        if not cat:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(cat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# Product Views
# ─────────────────────────────────────────────

class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.select_related('category').prefetch_related('images', 'inventory')

        # Filters
        category   = request.query_params.get('category')
        status_f   = request.query_params.get('status', 'active')
        min_price  = request.query_params.get('min_price')
        max_price  = request.query_params.get('max_price')
        search     = request.query_params.get('search')
        ordering   = request.query_params.get('ordering', '-created_at')

        if category:
            products = products.filter(category__code=category)
        if status_f:
            products = products.filter(status=status_f)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if search:
            products = products.filter(name__icontains=search) | products.filter(description__icontains=search)

        allowed_orderings = ['price', '-price', 'name', '-name', '-created_at', 'rating_avg', '-rating_avg']
        if ordering in allowed_orderings:
            products = products.order_by(ordering)

        # Pagination
        page      = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        total     = products.count()
        start     = (page - 1) * page_size
        end       = start + page_size
        products  = products[start:end]

        return Response({
            'count':     total,
            'page':      page,
            'page_size': page_size,
            'results':   ProductSerializer(products, many=True).data,
        })

    def post(self, request):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        if not data.get('slug'):
            data['slug'] = slugify(data.get('name', '')) + '-' + str(uuid.uuid4())[:8]
        serializer = ProductWriteSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Product.objects.select_related('category').prefetch_related('images', 'inventory').get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product).data)

    def put(self, request, pk):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        if not product:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductWriteSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ProductSerializer(product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        if not product:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        product.status = 'inactive'
        product.save()
        return Response({'message': 'Product deactivated.'})


# ─────────────────────────────────────────────
# Inventory Views
# ─────────────────────────────────────────────

class InventoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        try:
            inv = Inventory.objects.get(product_id=product_id)
        except Inventory.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(InventorySerializer(inv).data)

    def put(self, request, product_id):
        if not is_staff_or_admin(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            inv = Inventory.objects.get(product_id=product_id)
        except Inventory.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = InventoryUpdateSerializer(inv, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(InventorySerializer(inv).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryBulkCheckView(APIView):
    """Internal endpoint: check availability for a list of product IDs."""
    permission_classes = [AllowAny]

    def post(self, request):
        product_ids = request.data.get('product_ids', [])
        items = []
        for pid in product_ids:
            try:
                inv = Inventory.objects.get(product_id=pid)
                items.append({'product_id': pid, 'available': inv.available})
            except Inventory.DoesNotExist:
                items.append({'product_id': pid, 'available': 0})
        return Response(items)
