import graphene
from graphene import ObjectType
from graphene_django import DjangoObjectType
import graphene.relay as relay
from .filters import CustomerFilter
from graphene_django.filter import DjangoFilterConnectionField

from .models import Customer, Product, Order


class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)
        filterset_class = CustomerFilter

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "description", "created_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "product", "quantity", "total_price", "created_at")


class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    def mutate(self, info, name, email, phone=""):
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer)


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        description = graphene.String(required=False)

    def mutate(self, info, name, price, description=""):
        product = Product(name=name, price=price, description=description)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    def mutate(self, info, customer_id, product_id, quantity):
        customer = Customer.objects.get(id=customer_id)
        product = Product.objects.get(id=product_id)

        total_price = product.price * quantity

        order = Order(
            customer=customer,
            product=product,
            quantity=quantity,
            total_price=total_price,
        )
        order.save()
        return CreateOrder(order=order)


class Query(ObjectType):
    hello = graphene.String()

    # existing simple lists
    all_customers = DjangoFilterConnectionField(CustomerNode)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    # NEW: filtered lists (arguments added directly on the fields)
    filtered_customers = graphene.List(
        CustomerType,
        name_icontains=graphene.String(),
        email_icontains=graphene.String(),
        created_at_gte=graphene.types.datetime.Date(),
        created_at_lte=graphene.types.datetime.Date(),
        phone_pattern=graphene.String(),
    )

    filtered_products = graphene.List(
        ProductType,
        name_icontains=graphene.String(),
        price_gte=graphene.Decimal(),
        price_lte=graphene.Decimal(),
        stock_gte=graphene.Int(),
        stock_lte=graphene.Int(),
        order_by=graphene.String(),  # e.g. "-stock" or "price"
    )

    filtered_orders = graphene.List(
        OrderType,
        total_amount_gte=graphene.Decimal(),
        total_amount_lte=graphene.Decimal(),
        order_date_gte=graphene.types.datetime.Date(),
        order_date_lte=graphene.types.datetime.Date(),
        customer_name=graphene.String(),
        product_name=graphene.String(),
        product_id=graphene.ID(),
        order_by=graphene.String(),  # e.g. "-created_at"
    )

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()

    # === resolvers for filtered queries ===

    def resolve_filtered_customers(
        root,
        info,
        name_icontains=None,
        email_icontains=None,
        created_at_gte=None,
        created_at_lte=None,
        phone_pattern=None,
    ):
        qs = Customer.objects.all()

        if name_icontains:
            qs = qs.filter(name__icontains=name_icontains)
        if email_icontains:
            qs = qs.filter(email__icontains=email_icontains)
        if created_at_gte:
            qs = qs.filter(created_at__gte=created_at_gte)
        if created_at_lte:
            qs = qs.filter(created_at__lte=created_at_lte)
        if phone_pattern:
            qs = qs.filter(phone__startswith=phone_pattern)

        return qs

    def resolve_filtered_products(
        root,
        info,
        name_icontains=None,
        price_gte=None,
        price_lte=None,
        stock_gte=None,
        stock_lte=None,
        order_by=None,
    ):
        qs = Product.objects.all()

        if name_icontains:
            qs = qs.filter(name__icontains=name_icontains)
        if price_gte is not None:
            qs = qs.filter(price__gte=price_gte)
        if price_lte is not None:
            qs = qs.filter(price__lte=price_lte)
        if stock_gte is not None:
            qs = qs.filter(stock__gte=stock_gte)
        if stock_lte is not None:
            qs = qs.filter(stock__lte=stock_lte)

        if order_by:
            qs = qs.order_by(order_by)

        return qs

    def resolve_filtered_orders(
        root,
        info,
        total_amount_gte=None,
        total_amount_lte=None,
        order_date_gte=None,
        order_date_lte=None,
        customer_name=None,
        product_name=None,
        product_id=None,
        order_by=None,
    ):
        qs = Order.objects.all()

        if total_amount_gte is not None:
            qs = qs.filter(total_price__gte=total_amount_gte)
        if total_amount_lte is not None:
            qs = qs.filter(total_price__lte=total_amount_lte)
        if order_date_gte:
            qs = qs.filter(created_at__date__gte=order_date_gte)
        if order_date_lte:
            qs = qs.filter(created_at__date__lte=order_date_lte)
        if customer_name:
            qs = qs.filter(customer__name__icontains=customer_name)
        if product_name:
            qs = qs.filter(product__name__icontains=product_name)
        if product_id:
            qs = qs.filter(product__id=product_id)

        if order_by:
            qs = qs.order_by(order_by)

        return qs


class Mutation(ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()



