from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from secrets import token_urlsafe as generate_cookie

# Relationship between Vaults and Users
class VaultSubscription(db.Model):
    __tablename__ = 'vaultSubscriptions'
    id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    vault_id = db.Column(db.BigInteger, db.ForeignKey('vaults.id'))

    state = db.Column(db.Integer, default=0)
    # 0 - not confirmed
    # 1 - accepted
    # 2 - admin
    # 3 - rejected

class PaymentState(db.Model):
    __tablename__ = 'paymentStates'
    id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    payment_id = db.Column(db.BigInteger, db.ForeignKey('vaultPayments.id'))

    state = db.Column(db.Integer, default=0)

    # 0 - confirmed
    # 1 - rejected
    # 2 - not confirmed
    

# Vault Payments
class VaultPayment(db.Model):
    __tablename__ = 'vaultPayments'
    id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    vault_id = db.Column(db.BigInteger, db.ForeignKey('vaults.id'))

    amount = db.Column(db.BigInteger, default=0)
    about = db.Column(db.String(100))

    acceptedBy = db.Column(db.BigInteger, default=0)
    accepted = db.Column(db.Boolean, default=False)
    refused = db.Column(db.Boolean, default=False)

    states = db.relationship('PaymentState', \
                            foreign_keys=[PaymentState.payment_id], \
                            backref='payment', \
                            lazy='dynamic')

    payment_since = db.Column(db.DateTime(), default=datetime.utcnow)

    def notConfirmedBy(self, userId):
        payment = self.states.filter_by(user_id=userId).first()
        if payment is None:
            return True
        return False

     

class Vault(db.Model):
    __tablename__ = 'vaults'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100))

    total = db.Column(db.BigInteger, default=0)
    NotConfirmedTotal = db.Column(db.BigInteger, default=0)

    users = db.relationship('VaultSubscription', \
            foreign_keys=[VaultSubscription.vault_id], \
            backref=db.backref('vault', lazy='joined'), \
            lazy='dynamic', \
            cascade='all, delete-orphan')

    usersAmount = db.Column(db.Integer, default=1)

    payments = db.relationship('VaultPayment', \
               foreign_keys=[VaultPayment.vault_id], \
               backref='vault',
               lazy='dynamic')

    paymentsAmount = db.Column(db.Integer, default=0)

    vault_since = db.Column(db.DateTime(), default=datetime.utcnow)    



# confirmed - ret answered request
# refused - ret refused request
# paid - ret paid request
class Debt(db.Model):
    __tablename__ = 'debts'
    id = db.Column(db.BigInteger, primary_key=True)
    about = db.Column(db.String(100))
    total = db.Column(db.BigInteger, server_default='0')
    confirmed = db.Column(db.Boolean, server_default='0')
    refused = db.Column(db.Boolean, server_default='0')
    paid = db.Column(db.Boolean, server_default='0')
    give_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    ret_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))

    debt_since = db.Column(db.DateTime(), default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True, index=True)

    # Info

    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    password_ver = db.Column(db.String(10))

    totalDebt = db.Column(db.BigInteger, server_default='0')
    notConfirmedTotalDebt = db.Column(db.BigInteger, server_default='0')

    confirmedAccount = db.Column(db.Boolean, server_default='0')

    # Debts

    give = db.relationship('Debt', foreign_keys=[Debt.give_id], backref='give', lazy='dynamic')
    ret = db.relationship('Debt', foreign_keys=[Debt.ret_id], backref='ret', lazy='dynamic')

    giveAmount = db.Column(db.Integer, server_default='0')
    retAmount = db.Column(db.Integer, server_default='0')
    notConfirmedAmount = db.Column(db.Integer, server_default='0')
    
    debtsLeft = db.Column(db.Integer, server_default='1000000000')

    # Telegram

    isTelegram = db.Column(db.Boolean, server_default='0')
    telegramNick = db.Column(db.String(128))
    telegramChatId = db.Column(db.BigInteger, server_default='0')

    # Vaults
    
    vaults = db.relationship('VaultSubscription', \
            foreign_keys=[VaultSubscription.user_id], \
            backref=db.backref('user', lazy='joined'), \
            lazy='dynamic', \
            cascade='all, delete-orphan')

    payments = db.relationship('VaultPayment', \
               foreign_keys=[VaultPayment.user_id], \
               backref='user',
               lazy='dynamic')

    paymentStates = db.relationship('PaymentState', \
                   foreign_keys=[PaymentState.user_id], \
                   backref='user',
                   lazy='dynamic')

    vaultsAmount = db.Column(db.Integer, default=0)

    # OAuth

    usingOAuth = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.BigInteger, default=0)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('Password is not available')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_ver = generate_cookie(5)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY']) 

        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False 
        

        self.confirmedAccount = True
        db.session.add(self)
        db.session.commit()

        return True

    def generate_recovery_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'recover': self.id})

    def stop_telegram(self):
        self.isTelegram = False
        db.session.commit()

    @staticmethod
    def change_password(token, password):
        s = Serializer(current_app.config['SECRET_KEY']) 

        try:
            data = s.loads(token)
        except:
            return False

        if data.get('recover') is None:
            return False

        id = data.get('recover')
        user = User.query.get(int(id))

        if user is None:
            return False
        
        user.isTelegram = False
        user.password = password
        db.session.add(user)
        db.session.commit()
        
        return True

    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
