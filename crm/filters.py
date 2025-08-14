import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr='icontains')
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    phone = django_filters.CharFilter(method='filter_phone_pattern')

    class Meta:
        model = Customer
        fields = {
            "name": ["icontains"],
            "email": ["icontains"],
            "phone": ["exact", "icontains"],
            "created_at": ["gte", "lte"],
        }

    def filter_phone_pattern(self, queryset, name, value):
        """Match phone numbers starting with given value (e.g., '+1')."""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    price__gte = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    stock__gte = django_filters.NumberFilter(field_name="stock", lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name="stock", lookup_expr='lte')
    stock_less_than_10 = django_filters.BooleanFilter(method='filter_stock_less_than_10')

    class Meta:
        model = Product
        fields = {
            "name": ["icontains"],
            "price": ["gte", "lte"],
            "stock": ["gte", "lte"],
        }

    def filter_stock_less_than_10(self, queryset, name, value):
        """Return products with stock < 10 if True."""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    # Total amount range
    total_amount__gte = django_filters.NumberFilter(method='filter_total_gte')
    total_amount__lte = django_filters.NumberFilter(method='filter_total_lte')

    # Order date range
    order_date__gte = django_filters.DateFilter(field_name="order_date", lookup_expr='gte')
    order_date__lte = django_filters.DateFilter(field_name="order_date", lookup_expr='lte')

    # Related lookups
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name="products__name", lookup_expr='icontains')
    product_id = django_filters.NumberFilter(field_name="products__id", lookup_expr='exact')

    class Meta:
        model = Order
        fields = {
            "customer": ["exact"],
            "products": ["exact"],
            "order_date": ["gte", "lte"],
        }

    def filter_total_gte(self, queryset, name, value):
        return queryset.annotate(total_price_sum=Sum('products__price')).filter(total_price_sum__gte=value)

    def filter_total_lte(self, queryset, name, value):
        return queryset.annotate(total_price_sum=Sum('products__price')).filter(total_price_sum__lte=value)
