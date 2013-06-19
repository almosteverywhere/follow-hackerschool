from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base

class User(object):
    def __init__(self, token, secret):
        self.token = token
        self.secret = secret

class Batch(Base):
    __tablename__ = 'batch'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Batch Name %r>' % self.name

class Person(Base):
    __tablename__='person'
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey('batch.id'))
    name = Column(String(80))
    twitter_screen_name = Column(String(16))

    batch = relationship('Batch', backref=backref('person', order_by=id))

    def __init__(self, name, twitter):
        self.name = name
        self.twitter_screen_name = twitter

    def __repr__(self):
        return '<Name %r Twitter Name %r>' % (self.name, self.twitter_screen_name)

    @staticmethod
    def people_in_batches(batch_ids):
        return Person.query.filter(Person.batch_id.in_(batch_ids)).all()

