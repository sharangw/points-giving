# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import date

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import bcrypt
from sqlalchemy import extract

builtin_list = list


db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.employeeid
    data.pop('_sa_instance_state')
    return data

# [START model]

class Employee(db.Model):
    __tablename__ = 'employee'

    employeeid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    pointsBalance = db.Column(db.Integer)
    pointsReceived = db.Column(db.Integer)
    pointsGiven = db.Column(db.Integer)
    admin = db.Column(db.String(1), default="0")

    @property
    def hash_password(self):
        return self.password

    @hash_password.setter
    def set_password(self, password):
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

    def verify_password(self, password):
        print("verifying")
        if bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8')):
            print("Passwords match")
            return True
        else:
            print("Passwords don't match")
            return False

    def __repr__(self):
        return "<Employee(name='%s', points=%s)" % (self.name, str(self.pointsBalance))


class Transaction(db.Model):
    __tablename__ = 'transaction'

    transactionid = db.Column(db.Integer, primary_key=True)
    transactiondate = db.Column(db.Date)
    points = db.Column(db.Integer)
    senderid = db.Column(db.Integer)
    receiverid = db.Column(db.Integer)
    message = db.Column((db.String(255)))

    def __repr__(self):
        return "<Transaction(points='%s', sender=%s, receiver=%d)" % (self.points, self.senderid, self.receiverid)

class Redemption(db.Model):
    __tablename__ = 'redemption'

    redemptionid = db.Column(db.Integer, primary_key=True)
    redemptiondate = db.Column(db.Date)
    points = db.Column(db.Integer)
    employeeid = db.Column(db.Integer)

    def __repr__(self):
        return "<Redemption(points='%s', employee=%d)" % (self.points, self.employeeid)

# [END model]


def getAllEmployees(cursor = None):
    cursor = int(cursor) if cursor else 0
    query = (Employee.query
             .filter(Employee.admin=='0')
             .order_by(Employee.name)
             .offset(cursor))
    empl = builtin_list(map(from_sql, query.all()))
    next_page = cursor
    return (empl, next_page)

def getEmployee(name,password):
    empl = Employee.query.filter_by(name=name).first()
    if (empl is not None):
        emplId = empl.employeeid
        print("emplId: {}".format(emplId))
        # password = password.encode('utf-8')
        if empl.verify_password(password):  # entered password matches one in database
            return emplId
        else:
            return "0"
    else:
        return "0"

def insertEmpl():
    print("herere")
    empDict = {  "name" : "Huevos",
                 "password": "egg",
                 "pointsReceived": 0,
                 "pointsGiven": 0,
                 "pointsBalance":0,
                 "admin": "0"
              }

    empl = Employee(**empDict)
    empl.set_password = empDict.get('password').encode('utf-8')
    db.session.add(empl)
    db.session.commit()
    return from_sql(empl)

def getEmployeeById(id):
    empl = Employee.query.filter_by(employeeid=id).first()
    print("empl {}".format(empl))
    if not empl:
        return None
    else:
        return empl

def getSentTransactionsByEmployee(emp):

    transactions = db.session.query(Transaction, Employee).\
        join(Transaction, Employee.employeeid == Transaction.receiverid).\
        filter(Transaction.senderid == emp).add_columns(
        Transaction.transactiondate, Transaction.points, Transaction.message, Employee.name).all()
    print(transactions)
    return transactions

def getReceivedTransactionsByEmployee(emp):
        transactions = db.session.query(Transaction, Employee). \
            join(Transaction, Employee.employeeid == Transaction.senderid). \
            filter(Transaction.receiverid == emp).add_columns(
            Transaction.transactiondate, Transaction.points, Transaction.message, Employee.name).all()
        print(transactions)
        return transactions

def givePoints(fromEmp, toEmp, amount, message):
    sender = getEmployeeById(fromEmp)
    receiver = getEmployeeById(toEmp)
    senderPoints = sender.pointsBalance
    print("sender points balance: {}".format(senderPoints))
    if int(senderPoints) >= amount:
        sender.pointsBalance -= amount
        sender.pointsGiven += amount
        receiver.pointsReceived += amount
        today = date.today()
        print("Today's date:", today)
        transaction = Transaction(transactiondate=today, points=amount, senderid = int(fromEmp), receiverid = toEmp, message=message)
        db.session.add(transaction)
        db.session.commit()
        return True
    else:
        return False

def redeemPoints(emp, amount):
    redeemer = getEmployeeById(emp)
    pointsToRedeem = amount
    currentPoints = redeemer.pointsReceived
    print("redeemer points to redeem: {}".format(currentPoints))
    if int(currentPoints) >= pointsToRedeem:
        redeemer.pointsReceived -= pointsToRedeem
        today = date.today()
        redemption = Redemption(redemptiondate=today, points=pointsToRedeem, employeeid = int(emp))
        db.session.add(redemption)
        db.session.commit()
        return True
    else:
        return False

def getAllRedemptions():
    redemptions = db.session.query(Redemption, Employee).join(Redemption, Employee.employeeid == Redemption.employeeid).add_columns(Redemption.redemptiondate, Redemption.points, Employee.name).all()
    return redemptions

def getRedemptionsByEmployee(emp):
    redemptions = db.session.query(Redemption, Employee).\
        join(Redemption, Employee.employeeid == Redemption.employeeid).\
        filter(Redemption.employeeid == emp).add_columns(
        Redemption.redemptiondate, Redemption.points, Employee.name).all()
    return redemptions

def getRedemptionsByMonth(month):
    months = dict(January=1, February=2, March=3, April=4, May=5, June=6, July=7,
                  August=8, September=9, October=10, November=11, December=12)
    redemptions = db.session.query(Redemption, Employee). \
        join(Redemption, Employee.employeeid == Redemption.employeeid). \
        filter(extract('month', Redemption.redemptiondate)==months[month]).add_columns(
        Redemption.redemptiondate, Redemption.points, Employee.name).all()
    print(redemptions)
    return redemptions

def resultEnginetoDict(result):
    d, a = {}, []
    for rowproxy in result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)

        return a

def getAllPoints():
    result = db.engine.execute("select extract(month from transactiondate) as tmonth, sum(tra.points) as rewardsGivenOut, "
                        "sum(red.points) as rewardsCashedIn " +
                        "from points.transaction tra, points.redemption red " +
                        "group by extract(month from transactiondate);")

    d, allPoints = {}, []
    for rowproxy in result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        allPoints.append(d)

    return allPoints

def getWellLikedEmployeesByMonth(month):
    months = dict(January=1, February=2, March=3, April=4, May=5, June=6, July=7,
                  August=8, September=9, October=10, November=11, December=12)

    monthSelected = months[month]
    print("month selected {}".format(monthSelected))
    result = db.engine.execute(
        "select emp.name as name, sum(tra.points) as receivedPoints from points.transaction tra " +
        "inner join points.employee emp on tra.receiverid = emp.employeeid " +
        "where extract(month from tra.transactiondate) = " + str(monthSelected) + " "
        "group by emp.employeeid " +
        "order by receivedPoints desc " +
        "limit 5;")

    d, allPoints = {}, []
    for rowproxy in result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        allPoints.append(d)

    return allPoints

def getAllPointsByEmployee():
    result = db.engine.execute(
        "select red.employeeid, sum(red.points) as redeemedPoints, sum(tra.points) as receivedPoints from points.redemption red"+
        "inner join points.transaction tra on red.employeeid = tra.receiverid"+
        "group by red.employeeid"+
        "order by receivedPoints desc;")

    d, allPoints = {}, []
    for rowproxy in result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        allPoints.append(d)

    return allPoints

def getWellLikedEmployees():
    result = db.engine.execute(
        "select emp.name as name, sum(tra.points) as receivedPoints from points.transaction tra "+
        "inner join points.employee emp on tra.receiverid = emp.employeeid "+
        "group by emp.employeeid "+
        "order by receivedPoints desc "+
        "limit 5;")

    d, pointsReceivedByEmp = {}, []
    for rowproxy in result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        pointsReceivedByEmp.append(d)

    return pointsReceivedByEmp

def getStingyEmployees():

    # result = db.engine.execute("select name, pointsGiven, 1000-pointsGiven as pointsRemaining from points.employee "
    #                            "where pointsGiven < 1000 and admin = \"0\" " +
    #                            "order by pointsGiven asc;")

    ## use view
    result = db.engine.execute("select * from noPointsGiven;")

    d, pointsNotGiven = {}, []
    for rowproxy in result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        pointsNotGiven.append(d)

    return pointsNotGiven

def getNumberOfGifts(id):

    result = db.engine.execute("select count(transactionid) as gifts from points.transaction where receiverid={};".format(id))

    d, giftsReceived = {}, []
    for rowproxy in result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        giftsReceived.append(d)

        gifts = giftsReceived[0]

        return gifts['gifts']

# pointsReceived is pointsToGive
# pointsGiven is pointsToRedeem
def resetPoints():
    employees = Employee.query.all()
    for empl in employees:
        empl.pointsBalance = 1000
        empl.pointsGiven = 0
        # empl.pointsReceived = 0
        db.session.commit()

def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    init_app(app)
    with app.app_context():
        # db.create_all()
        insertEmpl()
        # getEmployeeById(15)
    # print("All tables created")
    print("User added!")

def _drop_database():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    init_app(app)
    with app.app_context():
        db.drop_all()
    print("All tables dropped")

if __name__ == '__main__':
    _create_database()



