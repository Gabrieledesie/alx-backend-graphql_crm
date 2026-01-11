import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from crm.models import Customer, Product, Order
import re


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date", "created_at")


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        # Validate phone format if provided
        if input.phone:
            phone_pattern = r'^[\+\d\-\s\(\)]+$'
            if not re.match(phone_pattern, input.phone):
                raise Exception("Invalid phone number format")

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone if input.phone else None
        )
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []
        
        for idx, customer_input in enumerate(input):
            try:
                # Validate email uniqueness
                if Customer.objects.filter(email=customer_input.email).exists():
                    errors.append(f"Row {idx + 1}: Email {customer_input.email} already exists")
                    continue

                # Validate phone format if provided
                if customer_input.phone:
                    phone_pattern = r'^[\+\d\-\s\(\)]+$'
                    if not re.match(phone_pattern, customer_input.phone):
                        errors.append(f"Row {idx + 1}: Invalid phone number format")
                        continue

                customer = Customer(
                    name=customer_input.name,
                    email=customer_input.email,
                    phone=customer_input.phone if customer_input.phone else None
                )
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        # Validate price is positive
        if input.price <= 0:
            raise Exception("Price must be positive")

        # Validate stock is non-negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(
            name=input.name,
            price=input.price,
            stock=stock
        )
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        # Validate at least one product
        if not input.product_ids:
            raise Exception("At least one product must be provided")

        # Validate products exist and calculate total
        products = []
        total_amount = 0
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
                total_amount += product.price
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {product_id}")

        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount
            )
            order.products.set(products)

        return CreateOrder(order=order)


# Query
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()


# Mutation


class UpdateLowStockProducts(graphene.Mutation):
    """Mutation to update low stock products (stock < 10)"""
    
    class Arguments:
        pass
    
    products = graphene.List(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info):
        # Find products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        
        updated_products = []
        for product in low_stock_products:
            # Increment stock by 10
            product.stock += 10
            product.save()
            updated_products.append(product)
        
        return UpdateLowStockProducts(
            products=updated_products,
            success=True,
            message=f"Updated {len(updated_products)} low-stock products"
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
