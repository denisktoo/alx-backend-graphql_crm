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
        fields = ("id", "name", "price", "stock")
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter

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

    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter

    def resolve_total_amount(self, info):
        # Sum the price of all products in this order
        return sum(product.price for product in self.products.all())
    
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

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    # def resolve_allCustomers(self, info, filter=None, order_by=None, **kwargs):
    #     qs = Customer.objects.all()
    #     if filter:
    #         if filter.get('nameIcontains'):
    #             qs = qs.filter(name__icontains=filter['nameIcontains'])
    #         if filter.get('emailIcontains'):
    #             qs = qs.filter(email__icontains=filter['emailIcontains'])
    #         if filter.get('createdAtGte'):
    #             qs = qs.filter(created_at__gte=filter['createdAtGte'])
    #         if filter.get('createdAtLte'):
    #             qs = qs.filter(created_at__lte=filter['createdAtLte'])
    #         if filter.get('phonePattern'):
    #             qs = qs.filter(phone__startswith=filter['phonePattern'])

    #         if order_by:
    #             qs = qs.order_by(*order_by)
    #     return qs

    # def resolve_all_products(self, info, order_by=None, **kwargs):
    #     qs = Product.objects.all()
    #     if order_by:
    #         qs = qs.order_by(*order_by)
    #     return qs

    # def resolve_all_orders(self, info, total_amount_gte=None, total_amount_lte=None, order_by=None, **kwargs):
    #     qs = Order.objects.all()
    #     # if total_amount_gte is not None:
    #     #     qs = [order for order in qs if sum(p.price for p in order.products.all()) >= total_amount_gte]
    #     # if total_amount_lte is not None:
    #     #     qs = [order for order in qs if sum(p.price for p in order.products.all()) <= total_amount_lte]
    #     if order_by:
    #         qs = qs.order_by(*order_by)
    #     return qs
    
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
