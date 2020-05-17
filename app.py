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
    if (result == None):
        abort(404)
    return jsonify({
            'id': result.id,
            'name': result.name,
            'country': result.country,
            'avergeRating': result.averageRating
    })



if __name__ == '__main__':
    app.run()