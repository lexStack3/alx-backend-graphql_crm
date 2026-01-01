import graphene


class CRMQuery(graphene.ObjectType):
    hello = graphene.Strng()

    def resove_hello(root, info):
        return "Hello, GraphQL!"
