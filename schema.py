import graphene
from flask import json, jsonify, request
import requests
from collections import namedtuple
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

def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    
    #/getAllCustomers
    all_Customers = graphene.List(Customer)
    def resolve_all_Customers(self, info):
        query = Customer.get_query(info)
        return query
    
    #/getAllDealers
    all_Dealers = graphene.List(Dealer)
    def resolve_all_Dealers(self, info):
        query = Dealer.get_query(info)
        return query
    
    #Similar to previous routes
    all_orders = SQLAlchemyConnectionField(Order.connection)
    all_feedbacks = SQLAlchemyConnectionField(Feedback.connection)

    #/getDealerByName
    dealer = graphene.List(Dealer, name=graphene.String())
    def resolve_dealer(self, info, **args):
        result = requests.get("http://127.0.0.1:5000/getDealerByName/" + args.get('name')).json()
        return result
        
schema = graphene.Schema(query=Query)