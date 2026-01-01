import graphene
from cmr.schema import CRMQuery


class Query(CRMQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
