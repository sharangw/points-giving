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







