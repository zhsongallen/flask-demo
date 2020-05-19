from sqlalchemy import *
from sqlalchemy import select
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://postgres:test123@localhost/lexus', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
# We will need this for querying
Base.query = db_session.query_property()

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(200))
    rating = Column(Integer)
    comments = Column(Text())
    order_id = Column(Integer, ForeignKey('order.id'))
    dealer_id = Column(Integer, ForeignKey('dealer.id'))
    customer_id = Column(Integer, ForeignKey('customer.id'))

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    dealer_id = Column(Integer, ForeignKey('dealer.id'))

class Dealer(Base):
    __tablename__ = 'dealer'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    country = Column(String(200))
    averageRating = Column(Integer)
    numofRatings = Column(Integer)
    feedbacks = relationship('Feedback', backref = 'dealer', cascade='all, delete-orphan', lazy=True)
    orders = relationship('Order', backref = 'dealer', cascade='all, delete-orphan', lazy=True)


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    feedbacks = relationship('Feedback', backref = 'customer', lazy = True)
    orders = relationship('Order', backref = 'customer', lazy = True)


