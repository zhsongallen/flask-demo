import graphene
from flask import json, jsonify, request
import sqlalchemy
from sqlalchemy.sql import select
from collections import namedtuple
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Order as OrderModel, Feedback as FeedbackModel, Customer as CustomerModel, Dealer as DealerModel

def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

class Feedback(SQLAlchemyObjectType):
    class Meta:
        model = FeedbackModel


class Order(SQLAlchemyObjectType):
    class Meta:
        model = OrderModel


class Customer(SQLAlchemyObjectType):
    class Meta:
        model = CustomerModel

class Dealer(SQLAlchemyObjectType):
    class Meta:
        model = DealerModel

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    
    #/getAllCustomers
    all_customers = graphene.List(Customer)
    def resolve_all_customers(self, info):
        query = Customer.get_query(info)
        return query
    
    #/getAllDealers
    all_dealers = graphene.List(Dealer)
    def resolve_all_dealers(self, info):
        query = Dealer.get_query(info)
        return query
    
    #/getAllOrders
    all_orders = graphene.List(Order)
    def resolve_all_orders(self, info):
        query = Order.get_query(info)
        return query

    #/getAllFeedbacks
    all_feedbacks = graphene.List(Feedback)
    def resolve_all_feedbacks(self, info):
        query = Feedback.get_query(info)
        return query

    #/getDealerByID
    get_dealer = graphene.List(Dealer, id=graphene.Int())
    def resolve_dealer(self, info, **args):
        query = Dealer.get_query(info)
        return query.filter(DealerModel.id == args.get('id'))
    
    #/getOrders, get orders for a particular customer and dealer
    get_orders = graphene.List(Order, customer_id=graphene.Int(), dealer_id=graphene.Int())
    def resolve_get_orders(self, info, **args):
        query = Order.get_query(info)
        query = query.join(CustomerModel)
        query = query.join(DealerModel)
        query = query.filter(CustomerModel.id == args.get('customer_id'))
        query = query.filter(DealerModel.id == args.get('dealer_id'))

        return query

    #/getCustomers, get all customers for a particular dealer
    get_customers = graphene.List(Customer, dealer_id=graphene.Int())
    def resolve_get_customers(self, info, **args):
        customersFound = db_session.query(OrderModel.customer_id).filter(DealerModel.id == args.get('dealer_id'))
        customerList = customersFound.all()
        return Customer.get_query(info).filter(CustomerModel.id.in_(customerList))

    
    #/getFeedback, get feedbacks for a customer and dealer
    get_feedbacks = graphene.List(Feedback, customer_id=graphene.Int(), dealer_id=graphene.Int())
    def resolve_get_feedbacks(self, info, **args):
        query = Feedback.get_query(info)
        query = query.join(CustomerModel)
        query = query.join(DealerModel)
        query = query.filter(CustomerModel.id == args.get('customer_id'))
        query = query.filter(DealerModel.id == args.get('dealer_id'))
        return query

class addDealer(graphene.Mutation):
    name = graphene.String()
    country = graphene.String()
    class Arguments:
        name = graphene.String()
        country = graphene.String()

    def mutate(self, info, name, country):
        dealer = DealerModel(name=name, country=country)
        db_session.add(dealer)
        db_session.commit()
        return addDealer(name=dealer.name, country=dealer.country)

class addCustomer(graphene.Mutation):
    name = graphene.String()
    class Arguments:
        name = graphene.String()

    def mutate(self, info, name):
        customer = CustomerModel(name=name)
        db_session.add(customer)
        db_session.commit()
        return addCustomer(name=customer.name, country=customer.country)

class makeOrder(graphene.Mutation):
    dealer_id = graphene.Int()
    customer_id = graphene.Int()
    price = graphene.Int()

    class Arguments:
        dealer_id = graphene.Int()
        customer_id = graphene.Int()
        price = graphene.Int()

    def mutate(self, info, dealer_id, customer_id, price):
        order = OrderModel(dealer_id=dealer_id, customer_id=customer_id, price=price)
        db_session.add(order)
        db_session.commit()
        return makeOrder(dealer_id=order.dealer_id, customer_id=order.customer_id, price=order.price)

class addFeedback(graphene.Mutation):
    dealer_id = graphene.Int()
    customer_id = graphene.Int()
    comments = graphene.String()
    rating = graphene.Int()

    class Arguments:
        dealer_id = graphene.Int()
        customer_id = graphene.Int()
        comments = graphene.String()
        rating = graphene.Int()

    def mutate(self, info, dealer_id, customer_id, comments, rating):
        feedback = FeedbackModel(dealer_id=dealer_id, customer_id=customer_id, comments=comments, rating=rating)
        db_session.add(feedback)
        db_session.commit()
        return addFeedback(dealer_id=feedback.dealer_id, customer_id=feedback.customer_id, comments=feedback.comments, rating=feedback.rating)

class Mutation(graphene.ObjectType):
    #/addDealer
    add_dealer = addDealer.Field()
    #/addCustomer
    add_customer = addCustomer.Field()
    #/makeOrder, make a new order
    make_order =makeOrder.Field()

    #/deleteDealerByID

    #/submitFeedback
    add_feedback = addFeedback.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)