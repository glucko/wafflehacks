#Imports
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth, db
from flask import Flask, request
from functools import wraps
from dotenv import load_dotenv
import os

#App configuration

app = Flask(__name__)
#Connect to firebase
load_dotenv()
cred = credentials.Certificate('fbadminconfig.json')
firebase = firebase_admin.initialize_app(cred, 
{
    'databaseURL': "https://wafflehacks-284f7-default-rtdb.firebaseio.com/"
})
pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))

def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except:
            return {'message':'Invalid token provided.'},400
        return f(*args, **kwargs)
    return wrap

#Api route to sign up a new user
@app.route('/api/signup')
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    print(request.data)
    if email is None or password is None:
        return {'message': 'Error missing email or password'},400
    try:
        print(email, password)
        user = auth.create_user(
               email=email,
               password=password
        )
        ref = db.reference('/users')
        ref.set(
            {
                user.uid: {
                    'email': email,
                    'password': password,
                    'rating': 0
                }
            }
        )
        return {'message': f'Successfully created user {user.uid}'},200
    except:
        return {'message': 'Error creating user'},400

#Api route to get a new token for a valid user
@app.route('/api/token')
def token():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return {'token': jwt}, 200
    except:
        return {'message': 'There was an error logging in'},400

#connect to firebase database and publish json data
@app.route('/api/publish', methods=['PUT'])
@check_token
def publish_data():
    token = auth.verify_id_token(request.headers['authorization'])
    user = auth.get_user(token['uid'])
    print(user.uid, user.email)
    ref = db.reference("/events")
    data = {
        'name': request.form.get('name'),
        'location': request.form.get('location'),
        'description': request.form.get('description'),
        'time': request.form.get('time'),
        'rating': 0,
        'user': user.uid
    }
    ref.set(data)
    return {'message': 'Successfully published data'},200

@app.route('/api/getdata')
def get_data():
    ref = db.reference("/events")
    data = ref.get()
    return {'data': data}, 200

def get_user_info(uid):
    return users[uid]


if __name__ == '__main__':
    app.run(debug=True)