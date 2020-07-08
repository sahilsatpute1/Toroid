from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from __init__ import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

subs = db.Table('subs',
db.Column('user_id',db.Integer, db.ForeignKey('user.user_id')),
db.Column('prod_id',db.Integer,db.ForeignKey('hobies.prod_id'))
)

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def get_id(self):
        return self.user_id
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{ self.first_name }','{ self.last_name }',{self.email}')"




class Hobies(db.Model):
  __tablename__ = 'hobies'
  prod_id = db.Column(db.Integer, primary_key=True)
  tag = db.Column(db.String(50), nullable=False)  
  title = db.Column(db.String(50), nullable=False) 
  content = db.Column(db.String(200), nullable=False)   
  image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
  users_prod = db.relationship('User',secondary=subs, backref=db.backref('products',lazy='dynamic'))