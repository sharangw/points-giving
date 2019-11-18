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
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import redirect

from points import get_model
# from flask import Blueprint, redirect, render_template, request, url_for, jsonify

import ast, json

crud = Blueprint('crud', __name__)

@crud.route('/givepoints/<id>', methods=['GET', 'POST'])
def givePoints(id):

    empl = get_model().getEmployeeById(id)
    balancePercent = (1000-empl.pointsGiven)*100/1000
    numberOfGifts = get_model().getNumberOfGifts(id)

    token = request.args.get('page_token', None)

    if token:
        token = token.encode('utf-8')

    # employees = get_model().getAllEmployees()
    employees, next_page_token = get_model().getAllEmployees(cursor=token)
    print(type(employees))

    if request.method == 'POST':
        empSelected = request.form.get("employees")
        empDict = ast.literal_eval(empSelected)
        empId = empDict['id']
        print("empId selected: {}".format(empId))
        if empId == int(id): # can't choose themselves from the list
            print("cant choose yourself")
            return render_template("givepoints.html", empl=empl, employees=employees, invalid=True,  balancePercent=balancePercent, numberOfGifts=numberOfGifts)
        else:
            points = request.form.get("points")
            message = request.form.get("message")
            print("points: {}".format(points))
            points = int(points)
            sentPoints = get_model().givePoints(id,empId,points,message)
            if sentPoints:
                pointsBalance = empl.pointsReceived - empl.pointsGiven
                balancePercent = (1000 - empl.pointsGiven) * 100 / 1000
                return render_template("givepoints.html", empl=empl, employees=employees, pointsSent=True, balancePercent=balancePercent, numberOfGifts=numberOfGifts)
            else:
                return render_template("givepoints.html", empl=empl, employees=employees, balanceError=True, balancePercent=balancePercent, numberOfGifts=numberOfGifts)

    return render_template("givepoints.html", empl=empl, employees=employees, balancePercent=balancePercent, numberOfGifts=numberOfGifts)

@crud.route('/redeempoints/<id>', methods=['GET', 'POST'])
def redeemPoints(id):

    empl = get_model().getEmployeeById(id)
    balancePercent = (1000 - empl.pointsGiven) * 100 / 1000
    numberOfGifts = get_model().getNumberOfGifts(id)

    if request.method == 'POST':
        points = request.form.get("points")
        print("points to redeem: {}".format(points))
        points = int(points)
        redeemedPoints = get_model().redeemPoints(id,points)
        if redeemedPoints:
            pointsBalance = empl.pointsReceived - empl.pointsGiven
            balancePercent = (1000-empl.pointsGiven)*100/1000
            return render_template("redeem.html", empl=empl, pointsRedeemed=True, balancePercent=balancePercent, numberOfGifts=numberOfGifts)
        else:
            return render_template("redeem.html", empl=empl, balanceError=True, balancePercent=balancePercent, numberOfGifts=numberOfGifts)

    return render_template("redeem.html", empl=empl, balancePercent=balancePercent, numberOfGifts=numberOfGifts)

@crud.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        name = data['username']
        password = data['password']
        print("name: {}".format(name))
        print("password: {}".format(password))
        emplId = get_model().getEmployee(name,password)
        print("emplID: {}".format(emplId))
        if emplId == "0":
            print("wrong credentials")
            return render_template("login.html", invalid = True)
        else:
            empl = get_model().getEmployeeById(emplId)
            print("admin? {}".format(empl.admin))
            if empl.admin == 1:
                return redirect("/admin/{}".format(emplId))
            else:
                return redirect("/home/{}".format(emplId))

    return render_template("login.html") #, user={}, invalid = False)

@crud.route('/transactions/<id>')
def transactions(id):

    empl = get_model().getEmployeeById(id)

    sentTransactions = get_model().getSentTransactionsByEmployee(id)
    receivedTransactions = get_model().getReceivedTransactionsByEmployee(id)

    return render_template("transaction.html", empl=empl, sentTransactions=sentTransactions, receivedTransactions = receivedTransactions)

@crud.route('/home/<id>')
def userHome(id):
    empl = get_model().getEmployeeById(id)

    # pointsBalance = empl.pointsReceived - empl.pointsGiven
    balancePercent = (1000-empl.pointsGiven)*100/1000

    numberOfGifts = get_model().getNumberOfGifts(id)

    return render_template("index.html", empl = empl, balancePercent = balancePercent, numberOfGifts=numberOfGifts)

@crud.route('/admin/<id>', methods=['GET', 'POST'])
def adminHome(id):
    empl = get_model().getEmployeeById(id)

    allPoints = get_model().getAllPoints()

    pointsReceivedByEmp = get_model().getWellLikedEmployees()

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    if request.method == 'POST':
        if request.form.get("months") is not None:
            monthSelected = request.form.get("months")
            pointsReceivedByEmp = get_model().getWellLikedEmployeesByMonth(monthSelected)
            return render_template("admin.html", empl=empl, allPoints=allPoints,
                                   pointsReceivedByEmp=pointsReceivedByEmp, months=months, monthSelected="in " + monthSelected)

        if request.form.get("reset") is not None:
            print("reset all points")
            get_model().resetPoints()
            pointsNotGiven = get_model().getStingyEmployees()
            return render_template("leftover.html", empl=empl, pointsNotGiven=pointsNotGiven)

    return render_template("admin.html", empl = empl, allPoints=allPoints, pointsReceivedByEmp=pointsReceivedByEmp, months=months)

@crud.route('/admin/<id>/leftovers', methods=['GET', 'POST'])
def adminLeftovers(id):
    empl = get_model().getEmployeeById(id)

    pointsNotGiven = get_model().getStingyEmployees()

    if request.method == 'POST':
        print("reset all points")
        get_model().resetPoints()

    return render_template("leftover.html", empl = empl, pointsNotGiven=pointsNotGiven)

@crud.route('/admin/<id>/redemptions', methods=['GET', 'POST'])
def adminRedemptions(id):
    redemptions = get_model().getAllRedemptions()
    empl = get_model().getEmployeeById(id)

    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')
    employees, next_page_token = get_model().getAllEmployees(cursor=token)

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    if request.method == 'POST':

        # view by employee
        if request.form.get("employees") is not None:
            empSelected = request.form.get("employees")
            empDict = ast.literal_eval(empSelected)
            empId = empDict['id']
            redemptions = get_model().getRedemptionsByEmployee(empId)

        # view by month
        if request.form.get("months") is not None:
            monthSelected = request.form.get("months")
            redemptions = get_model().getRedemptionsByMonth(monthSelected)

        # reset points
        print("reset all points")
        get_model().resetPoints()

        return render_template("redemptions.html", redemptions=redemptions, empl=empl, employees=employees, months=months)

    return render_template("redemptions.html", redemptions=redemptions, empl = empl, employees=employees, months=months)


# @crud.route('/info')
# def showinfo():
#     return render_template("info.html")
#
# # [START list]
# @crud.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         user = request.form.to_dict(flat=True)
#         userCreated = get_model().create(user)
#         if (userCreated):
#             print("yes")
#             return redirect("/")
#         else:
#             print("no")
#
#     return render_template("signup.html")
#

# @crud.route('/events/<id>')
# def showEventsById(id):
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     events = get_model().showEventsByUser(id)
#
#     users = get_model().getUserById(id)
#     return render_template("myevents.html", events = events, users = users)
#
# @crud.route('/<id>')
# def view(id):
#     user = get_model().read(id)
#     return render_template("view.html", user=user)
#
# @crud.route('/<id>/events', methods=['GET', 'POST'])
# def showEvents(id):
#
#     events = get_model().showAllEventsAndVenue()
#     users = get_model().getUserById(id)
#
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     venues, next_page_token = get_model().showAllVenues(cursor=token)
#
#     if request.method == 'POST':
#         venueSelected = request.form.get("venues")
#         print(type(venueSelected))
#         if venueSelected is not None:
#             venueDict = ast.literal_eval(venueSelected)
#             venueId = venueDict['id']
#             print("venue selected: {}".format(venueId))
#             filteredEvents = get_model().showEventByVenue(venueId)
#             print("events by venue: {}".format(events))
#
#         else:
#             return render_template("events.html", events = events, users = users, venues = venues, next_page_token = next_page_token)
#
#         return render_template("events.html", events=filteredEvents, users = users, venues = venues, next_page_token = next_page_token)
#
#
#     return render_template("events.html", events = events, users = users, venues = venues, next_page_token = next_page_token)
#
# @crud.route('/<uid>/join/<eid>', methods=['GET', 'POST'])
# def joinEvent(uid, eid):
#
#     events = get_model().getEventById(eid)
#     users = get_model().getUserById(uid)
#
#     if request.method == 'POST':
#         userAdded = get_model().addUserToEvent(uid, eid)
#         if userAdded == 0:
#             print("User cannot be added to this event")
#             return render_template("join.html", events = events, users = users, eventFull = True, playerAdded = False)
#         elif userAdded == -1:
#             print("Player already added")
#             return render_template("join.html", events = events, users = users, playerAdded=True, eventFull = False)
#         else:
#             return redirect("/events/{}".format(uid))
#
#     return render_template("join.html", events = events, users = users, eventFull = False, playerAdded = False)
#
# @crud.route('/events')
# def showAllEvents():
#
#     events = get_model().showAllEventsAndVenue()
#     print(type(events))
#     print("events: {}".format(events[0]))
#
#     return render_template("browseEvents.html", events = events)
#
# @crud.route('/venues')
# def showAllVenues():
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     venues, next_page_token = get_model().showAllVenues(cursor=token)
#     return render_template("venues.html", venues = venues, next_page_token = next_page_token)
#
# # [START add]
# @crud.route('/add', methods=['GET', 'POST'])
# def add():
#     if request.method == 'POST':
#         data = request.form.to_dict(flat=True)
#
#         user = get_model().create(data)
#
#         return redirect(url_for('.view', id=user['id']))
#
#     return render_template("form.html", action="Add", user={})
#
#
# ### Admin functionalities: ####
#
# @crud.route('/admin', methods=['GET', 'POST'])
# def admin():
#     if request.method == 'POST':
#         data = request.form.to_dict(flat=True)
#         email = data['email']
#         password = data['password']
#         print("email: {}".format(email))
#         userId = get_model().getadmin(email, password)
#         if userId == "0":
#             print("wrong credentials")
#             return render_template("admin.html", invalid = True, notAdmin = False)
#         elif userId == "-1":
#             print("not an admin")
#             return render_template("admin.html", notAdmin = True, invalid = False)
#         else:
#             return redirect("/admin/events/{}".format(userId))
#
#     return render_template("admin.html", user={}, invalid = False, notAdmin = False)
#
# @crud.route('/admin/events/<id>')
# def showEventsByIdAdmin(id):
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     events = get_model().showEventsByUser(id)
#
#     users = get_model().getUserById(id)
#     return render_template("adminevents.html", events = events, users = users)
#
# @crud.route('/admin/events', methods=['GET', 'POST'])
# def showAllEventsAdmin():
#
#     events = get_model().showAllEventsAndVenue()
#
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#     eventsToRemove, next_page_token = get_model().showAllEvents(cursor=token)
#
#     if request.method == 'POST':
#         eventSelected = request.form.get("eventsToRemove")
#         print(type(eventSelected))
#         print("eventssss: {}".format(eventSelected))
#         if eventSelected is not None:
#             eventList = eventSelected.split(',')
#             eventId = eventList[4].strip().split(':')[1] # parse from "'id': <id>" to "<id>"
#             print("event id: {}".format(eventId))
#             get_model().deleteEvent(eventId)
#         return redirect("/admin/events")
#
#     return render_template("browseEventsAdmin.html", events = events, eventsToRemove = eventsToRemove, next_page_token = next_page_token)
#
# @crud.route('/admin/users', methods=['GET', 'POST'])
# def list():
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     users, next_page_token = get_model().showAllUsers(cursor=token)
#
#     if request.method == 'POST':
#         userSelected = request.form.get("users")
#         print(type(userSelected))
#         userDict = ast.literal_eval(userSelected)
#         print("user dict: {}".format(userDict))
#         userId = userDict['id']
#         print("user id: {}".format(userId))
#         get_model().deleteUser(userId)
#
#         return redirect("/admin/users")
#
#     return render_template(
#         "adminUsers.html",
#         users=users,
#         next_page_token=next_page_token)
#
# @crud.route('/admin/venues', methods=['GET', 'POST'])
# def showAllVenuesAdmin():
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     venues, next_page_token = get_model().showAllVenues(cursor=token)
#
#     if request.method == 'POST':
#         venueSelected = request.form.get("venues")
#         print(type(venueSelected))
#         venueDict = ast.literal_eval(venueSelected)
#         venueId = venueDict['id']
#         print("venue id: {}".format(venueId))
#         get_model().deleteVenue(venueId)
#         return redirect("/admin/venues")
#
#     return render_template("adminVenues.html", venues = venues, next_page_token = next_page_token)
#
# @crud.route('/admin/add', methods=['GET','POST'])
# def addVenue():
#     if request.method == 'POST':
#         venue = request.form.to_dict(flat=True)
#         venueCreated = get_model().createVenue(venue)
#         if (venueCreated):
#             print("yes")
#             return redirect("/admin/venues")
#         else:
#             print("no")
#
#     return render_template("adminAddVenue.html")
#
#
# ### Endpoints for Android app:
#
# @crud.route('/app/signup', methods=['GET', 'POST'])
# def signupApp():
#     if request.method == 'POST':
#         user = request.form.to_dict(flat=True)
#         print(user)
#         userCreated = get_model().create(user)
#         if (userCreated):
#             return "True"
#         else:
#             return "False"
#
# @crud.route('/app/login', methods=['GET', 'POST'])
# def loginApp():
#     if request.method == 'POST':
#         data = request.form.to_dict(flat=True)
#         email = data['email']
#         password = data['password']
#         print("email: {}".format(email))
#         userId = get_model().getuser(email, password)
#
#         if userId == "0":
#             print("wrong credentials")
#             return jsonify(None)
#         else:
#             users = get_model().getUserByIdApp(userId)
#             userJson = jsonify(users)
#             return userJson
#
# @crud.route('/app/admin', methods=['GET', 'POST'])
# def adminApp():
#     if request.method == 'POST':
#         data = request.form.to_dict(flat=True)
#         email = data['email']
#         password = data['password']
#         print("email: {}".format(email))
#         userId = get_model().getadmin(email, password)
#         print(userId)
#         if userId == "0":
#             error = "Invalid"
#             return error
#         elif userId == "-1":
#             error = "Not admin"
#             return error
#         else:
#             users = get_model().getUserByIdApp(userId)
#             userJson = jsonify(users)
#             return userJson
#
# @crud.route('/app/events')
# def showAllEventsApp():
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     events, next_page_token = get_model().showAllEventsApp(cursor=token)
#     print(type(events))
#     print(events)
#     if events is not None:
#         eventsJson = jsonify(events)
#         return eventsJson
#     else:
#         return jsonify(None)
#
#
# @crud.route('/app/venues')
# def showAllVenuesApp():
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     venues, next_page_token = get_model().showAllVenuesApp(cursor=token)
#     print(type(venues))
#     print(venues)
#     if venues is not None:
#         venuesJson = jsonify(venues)
#         return venuesJson
#     else:
#         return jsonify(None)
#
# @crud.route('/app/users', methods=['GET', 'POST'])
# def showAllUsersApp():
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#
#     users, next_page_token = get_model().showAllUsersApp(cursor=token)
#
#     print(type(users))
#     print(users)
#     if users is not None:
#         usersJson = jsonify(users)
#         return usersJson
#     else:
#         return jsonify(None)
#
# @crud.route('/app/events/<id>', methods=['GET', 'POST'])
# def showEventsByIdApp(id):
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')
#     events = get_model().showEventsByUserApp(id)
#
#     print(type(events))
#     print(events)
#     if events is not None:
#         eventsJson = jsonify(events)
#         return eventsJson
#     else:
#         return "None"
#
# @crud.route('/app/<uid>/join/<eid>', methods=['GET', 'POST'])
# def joinEventApp(uid, eid):
#
#     events = get_model().getEventById(eid)
#     users = get_model().getUserById(uid)
#
#     if request.method == 'GET':
#         userAdded = get_model().addUserToEvent(uid, eid)
#         if userAdded == 0:
#             return "User cannot be added to this event"
#         elif userAdded == -1:
#             return "Player already added"
#         else:
#             return "Success"
#
# @crud.route('/app/<uid>/leave/<eid>', methods=['GET', 'POST'])
# def leaveEventApp(uid, eid):
#
#     events = get_model().getEventById(eid)
#     users = get_model().getUserById(uid)
#
#     if request.method == 'GET':
#         userAdded = get_model().removeUserFromEvent(uid, eid)
#         if userAdded == 0:
#             return "No players in this event"
#         elif userAdded == -1:
#             return "Player has not joined this event"
#         else:
#             return "Success"
#
# @crud.route('/app/admin/users/<id>', methods=['GET', 'POST'])
# def removeUserApp(id):
#
#     get_model().deleteUser(id)
#
#     return "Deleted user"
#
# @crud.route('/app/admin/events/<id>', methods=['GET', 'POST'])
# def removeEventsApp(id):
#
#     get_model().deleteEvent(id)
#
#     return "Deleted event"
#
# @crud.route('/app/admin/venues/<id>', methods=['GET', 'POST'])
# def removeVenuesApp(id):
#
#     get_model().deleteVenue(id)
#
#     return "Deleted venue"
#
# @crud.route('/app/admin/venue/add', methods=['GET','POST'])
# def addVenueApp():
#     if request.method == 'POST':
#         venue = request.form.to_dict(flat=True)
#         venueCreated = get_model().createVenue(venue)
#         if (venueCreated):
#             return "Success"
#         else:
#             return "Failure"
#
# @crud.route('/app/admin/event/add', methods=['GET','POST'])
# def addEventApp():
#     if request.method == 'POST':
#         event = request.form.to_dict(flat=True)
#         eventCreated = get_model().createEvent(event)
#         if (eventCreated):
#             return "Success"
#         else:
#             return "Failure"
#
#
# @crud.route('/app/events/search', methods=['GET'])
# def searchEventsApp():
#
#     if request.method == 'GET':
#         query = request.args.get('description')
#
#         events = get_model().searchEvents(query)
#         eventsJson = jsonify(events)
#
#         return eventsJson
#
#     else:
#         return "Failure"






