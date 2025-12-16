import graphene
from graphene import ObjectType, String

class Query(ObjectType):
    hello = graphene.String()

    def resolve_hello(root, info):
        return "Hello, GraphQL!"
