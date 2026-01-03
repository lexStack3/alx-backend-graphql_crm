import re
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from graphql import GraphQLError
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "products",
            "total_amount",
            "order_date"
        )

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


class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    class Arguments:
        input = CustomerInput(required=True)

    def mutate(self, info, input):
        name = input.name
        email = input.email
        phone = input.phone

        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(
                customer=None,
                message="Email already exists"
            )

        if phone:
            pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
            if not re.match(pattern, phone):
                return CreateCustomer(
                    customer=None,
                    message="Invalid phone number format"
                )

        customer = Customer.objects.create(
            name=name,
            email=email,
            phone=phone
        )

        return CreateCustomer(
            customer=customer,
            message="Customer created successfully"
        )


class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)


    class Arguments:
        input = graphene.List(
            graphene.NonNull(CustomerInput),
            required=True
        )


    def mutate(self, info, input):
        created = []
        errors = []

        with transaction.atomic():
            for data in input:
                email = data.email

                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Email already exists: {email}")
                    continue

                if data.phone:
                    pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
                    if not re.match(pattern, data.phone):
                        errors.append(f"Invalid phone format for email: {email}")
                        continue

                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone
                )
                created.append(customer)
        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        input = ProductInput(required=True)

    def mutate(self, info, input):
        name = input.get('name')
        price = input.get('price')
        stock = input.get('stock', 0)

        if price <= 0.00:
            raise GraphQLError("Price must be greater than zero")

        if stock < 0:
            raise GraphQLError("Stock cannot be negative")

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock
        )

        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)


    class Arguments:
        input = OrderInput(required=True)

    def mutate(self, info, input):
        customer_id = input.customer_id
        product_ids = input.product_ids
        order_date = input.order_date

        if not product_ids:
            raise GraphQLError("At least one product must be selected")

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")
        
        products = Product.objects.filter(id__in=product_ids)

        if products.count() != len(product_ids):
            raise GraphQLError("Invalid product ID")

        total_amount = sum(product.price for product in products)

        order = Order(
            customer=customer,
            total_amount=total_amount
        )
        order.save()

        order.products.set(products)

        return CreateOrder(order=order)


class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter


class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter


class Query(graphene.ObjectType):
    hello = graphene.String()
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    # Filter endpoints
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter
    )

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.select_related('customer').prefetch_related('products')


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
