from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, jsonify, abort

app = Flask(__name__)

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test123@db:5432/lexus'

db = SQLAlchemy(app)

# A customer can submit multiple feedbacks to many dealers

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), unique=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

class Dealer(db.Model):
    __tablename__ = 'dealer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    country = db.Column(db.String(200))
    averageRating = db.Column(db.Integer)
    numofRatings = db.Column(db.Integer)
    feedbacks = db.relationship('Feedback', backref = 'dealer', cascade='all, delete-orphan', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique = True)
    feedbacks = db.relationship('Feedback', backref = 'customer', lazy = True)

def create_db():
    db.create_all()
    db.session.commit()

# Get feedback for a particular dealer and customer
@app.route('/getFeedback', methods=['GET'])
def getFeedback():
    if not request.json:
        abort(404)
    dealer = request.json['dealer']
    customer_name = request.json['customer'] 
    feedbackList = Customer.query.filter(Customer.name == customer_name).first().feedbacks
    DealerID = Dealer.query.filter(Dealer.name == dealer).first().id
    if (DealerID == None or feedbackList == None):
        abort(404)
    for feedback in feedbackList:
        if (feedback.dealer_id == DealerID):
            return jsonify({
                "customer": customer_name,
                "dealer": dealer,
                "comments": feedback.comments
            })
    

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
        rating = request.json['rating']
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
        data = Feedback(customer_name=customerFound.name, dealer_id = reviewedDealer.id , rating = rating, comments = comments, customer_id = customerFound.id)
        db.session.add(data)
        db.session.commit()
        return jsonify({
            "customer":customerFound.name,
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
        "name":nameofCustomer
    })

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
        "customer": "Customer1",
        "dealer": "Dealer1",
        "rating": 10,
        "comments": "Great dealer!"
    }

    /getFeedback: [GET]
    {
        "customer": "Customer1",
        "dealer": "Dealer1"
    }
'''