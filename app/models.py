from app import db, app
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))

    @staticmethod
    def generateConfirmationToken(email):
        serializer = Serializer(app.config['SECRET_KEY'])
        return serializer.dumps({'email': email}, salt=app.config['SECURITY_PASSWORD_SALT'])


    @staticmethod
    def confirmToken(token, expiration=300):
        serializer = Serializer(app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )['email']
        except:
            return None
        return email
        
    def __repr__(self):
        return '<User %r>' % self.username
    
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bio = db.Column(db.String(500))
    profile_picture = db.Column(db.String(100))
    user = db.relationship('User', backref='profile')
    
class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='journal_entries')
