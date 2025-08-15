import django_filters
from django.db.models import Sum
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr='icontains')
    created_at_gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at_lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    phone = django_filters.CharFilter(method='filter_phone_pattern')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = Customer
        fields = ["name", "email", "phone", "created_at"]

    def filter_phone_pattern(self, queryset, name, value):
        """
        Custom filter: match phone numbers starting with given value (e.g., '+1')
        """
        return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    price_gte = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    stock_gte = django_filters.NumberFilter(field_name="stock", lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name="stock", lookup_expr='lte')
    stock_less_than_10 = django_filters.BooleanFilter(method='filter_stock_less_than_10')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('stock', 'stock'),
            ('name', 'name'),
        )
    )

    class Meta:
        model = Product
        fields = ["name", "price", "stock"]

    def filter_stock_less_than_10(self, queryset, name, value):
        """
        Custom filter: returns stock < 10
        """
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    # Total amount range
    total_amount_gte = django_filters.NumberFilter(method='filter_total_gte')
    total_amount_lte = django_filters.NumberFilter(method='filter_total_lte')

    # Order date range
    order_date_gte = django_filters.DateFilter(field_name="order_date", lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name="order_date", lookup_expr='lte')

    # Customer name
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr='icontains')

    # Product name
    product_name = django_filters.CharFilter(field_name="products__name", lookup_expr='icontains')

    # Product ID
    product_id = django_filters.NumberFilter(field_name="products__id", lookup_expr='exact')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('order_date', 'order_date'),
            ('customer__name', 'customer_name'),
        )
    )

    class Meta:
        model = Order
        fields = ["customer", "products", "order_date"]

    def filter_total_gte(self, queryset, name, value):
        return queryset.annotate(total_price=Sum('products__price')).filter(total_price__gte=value)

    def filter_total_lte(self, queryset, name, value):
        return queryset.annotate(total_price=Sum('products__price')).filter(total_price__lte=value)
