import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re
from django.core.exceptions import ValidationError
from datetime import datetime
from decimal import Decimal
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter
        fields = ['id', 'name', 'email', 'phone', 'created_at']

# Define an InputObjectType for single customer creation
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

# Mutation class
class CreateCustomer(graphene.Mutation):
    # Fields that will be returned
    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = CustomerInput(required=True)

    def mutate(self, info, input):
        name = input.name
        email = input.email
        phone = input.phone

        # Check for duplicate email
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(success=False, message="User with this email already exists!")
        
        # Validates Phone Number
        phone_pattern = r"^(?:\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
        if phone and not re.match(phone_pattern, phone):
            return CreateCustomer(
                success = False,
                message = "Invalid phone number format, Examples: +1234567890 or 123-456-7890"
            )
        
        # Create a new Customer
        customer = Customer(name=name, email=email, phone=phone)
        try:
            customer.full_clean()
            customer.save()
        except ValidationError as e:
            return CreateCustomer(
                success = False,
                message = f"Validation Error: {e}"
            )
        
        return CreateCustomer(
            customer = customer,
            success = True,
            message = "Customer created successfully!"
        )

class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(graphene.NonNull(CustomerInput), required=True)

    def mutate(root, info, input):
        created_customers = []
        errors = []

        for i, customer_data in enumerate(input):
            mutation_result = CreateCustomer.mutate(
                root, info, input=customer_data
            )

            if getattr(mutation_result, "success", False):
                created_customers.append(mutation_result.customer)
            else:
                errors.append(f"Row {i + 1}: {getattr(mutation_result, 'message', 'Unknown error')}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)
    
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter
        fields = ['id', 'name', 'price', 'stock']

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False)

class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = ProductInput(required=True)

    def mutate(self, info, input):
        name = input.name
        price = Decimal(str(input.price))
        stock = input.stock if input.stock is not None else 0

        #validate price to be positive
        if price <= 0:
            return CreateProduct(
                success = False,
                message = "Price should be greater than 0."
            )
        
        # validate stock to be non-negative
        if stock < 0:
            return CreateProduct(
                success = False,
                message = "Stock should be 0 or more."
            )

        # Create a new Product
        product = Product(name=name, price=price, stock=stock)
        try:
            product.full_clean()
            product.save()
            return CreateProduct(product=product, success=True, message="Product created successfully.")
        except ValidationError as e:
            return CreateProduct(product=None, success=False, message=f"Validation error: {e}")

class OrderType(DjangoObjectType):
    total_amount = graphene.Float()
    products = graphene.List(lambda: ProductType)  # override connection field

    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter
        fields = ['id', 'customer', 'order_date', 'total_amount']  # remove 'products' from Meta

    def resolve_total_amount(self, info):
        return sum(product.price for product in self.products.all())

    def resolve_products(self, info):
        return self.products.all()
    
class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)  # GraphQL will expose this as customerId
    product_ids = graphene.List(graphene.ID, required=True)  # GraphQL will expose as productIds
    order_date = graphene.DateTime()


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = OrderInput(required=True)

    def mutate(self, info, input):
        try:
            customer_id = int(input.customer_id)
            product_ids = [int(pid) for pid in input.product_ids]
        except ValueError:
            return CreateOrder(success=False, message="IDs must be valid integers.")

        order_date = input.order_date

        # Validate customer
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(success=False, message="Customer not found.")

        # Validate products
        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            return CreateOrder(success=False, message="No valid products found.")

        if len(product_ids) != products.count():
            return CreateOrder(success=False, message="Some product IDs are invalid.")

        if not product_ids:
            return CreateOrder(success=False, message="At least one product must be selected.")

        # Create order
        order = Order.objects.create(
            customer=customer,
            order_date=order_date or datetime.now()
        )
        order.products.set(products)

        return CreateOrder(order=order, success=True, message="Order created successfully.")

class CustomerFilterInput(graphene.InputObjectType):
    nameIcontains = graphene.String()
    emailIcontains = graphene.String()
    createdAtGte = graphene.DateTime()
    createdAtLte = graphene.DateTime()
    phonePattern = graphene.String()

class ProductFilterInput(graphene.InputObjectType):
    nameIcontains = graphene.String()
    priceGte = graphene.Float()
    priceLte = graphene.Float()
    stockGte = graphene.Int()
    stockLte = graphene.Int()

class OrderFilterInput(graphene.InputObjectType):
    totalAmountGte = graphene.Float()
    totalAmountLte = graphene.Float()
    orderDateGte = graphene.DateTime()
    orderDateLte = graphene.DateTime()
    customerName = graphene.String()
    productName = graphene.String()
    productId = graphene.ID()

class Query(graphene.ObjectType):
    # Add custom `filter` and `orderBy` args; return queryset -> Relay edges
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filter=graphene.Argument(CustomerFilterInput),
        order_by=graphene.List(graphene.String)  # e.g., ["-created_at", "name"]
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filter=graphene.Argument(ProductFilterInput),
        order_by=graphene.List(graphene.String)
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filter=graphene.Argument(OrderFilterInput),
        order_by=graphene.List(graphene.String)
    )

    def resolve_all_customers(self, info, filter=None, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if filter:
            if filter.get("nameIcontains"):
                qs = qs.filter(name__icontains=filter["nameIcontains"])
            if filter.get("emailIcontains"):
                qs = qs.filter(email__icontains=filter["emailIcontains"])
            if filter.get("createdAtGte"):
                qs = qs.filter(created_at__gte=filter["createdAtGte"])
            if filter.get("createdAtLte"):
                qs = qs.filter(created_at__lte=filter["createdAtLte"])
            if filter.get("phonePattern"):
                qs = qs.filter(phone__startswith=filter["phonePattern"])
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, filter=None, order_by=None, **kwargs):
        qs = Product.objects.all()
        if filter:
            if filter.get("nameIcontains"):
                qs = qs.filter(name__icontains=filter["nameIcontains"])
            if filter.get("priceGte") is not None:
                qs = qs.filter(price__gte=filter["priceGte"])
            if filter.get("priceLte") is not None:
                qs = qs.filter(price__lte=filter["priceLte"])
            if filter.get("stockGte") is not None:
                qs = qs.filter(stock__gte=filter["stockGte"])
            if filter.get("stockLte") is not None:
                qs = qs.filter(stock__lte=filter["stockLte"])
        if order_by:
            if isinstance(order_by, str):
                qs = qs.order_by(order_by)  # no unpacking
            else:
                qs = qs.order_by(*order_by)

        return qs

    def resolve_all_orders(self, info, filter=None, order_by=None, **kwargs):
        # annotate total_amount for DB-level filtering
        qs = Order.objects.all().annotate(total_amount_db=Sum("products__price"))
        if filter:
            if filter.get("orderDateGte"):
                qs = qs.filter(order_date__gte=filter["orderDateGte"])
            if filter.get("orderDateLte"):
                qs = qs.filter(order_date__lte=filter["orderDateLte"])
            if filter.get("customerName"):
                qs = qs.filter(customer__name__icontains=filter["customerName"])
            if filter.get("productName"):
                qs = qs.filter(products__name__icontains=filter["productName"])
            if filter.get("productId"):
                try:
                    qs = qs.filter(products__id=int(filter["productId"]))
                except (TypeError, ValueError):
                    qs = qs.none()
            if filter.get("totalAmountGte") is not None:
                qs = qs.filter(total_amount_db__gte=filter["totalAmountGte"])
            if filter.get("totalAmountLte") is not None:
                qs = qs.filter(total_amount_db__lte=filter["totalAmountLte"])
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
    
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
