<<<<<<< HEAD
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, jsonify, abort, json

app = Flask(__name__)

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test123@db:5432/lexus'

db = SQLAlchemy(app)

# A customer can make multiple orders with many dealers, and submit multiple feedbacks to many dealers, but only one for each order made
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'))

class Dealer(db.Model):
    __tablename__ = 'dealer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    country = db.Column(db.String(200))
    averageRating = db.Column(db.Integer)
    numofRatings = db.Column(db.Integer)
    feedbacks = db.relationship('Feedback', backref = 'dealer', cascade='all, delete-orphan', lazy=True)
    orders = db.relationship('Order', backref = 'dealer', cascade='all, delete-orphan', lazy=True)


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    feedbacks = db.relationship('Feedback', backref = 'customer', lazy = True)
    orders = db.relationship('Order', backref = 'customer', lazy = True)

#Get orders for a particular customer and dealer
@app.route('/getOrders', methods = ['GET'])
def getOrders():
    if not request.json:
        abort(404)
    dealer_id = request.json['dealer_id']
    customer_id = request.json['customer_id']
    dealerFound = Dealer.query.filter(Dealer.id == dealer_id).first()
    if (dealerFound == None):
        abort(404)
    ordersMade = []
    ordersFoundByDealer = dealerFound.orders
    if ordersFoundByDealer != None:
        for order in ordersFoundByDealer:
            if (order.customer_id == customer_id):
                ordersMade.append({
                    "id": order.id,
                    "price": order.price
                })
    json_arr = []
    for order in ordersMade:
        orderInJson = json.loads(str(order).replace("\'", "\""))
        json_arr.append(orderInJson)
    return jsonify(json_arr)

#Get all customers for a particular dealer
@app.route('/getCustomers', methods = ['GET'])
def getCustomers():
    if not request.json:
        abort(404)
    dealer_id = request.json['dealer_id']
    dealerFound = Dealer.query.filter(Dealer.id == dealer_id).first()
    if (dealerFound == None):
        abort(404)
    customersSet = []
    customersString = []
    ordersFoundByDealer = dealerFound.orders
    if ordersFoundByDealer != None:
        for order in ordersFoundByDealer:
            if not order.customer_id in customersSet:
                customersString.append({
                    "customer_id": order.customer_id,
                    "customer_name": Customer.query(Customer.id == order.customer_id).first().id,
                })
                customersSet.append(order.customer_id)
    json_arr = []
    for customer in customersString:
        customerInJson = json.loads(str(customer).replace("\'", "\""))
        json_arr.append(customerInJson)
    return jsonify(json_arr)

#Add a new order
@app.route('/makeOrder', methods = ['POST'])
def makeOrder():
    if not request.json:
        abort(404)
    dealer_id = request.json['dealer_id']
    customer_id = request.json['customer_id']
    price = request.json['price']
    customerFound = Customer.query.filter(Customer.id == customer_id)
    if customerFound == None:
        abort(404)
    dealerFound = Dealer.query.filter(Dealer.id == dealer_id)
    if dealerFound == None:
        abort(404)
    newOrder = Order(customer_id = customer_id, dealer_id = dealer_id, price = price)
    db.session.add(newOrder)
    db.session.commit()
    return jsonify({
        "customer": customerFound.first().name,
        "Dealer": dealerFound.first().name,
        "Price": price
    })

# Get feedback for a particular dealer and customer
@app.route('/getFeedback', methods=['GET'])
def getFeedback():
    if not request.json:
        abort(404)
    dealer_id = request.json['dealer_id']
    customer_id = request.json['customer_id'] 
    customerFound = Customer.query.filter(Customer.id == customer_id)
    if (customerFound == None):
        abort(404)
    customerFound = customerFound.first()
    dealerFound = Dealer.query.filter(Dealer.id == dealer_id)
    if (dealerFound == None):
        abort(404)
    dealerFound = dealerFound.first()
    feedbacksFound = customerFound.feedbacks
    if (feedbacksFound == None):
        abort(404)
    if (dealerFound == None):
        abort(404)
    feedbacksMade = []
    json_arr = []
    for feedback in feedbacksFound:
        if (feedback.dealer_id == dealerFound.id):
            feedbacksMade.append({
                "order": feedback.order_id, 
                "comments": feedback.comments 
                })
    for feedback in feedbacksMade:
        feedbackInJson = json.loads(str(feedback).replace("\'", "\""))
        json_arr.append(feedbackInJson)
    return jsonify(json_arr)
    abort(404) 

@app.route('/getDealerByID', methods=['GET'])
def getDealerbyID():
    if not request.json:
        abort(404)
    result = db.session.query(Dealer).filter(Dealer.id == request.json['id']).first()
=======
from flask import Flask, abort, request, jsonify
from flask_graphql import GraphQLView
from models import Order as OrderModel, Feedback as FeedbackModel, Customer as CustomerModel, Dealer as DealerModel

from models import db_session
from schema import schema, Feedback, Customer, Order, Dealer

app = Flask(__name__)
app.debug = True

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/getDealerByName/<name>', methods=['GET'])
def getDealerbyName(name):
    result = db_session.query(DealerModel).filter(DealerModel.name == name).first()
>>>>>>> graphQLVersion
    if (result == None):
        abort(404)
    return jsonify({
            'id': result.id,
            'name': result.name,
            'country': result.country,
            'avergeRating': result.averageRating
    })

<<<<<<< HEAD
@app.route('/addDealer', methods=['POST'])
def addDealer():
    if not request.json or (not "name" in request.json) or (not "country" in request.json):
        abort(400)
    nameofDealer = request.json['name']
    country = request.json['country']
    newDealer = Dealer(name = nameofDealer, averageRating = 0, country = country, numofRatings = 0)
    db.session.add(newDealer)
    db.session.commit()
    return jsonify({
        "id": newDealer.id,
        "name":nameofDealer,
        "country":country
    })

@app.route('/deleteDealerByID', methods=['DELETE'])
def deleteDealer():
    if not request.json or (not "id" in request.json):
        abort(400)
    result = db.session.query(Dealer).filter(Dealer.id == request.json['id']).first()
    if (result == None):
        abort(404)
    id = result.id
    name = result.name
    country = result.country
    db.session.delete(result)
    db.session.commit()
    return jsonify({
        'id': id,
        'name':name,
        'country':country
    })

@app.route('/submitFeedback', methods=['POST'])
def submitFeedback():
    if not request.json:
        abort(404)
    if request.method == 'POST':
        customer_id = request.json['customer_id']
        dealer_id = request.json['dealer_id']
        order_id = request.json['order_id']
        rating = request.json['rating']
        comments = request.json['comments']
        if db.session.query(Dealer).filter(Dealer.id == dealer_id).count() == 0:
            abort(404)
        if db.session.query(Customer).filter(Customer.id == customer_id).count() == 0:
            abort(404)
        if db.session.query(Order).filter(Order.id == order_id).count() == 0:
            abort(404)
        orderFound = db.session.query(Order).filter(Order.id == order_id).first()
        customerFound = db.session.query(Customer).filter(Customer.id == customer_id).first()
        reviewedDealer = db.session.query(Dealer).filter(Dealer.id == dealer_id).first()
        reviewedDealer.averageRating = ((reviewedDealer.averageRating * reviewedDealer.numofRatings) + rating) / (reviewedDealer.averageRating + 1)
        reviewedDealer.numofRatings += 1
        data = Feedback(customer_name=customerFound.name, dealer_id = reviewedDealer.id , rating = rating, comments = comments, customer_id = customerFound.id, order_id = orderFound.id)
        db.session.add(data)
        db.session.commit()
        return jsonify({
            "customer_name":customerFound.name,
            "customer_id":customerFound.id,
            "dealer_name": reviewedDealer.name,
            "dealer_id": reviewedDealer.id,
            "order_id": orderFound.id,
            "comments":comments
        })

@app.route('/addCustomer', methods=['POST'])
def addCustomer():
    if not request.json or (not "name" in request.json):
        abort(400)
    nameofCustomer = request.json['name']
    newCustomer = Customer(name = nameofCustomer)
    db.session.add(newCustomer)
    db.session.commit()
    return jsonify({
        "id": newCustomer.id,
        "name": newCustomer.name
    })

def create_db():
    db.create_all()
    db.session.commit()

create_db()
app.run(
host='0.0.0.0',
port=5000)

'''
    /addDealer: [POST]
    {
        "name": "Dealer1",
        "country": "China"
    }
    /addCustomer: [POST]
    {
        "name": "Customer1"
    }
    /getDealerByID: [GET]
    {
        "id":1
    }
    /deleteDealerByID: [DELETE]
    {
        "id":2
    }
    /submitFeedback: [POST]
    {
        "customer_id": 1,
        "dealer_id": 1,
        "rating": 10,
        "order_id": 1,
        "comments": "Great dealer!"
    }
    /getFeedback: [GET]
    {
        "customer_id":1,
        "dealer_id":1
    }
    /maekOrder: [POST]
    {
        "customer_id": 1,
        "dealer_id": 1,
        "price": 30
    }
'''
=======


if __name__ == '__main__':
    app.run()
>>>>>>> graphQLVersion
