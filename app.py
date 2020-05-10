from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test123@localhost/lexus'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

db = SQLAlchemy(app)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'), nullable=False)
        
class Dealer(db.Model):
    __tablename__ = 'dealer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    country = db.Column(db.String(200))
    averageRating = db.Column(db.Integer)
    numofRatings = db.Column(db.Integer)
    feedbacks = db.relationship('Feedback', backref = 'dealer', lazy=True)

@app.route('/')
def index():
    dealers = Dealer.query
    return render_template('index.html', dealers = dealers)

Return Json
getALlDealer, more routes
More tables


@app.route('/addDealer', methods=['GET'])
def newDealer():
    return render_template('dealer.html')

@app.route('/addDealer', methods=['POST'])
def addDealer():
    if request.method == 'POST':
        nameofDealer = request.form['dealer']
        country = request.form['country']
        newDealer = Dealer(name = nameofDealer, averageRating = 0, country = country, numofRatings = 0)
        db.session.add(newDealer)
        db.session.commit()
        return render_template('dealer.html', message = 'You have successfuly added the new dealer!')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealerName = request.form['dealer']
        rating = int(request.form['rating'])
        comments = request.form['comments']
        print(customer, dealer, rating, comments)
        if customer == '' or dealer == '':
            return render_template('index.html', message='Please enter required fields', dealers = Dealer.query)
        if db.session.query(Dealer).filter(Dealer.name == dealerName).count() == 0:
            return render_templete('index.html', message='Dealer does not exist', dealers = Dealer.query)
        reviewedDealer = db.session.query(Dealer).filter(Dealer.name == dealerName).first()
        reviewedDealer.averageRating = ((reviewedDealer.averageRating * reviewedDealer.numofRatings) + rating) / (reviewedDealer.averageRating + 1)
        reviewedDealer.numofRatings += 1

        print(reviewedDealer.name)
    
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            data = Feedback(customer=customer, dealer_id = reviewedDealer.id , rating = rating, comments = comments)
            db.session.add(data)
            db.session.commit()
            return render_template('index.html', message='You have successfully submitted feedback', dealers = Dealer.query)
        else:
            return render_template('index.html', message='You have already submitted feedback', dealers = Dealer.query)

@app.route('/dealer', methods=['GET'])
def dealer():
    return 0

if __name__ == '__main__':
    app.run()
