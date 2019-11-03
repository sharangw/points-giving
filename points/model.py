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

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
import json

builtin_list = list


db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data

# [START model]
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    password = db.Column(db.String(255))
    admin = db.Column(db.String(255), default="0")

    def __repr__(self):
        return "<User(name='%s', email=%s)" % (self.name, self.email)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    organizer = db.Column(db.String(255))
    players = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    length = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    description = db.Column(db.String(255))
    venueId = db.Column(db.Integer)

    def __repr__(self):
        return "<Event(organizer='%s', description=%s, players=%d)" % (self.organizer, self.description, self.players)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    description = db.Column(db.String(255))

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Players(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    eventId = db.Column(db.Integer)


# [END model]


def addevent(data):
    event = Event(**data)
    db.session.add(event)
    db.session.commit()
    return from_sql(event)

def insertPlayers():
    player1Dict = {"userid":1, "eventid": 2}
    player2Dict = {"userid":3, "eventid": 5}

    player = Event(**player1Dict)
    db.session.add(player)
    db.session.commit()
    return from_sql(player)

def insertuser():
    userDict = { "name" : "Michael Jordan",
                 "email": "jordan@bulls.com",
                 "phone": "232323",
                  "password": "goat",
                 "admin": "1"
              }

    user = User(**userDict)
    db.session.add(user)


    db.session.commit()
    return from_sql(user)

def showEventsByUser(userId):
    playerResult = Players.query.filter_by(userId = userId).all()
    print("result: {}".format(playerResult))
    events = []
    for r in playerResult:
        print(r.eventId)
        eventResult = Event.query.filter_by(id = r.eventId).first()
        events.append(eventResult)
    print("events: {}".format(events))
    # eventsJoinVenue = db.session.query(Event,Venue).join(Event, Venue.id == Event.venueId).add_columns(Event.organizer, Event.time, Event.length, Event.description, Event.venueId, Venue.name).filter(Event.id == events.id).all()
    # playerInfo = from_sql(result)
    # print("player info: ".format(playerInfo))
    # TODO: also get venue name by joining table
    if not events:
        return None
    return events

def showEventsByUserApp(userId):
    playerResult = Players.query.filter_by(userId = userId).all()
    print("result: {}".format(playerResult))
    eventList = []
    for r in playerResult:
        print(r.eventId)
        eventResult = Event.query.filter_by(id = r.eventId).first()
        if eventResult is not None:
            eventList.append(eventResult)
    print("events: {}".format(eventList))
    events = builtin_list(map(from_sql, eventList))
    if not events:
        return None
    return events

def showAllUsers(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (User.query
             .order_by(User.name)
             .limit(limit)
             .offset(cursor))
    users = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(users) == limit else None
    return (users, next_page)

def showAllUsersApp(limit=50, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (User.query
             .order_by(User.name)
             .limit(limit)
             .offset(cursor))
    users = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(users) == limit else None
    return (users, next_page)

def showAllEvents(limit = 10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Event.query
             .order_by(Event.organizer)
             .limit(limit)
             .offset(cursor))
    events = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(events) == limit else None
    return (events, next_page)

def showAllEventsApp(limit = 50, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Event.query
             .order_by(Event.organizer)
             .limit(limit)
             .offset(cursor))
    events = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(events) == limit else None
    return (events, next_page)

def showAllVenues(limit = 10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Venue.query
             .order_by(Venue.name)
             .limit(limit)
             .offset(cursor))
    venues = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(venues) == limit else None
    print(type(venues))
    return (venues, next_page)

def showAllVenuesApp(limit = 50, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Venue.query
             .order_by(Venue.name)
             .limit(limit)
             .offset(cursor))
    venues = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(venues) == limit else None
    print(type(venues))
    return (venues, next_page)

def searchEvents(desc):

    search = "%{}%".format(desc)
    searchEventQuery = Event.query.filter(Event.description.like(search))
    events = builtin_list(map(from_sql, searchEventQuery.all()))
    print(events)
    return events

def read(id):
    result = User.query.get(id)
    if not result:
        return None
    return from_sql(result)

# [END read]

def getUserById(id):
    user = User.query.filter_by(id=id).first()
    print("user {}".format(user))
    if not user:
        return None
    else:
        return user

def getUserByIdApp(id):
    query = (User.query.filter_by(id=id).order_by(User.name))
    user = builtin_list(map(from_sql, query.all()))
    print(type(user))
    print(user)
    if not user:
        return None
    else:
        return user

def getEventById(id):
    event = Event.query.filter_by(id=id).first()
    print("time {}".format(event.time))
    print("event {}".format(event))
    if not event:
        return None
    else:
        return event

def getVenueById(id):
    venue = Venue.query.filter_by(id=id).first()
    print("venue {}".format(venue))
    if not venue:
        return None
    else:
        return venue

def addUserToEvent(uid, eid):

    dict = {'userId':uid, 'eventId':eid}
    player = Players(userId=uid, eventId=eid)

    event = Event.query.filter_by(id = eid).first()
    print("players: {}".format(event.players))

    if (event.players < event.capacity):

        playerAlreadyAdded = 0 # check if same user has joined same event

        playerEvents = Players.query.filter_by(userId = uid).with_entities(Players.eventId).all()

        pEvents = [value for value, in playerEvents] # convert to list of ints with eventIds

        if int(eid) in pEvents:
            print("event already joined")
            playerAlreadyAdded += 1
        else:
            print("event not joined")

        if playerAlreadyAdded == 0:
            event.players = event.players + 1
            db.session.add(player)
            db.session.commit()
        else:
            return -1

        return 1
    else: # players exceed capacity - event full
        return 0


def removeUserFromEvent(uid, eid):
    dict = {'userId': uid, 'eventId': eid}
    player = Players(userId=uid, eventId=eid)

    event = Event.query.filter_by(id=eid).first()
    print("players: {}".format(event.players))

    if (event.players > 0):

        playerJoined = 0  # check if user has joined the event

        playerEvents = Players.query.filter_by(userId=uid).with_entities(Players.eventId).all()

        pEvents = [value for value, in playerEvents]  # convert to list of ints with eventIds

        if int(eid) in pEvents:
            print("user can leave this event")
            playerJoined += 1
        else:
            print("user has not joined this event")

        if playerJoined == 0:
            return -1
        else:
            event.players = event.players - 1
            playerToRemove = Players.query.filter_by(userId=uid,eventId=eid).first()
            playerToRemoveId = playerToRemove.id
            print("delete player with id: {}".format(playerToRemoveId))
            db.session.query(Players).filter(Players.id == playerToRemoveId).delete()
            db.session.commit()

        return 1
    else:  # no players
        return 0

def getuser(email,password):
    userInfo = User.query.filter_by(email=email).first()
    if (userInfo is not None):
        passwordInDatabase = userInfo.password
        userId = userInfo.id
        print("userid: {}".format(userId))
        if password == passwordInDatabase:  # entered password matches one in database
            return userId
        else:
            return "0"
    else:
        return "0"

def getadmin(email,password):
    userInfo = User.query.filter_by(email=email).first()
    print(userInfo)
    if (userInfo is not None):
        passwordInDatabase = userInfo.password
        userId = userInfo.id
        admin = userInfo.admin
        print("is admin: {}".format(admin))
        if admin == "1":
            if password == passwordInDatabase:  # entered password matches one in database
                return userId
            else:
                return "0"
        else:
            return "-1" # not an admin

    else:
        return "0"


def showEventByVenue(venueId):

    events = db.session.query(Event,Venue).join(Event, Venue.id == Event.venueId).add_columns(Event.id, Event.organizer, Event.time, Event.length, Event.description).filter(Venue.id == venueId).all()
    for e in events:
        print('{}'.format(e[0].organizer))
        print('{}'.format(e[0].time))
        print('{}'.format(e[0].length))
        print('{}'.format(e[0].description))
    return events

def showAllEventsAndVenue():

    events = db.session.query(Event,Venue).join(Event, Venue.id == Event.venueId).add_columns(Event.id, Event.organizer, Event.time, Event.length, Event.description, Event.venueId, Venue.name).all()
    return events

def create(data):
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return from_sql(user)

def createVenue(data):
    venue = Venue(**data)
    db.session.add(venue)
    db.session.commit()
    return from_sql(venue)

def createEvent(data):
    event = Event(**data)
    db.session.add(event)
    db.session.commit()
    return from_sql(event)

# [END create]

def deleteEvent(eventId):
    db.session.query(Event).filter(Event.id==eventId).delete()
    db.session.commit()

def deleteUser(userId):
    db.session.query(User).filter(User.id==userId).delete()
    db.session.commit()

def deleteVenue(venueId):
    db.session.query(Venue).filter(Venue.id==venueId).delete()
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
        insertuser()
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
