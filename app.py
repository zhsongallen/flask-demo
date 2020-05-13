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

# A customer can submit multiple feedbacks to many dealers

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

class Dealer(db.Model):
    __tablename__ = 'dealer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    country = db.Column(db.String(200))
    averageRating = db.Column(db.Integer)
    numofRatings = db.Column(db.Integer)
    feedbacks = db.relationship('Feedback', backref = 'dealer', cascade='all, delete-orphan', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    feedbacks = db.relationship('Feedback', backref = 'customer', lazy = True)

# Get feedback for a particular dealer and customer
@app.route('/getFeedback', methods=['GET'])
def getFeedback():
    if not request.json:
        abort(404)
    dealer_id = request.json['dealer_id']
    customer_id = request.json['customer_id'] 
    customerFound = Customer.query.filter(Customer.id == customer_id).first()
    if (customerFound == None):
        abort(404)
    feedbacksFound = customerFound.feedbacks
    if (feedbacksFound == None):
        abort(404)
    dealerFound = Dealer.query.filter(Dealer.id == dealer_id).first()
    if (dealerFound == None):
        abort(404)
    for feedback in feedbacksFound:
        if (feedback.dealer_id == dealerFound.id):
            return jsonify({
                "customer_id": customerFound.id,
                "customer_name":customerFound.name,
                "dealer_id": dealerFound.id,
                "dealer_name":dealerFound.name,
                "comments": feedback.comments
            })
    abort(404) 

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
        rating = request.json['rating']
        comments = request.json['comments']
        if db.session.query(Dealer).filter(Dealer.id == dealer_id).count() == 0:
            abort(404)
        if db.session.query(Customer).filter(Customer.id == customer_id).count() == 0:
            abort(404)
        customerFound = db.session.query(Customer).filter(Customer.id == customer_id).first()
        reviewedDealer = db.session.query(Dealer).filter(Dealer.id == dealer_id).first()
        reviewedDealer.averageRating = ((reviewedDealer.averageRating * reviewedDealer.numofRatings) + rating) / (reviewedDealer.averageRating + 1)
        reviewedDealer.numofRatings += 1
        data = Feedback(customer_name=customerFound.name, dealer_id = reviewedDealer.id , rating = rating, comments = comments, customer_id = customerFound.id)
        db.session.add(data)
        db.session.commit()
        return jsonify({
            "customer_name":customerFound.name,
            "customer_id":customerFound.id,
            "dealer_name": reviewedDealer.name,
            "dealer_id": reviewedDealer.id,
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
        "customer_id": 1,
        "dealer_id": 1,
        "rating": 10,
        "comments": "Great dealer!"
    }
    /getFeedback: [GET]
    {
        "customer_id":1,
        "dealer_id":1
    }
'''