import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Order as OrderModel, Feedback as FeedbackModel, Customer as CustomerModel, Dealer as DealerModel


class Feedback(SQLAlchemyObjectType):
    class Meta:
        model = FeedbackModel
        interfaces = (relay.Node, )


class Order(SQLAlchemyObjectType):
    class Meta:
        model = OrderModel
        interfaces = (relay.Node, )

class Customer(SQLAlchemyObjectType):
    class Meta:
        model = CustomerModel
        interfaces = (relay.Node, )

class Dealer(SQLAlchemyObjectType):
    class Meta:
        model = DealerModel
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_customers = SQLAlchemyConnectionField(Customer.connection)
    all_dealers = SQLAlchemyConnectionField(Dealer.connection)
    all_orders = SQLAlchemyConnectionField(Order.connection)
    all_feedbacks = SQLAlchemyConnectionField(Feedback.connection)
    customers = graphene.List(Customer, name=graphene.String())
    def resolve_customers(self, info, **args):
        query = Customer.get_query(info)
        print(args.get("name"))
        return query.filter(CustomerModel.name == args.get('name'))

schema = graphene.Schema(query=Query)