import graphene
from graphene import ObjectType, String, Decimal, Int, DateTime
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'created_at')

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'created_at')

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'product', 'quantity', 'total_price', 'created_at')

class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)

    class Arguments:
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()

    def mutate(self, info, name, email, phone=""):
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer)

class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String()
        price = graphene.Decimal()
        description = graphene.String()

    def mutate(self, info, name, price, description=""):
        product = Product(name=name, price=price, description=description)
        product.save()
        return CreateProduct(product=product)

class Query(ObjectType):
    hello = graphene.String()
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()

class Mutation(ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()

