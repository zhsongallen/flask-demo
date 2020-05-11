from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, jsonify, abort

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test123@localhost/lexus'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

db = SQLAlchemy(app)

# Relationships: Customer <===> Dealers, Many to Many
# Feedback <====> Dealers, One to Many
# Customer <==> Feedback, One to One

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), unique=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'))
    customer_id = db.relationship('Customer', backref = 'feedback', lazy = True)

class Dealer(db.Model):
    __tablename__ = 'dealer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    country = db.Column(db.String(200))
    averageRating = db.Column(db.Integer)
    numofRatings = db.Column(db.Integer)
    feedbacks = db.relationship('Feedback', backref = 'dealer', cascade='all, delete-orphan', lazy=True)
    orders = db.relationship('Order', backref = 'dealers', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique = True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'))
    orders = db.relationship('Order', backref = 'customers', lazy=True)

class Order(db.Model):
    __tablename__ = 'order'
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'), primary_key=True)
    price = db.Column(db.Integer)
    
        
@app.route('/')
def index():
    dealers = Dealer.query
    return render_template('index.html', dealers = dealers)

#========== Not Finished Yet================
@app.route('/getAllDealers', methods=['GET'])
def newDealer():
    dealersList = Dealer.query.all()
    #Query Object cannot be Jsonified!
#========== Not Finished Yet================

@app.route('/getDealerByID', methods=['GET'])
def getDealerbyID():
    if not request.json:
        abort(404)
    result = db.session.query(Dealer).filter(Dealer.id == request.json['id']).first()
    if (result == None):
        abort(404)
    return jsonify({
            'id': result.id,
            'name': result.name,
            'country': result.country,
            'avergeRating': result.averageRating
    })

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
        customer_name = request.json['customer']
        dealerName = request.json['dealer']
        rating = int(request.json['rating'])
        comments = request.json['comments']
        if customer_name == '' or dealerName == '':
            abort(404)
        if db.session.query(Dealer).filter(Dealer.name == dealerName).count() == 0:
            abort(404)
        if db.session.query(Customer).filter(Customer.name == customer_name).count() == 0:
            abort(404)
        customerFound = db.session.query(Customer).filter(Customer.name == customer_name).first()
        reviewedDealer = db.session.query(Dealer).filter(Dealer.name == dealerName).first()
        reviewedDealer.averageRating = ((reviewedDealer.averageRating * reviewedDealer.numofRatings) + rating) / (reviewedDealer.averageRating + 1)
        reviewedDealer.numofRatings += 1
        if db.session.query(Feedback).filter(Feedback.customer == customer_name).count() == 0:
            data = Feedback(customer_name=customerFound.name, dealer_id = reviewedDealer.id , rating = rating, comments = comments, customer_id = customerFound.id)
            db.session.add(data)
            db.session.commit()
            return jsonify({
                "customer":customerFound.name,
                "comments":comments 
            })
        else:
            abort(404)

@app.route('/addCustomer', methods=['POST'])
def addCustomer():
    if not request.json or (not "name" in request.json):
        abort(400)
    nameofCustomer = request.json['name']
    newCustomer = Customer(name = nameofCustomer)
    db.session.add(newCustomer)
    db.session.commit()
    return jsonify({
        "name":nameofCustomer
    })

@app.route('/addOrder', methods=['POST'])
def addOrder():
    if not request.json or (not "customer_name" in request.json) or (not "dealer_name" in request.json):
        abort(400)
    customerFound = db.session.query(Customer).filter(Customer.name == request.json['customer_name']).first()
    dealerFound = db.session.query(Dealer).filter(Dealer.name == request.json['dealer_name']).first()
    price = request.json['price']
    if (customerFound == None or dealerFound == None):
        abort(400)
    newOrder = Order(customer_id = customerFound.id, dealer_id = dealerFound.id, price = price)
    db.session.add(newOrder)
    db.session.commit()
    return jsonify({
        "Customer": customerFound.name,
        "Dealer": dealerFound.name,
        "price": price
    })

if __name__ == '__main__':
    app.run()

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
        "customer": "Allen",
        "dealer": "Allen Song",
        "rating": "10",
        "comments": "Great dealer!"
    }

    /addOrder [POST]
    {
        "customer_name": "Customer1",
        "dealer_name": "Dealer1",
        "price":100
    }

'''