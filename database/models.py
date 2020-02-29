from datetime import datetime, timedelta
from .db import db


class User(db.Document):
    email = db.EmailField(required=True, unique=True)
    notifId = db.StringField()
    loginPassCode = db.IntField(min_value=1000, max_value=9999)
    loginPassCodeExpires = db.DateTimeField()
    role = db.StringField(default="member")
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.createdAt:
            self.createdAt = datetime.now()
        self.updatedAt = datetime.now()
        return super(User, self).save(*args, **kwargs)


class Portfolio(db.Document):
    user = db.LazyReferenceField('User', reverse_delete_rule=2, required=True)
    name = db.StringField(required=True)
    buyTarget = db.FloatField(default=0)
    sellTarget = db.FloatField(default=0)
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now())

    def save(self, *args, **kwargs):
        if not self.createdAt:
            self.createdAt = datetime.now()
        self.updatedAt = datetime.now()
        return super(Portfolio, self).save(*args, **kwargs)


class Change(db.Document):
    date = db.StringField(required=True)
    increasing = db.IntField()
    decreasing = db.IntField()
    same = db.IntField()
    bist = db.IntField()
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.createdAt:
            self.createdAt = datetime.now()
        self.updatedAt = datetime.now()
        return super(Change, self).save(*args, **kwargs)


class Ticker(db.Document):
    name = db.StringField(required=True)
    rsi = db.FloatField()
    ninja = db.FloatField()
    fk = db.FloatField()
    pd_dd = db.FloatField()
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.createdAt:
            self.createdAt = datetime.now()
        self.updatedAt = datetime.now()
        return super(Ticker, self).save(*args, **kwargs)


class Transaction(db.Document):
    user = db.LazyReferenceField('User', reverse_delete_rule=2, required=True)
    name = db.StringField(required=True)
    price = db.FloatField()
    amount = db.FloatField()
    kind = db.StringField()
    informCount = db.IntField()
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.createdAt:
            self.createdAt = datetime.now()
        self.updatedAt = datetime.now()
        return super(Transaction, self).save(*args, **kwargs)
