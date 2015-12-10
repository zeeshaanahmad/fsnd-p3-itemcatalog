# app.py
#
# Project: FSND P3 - Item Catalog
# Author: Zeeshan Ahmad
# Email: ahmad.zeeshaan@gmail.com
#
# Description: This app.py python file provides the REST endpoint for
# Item Catalog application. It implements flask, sqlalchemy and oauth2.
# Some of the code is taken from OAuth course lectures for sign in using
# Google or Facebook with slight modifications.

# Imports
from flask import Flask, render_template, request, jsonify, make_response
from flask import url_for, redirect, flash, session as login_session
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item, User
import json
from werkzeug import secure_filename
import time
import os
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
from functools import wraps
from dicttoxml import dicttoxml

# Initializes flask app with templates folder already defined
app = Flask(__name__, template_folder='templates')

# Reads client_secrets.json file to get client_id value for Google Sign in
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Creates an sqlite database name itemcatalogwithusers
engine = create_engine('sqlite:///itemcatalogwithusers.db')
Base.metadata.bind = engine

# Session for querying and editing database
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Allowed extensions for item image upload. File will be dicarded if any other
# extension is uploaded
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', 'png'])

# Defines the folder on filesystem where the uploaded images will be stored
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Defines maximum size of a document upload which cannot be higher than 5 MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


# Adding a decorated function to check for login before requests are handled
# by methods. This will avoid repetition of code.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print '>>>> checking login...'
        if 'username' not in login_session:
            return render_template('login.html', STATE=generateRandom())
        else:
            if request.args.get('state') != login_session['state']:
                response = make_response(
                    json.dumps('Invalid state parameter.'),
                    401)
                response.headers['Content-Type'] = 'application/json'
                return response
        return f(*args, **kwargs)
    return decorated_function

# Generates a random alpha-numeric string which is kept in login_session as
# state and passed with call from client to server to prevent CSRF


def generateRandom():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return state

# This method takes the login_session object and creates a new user in the
# database
# Returns the id of newly created user


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Retreives the user information from User table in database based on user id
# Returns an object of User instance


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# Based on email provided, it queries the database for the user having same
# email.
# Returns user id if found a user, other returns None


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# It renders the login.html file from templates folder along with a context
# variable called STATE which has the randomly generated value.
# render_template function replaces STATE variable in login.html file,
# whereever it is referenced like this {{STATE}}
@app.route('/login')  # Handles all the requests which have the following
# url pattern
# i.e. <serverdomain:port>/login
def showLogin():
    return render_template('login.html', STATE=generateRandom())

# This method implements OAuth2 using Google Sign in. It also adds the new
# user to database. This code is taken from
# Udacity's Authentication & Authorization: OAuth course


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                    connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Adding the user to database if it doesn't already exist
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = 'Successfully logged in!'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Used for logging out of the application for google sign in


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['credentials']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token   # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Handles the sign in using facebook


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (   # noqa
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token   # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = 'Successfully logged in!'

    flash("Now logged in as %s" % login_session['username'])
    return output

# Handles logging out of application for facebook sign in


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)   # noqa
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider. One stop logout. It further decides which
# provider was used and logout the user by clearing the session.


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLogin'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLogin'))

# Checks for allowed extensions for file upload


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# converts data to xml


def convert_to_xml(data_to_convert):
    # data=[i.serialize for i in data_to_convert]
    xml = dicttoxml(data_to_convert, attr_type=True)
    return xml

# Takes the xml data and converts to response object for returning results
# in xml


def make_xml_response(xml):
    response = make_response(xml)
    response.headers["Content-Type"] = "application/xml"
    return response


# Checks whether the login_session is available


@app.route('/checkLoggedIn')
def checkLoggedIn():
    if 'username' not in login_session:
        return jsonify(loggedIn=False)
    else:
        if request.args.get('state') != login_session['state']:
            return jsonify(loggedIn=False)
        return jsonify(loggedIn=True)

# Handles any request which is of the
# pattern <serverdomain:port>/ or <serverdomain:port>/index
# Checks if the valid login session exists, then renders the index.html page
# from templates folder and replaces STATE, USERNAME, PICTURE according to
# context variables being set in render_template method arguments


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template(
        'index.html',
        STATE=login_session['state'],
        USERNAME=login_session['username'],
        PICTURE=login_session['picture'])

# Retreieves all the categories in database Category table
# Response is sent to client as JSON object
# Accepts f=xml parameter to return result in xml format


@app.route('/categories/all')
@login_required
def getAllCategories():
    cats = session.query(Category).all()
    if (request.args.get('f') == 'xml'):
        return make_xml_response(
            convert_to_xml([i.serialize for i in cats]))
    return jsonify(categories=[i.serialize for i in cats])


# Gets all items for selected category
# <int:category_id> means that this method expects the URL to have a
# category id
# Queries the database,
#     1 - for retreiving the items added by user only,
#     2 - for retreiving the items added by other users
# Returns the response as JSON object with two properties ie. userItems,
# itemsByOtherUsers
# Accepts f=xml parameter to return result in xml format


@app.route('/categories/<int:category_id>/items/all')
@login_required
def getAllItemsByCategoryId(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    userItems = session.query(Item).filter(
        and_(Item.category_id == category.id,
             Item.user_id == login_session['user_id']))
    itemsByOtherUsers = session.query(Item).filter(
        and_(Item.category_id == category.id,
             Item.user_id != login_session['user_id']))
    if (request.args.get('f') == 'xml'):
        userItems = [i.serialize for i in userItems]
        itemsByOtherUsers = [j.serialize for j in itemsByOtherUsers]
        return make_xml_response(
            convert_to_xml([userItems, itemsByOtherUsers]))
    return jsonify(userItems=[i.serialize for i in userItems],
                   itemsByOtherUsers=[j.serialize for j in
                                      itemsByOtherUsers])

# Gets the particular item which is mentioned in the url against <int:item_id>
# Result is returned as JSON object which contains list of items
# Accepts f=xml parameter to return result in xml format


@app.route('/categories/<int:category_id>/items/<int:item_id>')
@login_required
def getItemByCategoryIdAndItemId(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter(
        and_(Item.category_id == category.id,
             Item.id == item_id,
             Item.user_id == login_session['user_id']))
    if (request.args.get('f') == 'xml'):
        return make_xml_response(
            convert_to_xml([i.serialize for i in items]))
    return jsonify(items=[i.serialize for i in items])

# REST endpoint for new item addition. Handles the post request to get user
# input and retrieves the uploaded file. Saves the uploaded file in filesystem
# and updates the Item table in database with a new item added by user.
# Accepts f=xml parameter to return result in xml format


@app.route('/newitem/category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def addItem(category_id):
    if request.method == 'POST':
        try:
            image_src = ''
            # Checks if file is present in request and the file has proper
            # extension, then appends a date-time string with the file
            # name to keep it uniques and prevent overwriting of any
            # other user's file with same name
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = time.strftime("%Y%m%d-%H%M%S") + \
                        secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                           filename))
                    image_src = os.path.join(app.config['UPLOAD_FOLDER'],
                                             filename)

            data = request.form
            name = data['name']
            description = data['description']
            price = data['price']
            category = session.query(Category).\
                filter_by(id=category_id).one()
            item = Item(name=name, description=description,
                        price=price, image_src=image_src,
                        category=category,
                        user_id=login_session['user_id'])
            session.add(item)
            session.commit()  # New item is saved into database.
            if (request.args.get('f') == 'xml'):
                return make_xml_response(convert_to_xml({'added': True}))
            return jsonify(added=True)
        except Exception, e:
            print str(e)
            if (request.args.get('f') == 'xml'):
                return make_xml_response(convert_to_xml({'added': False}))
            return jsonify(added=False)
    else:
        if (request.args.get('f') == 'xml'):
            return make_xml_response(convert_to_xml({'added': False}))
        return jsonify(added=False)

# Handles editing of an existing item which has valid category id and item id
# and user had added the item previously.  Accepts f=xml
# parameter to return result in xml format


@app.route('/edititem/category/<int:category_id>/item/<int:item_id>',
           methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    if request.method == 'POST':
        try:
            image_src = ''
            if ('file' in request.files):
                file = request.files['file']
                if (file and file.filename != '' and
                        allowed_file(file.filename)):
                    # adding timestring to filename to prevent any
                    # duplicate file uploads
                    filename = time.strftime("%Y%m%d-%H%M%S") + \
                        secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                           filename))
                    image_src = os.path.join(app.config['UPLOAD_FOLDER'],
                                             filename)

            data = request.form
            item_name = data['name']
            item_description = data['description']
            item_price = data['price']

            item = session.query(Item).filter(
                and_(Item.category_id == category_id, Item.id == item_id,
                     Item.user_id == login_session['user_id'])).one()
            if item:
                if image_src:
                    item.name = item_name
                    item.description = item_description
                    item.price = item_price
                    item.user_id = login_session['user_id']
                    # remove any exisiting image on filesystem associated
                    # with this item
                    if item.image_src:
                        os.remove(item.image_src)
                    item.image_src = image_src
                else:
                    item.name = item_name
                    item.description = item_description
                    item.user_id = login_session['user_id']
                    item.price = item_price
                    # Do not change the image unless user provides a
                    # new image
                session.add(item)
                session.commit()
                if (request.args.get('f') == 'xml'):
                    return make_xml_response(convert_to_xml(
                        {'updated': True, 'msg': 'Record has been updated'}))
                return jsonify(updated=True,
                               msg='Record has been updated')
            else:
                if (request.args.get('f') == 'xml'):
                    return make_xml_response(convert_to_xml(
                        {'updated': False, 'msg': 'No such item exist'}))
                return jsonify(updated=False, msg='No such item exist')
        except Exception, e:
            print str(e)
            if (request.args.get('f') == 'xml'):
                return make_xml_response(convert_to_xml(
                    {'updated': False,
                     'msg': 'An error occured while trying to update \
                     this item.'}))
            return jsonify(updated=False,
                           msg='An error occured while trying to update \
                            this item.')
    else:
        if (request.args.get('f') == 'xml'):
            return make_xml_response(convert_to_xml(
                {'updated': False,
                 'msg': 'An error occured while trying to update \
                 this item.'}))
        return jsonify(updated=False,
                       msg='An error occured while trying to update \
                            this item.')


# REST endpoint for new item deletion. Handles the request to delete the item
# entry from database and any associated files from filesystem. Accepts f=xml
# parameter to return data in xml format

@app.route('/deleteitem/category/<int:category_id>/item/<int:item_id>')
@login_required
def deleteItem(category_id, item_id):
    try:
        item = session.query(Item).filter(
            and_(Item.category_id == category_id,
                 Item.id == item_id,
                 Item.user_id == login_session['user_id'])).one()
        if item:
            if item.image_src:
                img_src = item.image_src
            session.delete(item)
            session.commit()

            if img_src:
                os.remove(img_src)

            if (request.args.get('f') == 'xml'):
                return make_xml_response(convert_to_xml(
                    {'deleted': True,
                     'msg': 'Record has been deleted'}))
            return jsonify(deleted=True,
                           msg='Record has been deleted')
        else:
            if (request.args.get('f') == 'xml'):
                return make_xml_response(convert_to_xml(
                    {'deleted': False,
                     'msg': 'No such item exist'}))
            return jsonify(deleted=False, msg='No such item exist')
    except Exception, e:
        print str(e)
        if (request.args.get('f') == 'xml'):
            return make_xml_response(convert_to_xml(
                {'deleted': False,
                 'msg': 'An error occured while \
                    trying to delete this item.'}))
        return jsonify(deleted=False, msg='An error occured while \
                        trying to delete this item.')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
