
from engine import training
import csv
import pickle
import pandas as pd
# from gridfs import GridFS
from flask import Flask, render_template, url_for, request, session, redirect
import os
from flask_pymongo import PyMongo
# import bcrypt
# from bson import ObjectId
import re
import nltk
import random
# import create_db
host = "0.0.0.0"
port = 5000
app = Flask(__name__)
app.secret_key = "testing"
app.config["SECRET_KEY"]
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/shanna_db'
app.config['MONGO_URI'] = 'mongodb+srv://admin:AYiafjctmADP7Vot@cluster0.lmml9uf.mongodb.net/test-db?retryWrites=true&w=majority'
#app.config['FILE_UPLOADS'] = "C:\\Users\\Osama\\Downloads\\Sandeep Project\\App\\static\\files"
mongo = PyMongo(app)
# reg_users = mongo.db['register_users']
sentiment_model = training()

# create_db.createDB()


@app.route('/')
def index():

    return render_template('main.html')


@app.route('/about')
def about_us():
    return render_template('about.html')


@app.route('/user_login', methods=['POST'])
def login_user():
    # return redirect(url_for('dashboard'))
    user_collection = mongo.db.register_users
    # user_collection = reg_users
    # print(f'user collection {user_collection}')
    if request.method == 'POST':
        print('yesssss')
        username = request.form['email']
        password = request.form['password']
        login_user = user_collection.find_one({'email': username})
        valid = email_valid(em1=username, em2=login_user['email'])
        if login_user['is_verified']:
            if login_user and valid:
                if login_user['password'] == password:
                    session['email'] = username
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('/'))
            return 'Invalid username/password combination || OR || click on GET Started For Free to Signup'
        else:
            return 'User is Not Verified'


@app.route('/user_signup', methods=['POST'])
def signup_user():
    user_collection = mongo.db.register_users
    if request.method == 'POST':
        val = gen_val()
        while(user_collection.find_one({'code': val}) is not None):
            val = gen_val()
        user = request.form["email"]
        pwd = request.form["password"]
        existing_user = user_collection.find_one({'email': user})
        if existing_user is None:
            user_collection.insert_one(
                {'email': user, 'password': pwd, 'is_verified': False, 'code': val})
            session['email'] = request.form['email']
            print(f'validate at:- http://{host}:{port}/validation/{val}')
            return redirect(url_for('index'))
            # return "user registered"
        else:
            return redirect(url_for('dashboard'))
            # return "user already exists"

# Val Function


@app.route('/validation/<value>')
def validation(value):
    user_collection = mongo.db.register_users
    existing_code = user_collection.find_one({'code': value})
    if existing_code is not None and not existing_code['is_verified']:
        user_collection.update_one(
            {"code": value}, {"$set": {'is_verified': True}})
        return('User Validated')
    else:
        return('User Don\'t exists or already validated')


## IDK Why these Funtions Exist ##

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

## IDK Why these Funtions Exist ##


@app.route('/results', methods=['POST', 'GET'])
def model_result():
    return render_template('download.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/download')
def download():
    return render_template('download.html')


@app.route('/datafile', methods=['GET', 'POST'])
def uploadfile():
    print("File Uploading")
    if request.method == 'POST' and request.files:
        uploaded_file = request.files['csvfile']
        #model_name = request.form['modelname']
        # print('file name is:', str(uploaded_file).split('.')[-1])
        # print('file name is:::', uploaded_file)
        if 'csv' in str(uploaded_file):
            df = pd.read_csv(uploaded_file)
        elif 'xlsx' in str(uploaded_file):
            df = pd.read_excel(uploaded_file)
        else:
            return "Please upload file with .csv or .xslx extension"
        coloms = df.columns
        # print('coloms are:', coloms)

        df['text'] = df[coloms[1]]
        # print('text is::::', df['text'])

        #df = df.iloc[:500,:]
        # df.dropna(inplace=True)

        df['clean_text'] = df['text'].apply(sentiment_model.clean_text)
        # df.dropna(inplace=True)
        # print('clean text:', df['clean_text'])
        df['sentiment'] = df['clean_text'].apply(
            sentiment_model.sentiment_scores)
        # print(df['sentiment'])

        df.to_csv('static/file/results2.csv')
        tmp = df['sentiment'].value_counts()
        x = list(tmp.index)
        y = list(tmp.values)
        df['text_len'] = df['text'].apply(lambda x: len(str(x).split()))
        tmp2 = df['text_len'].value_counts()
        x2 = list(tmp2.index)
        y2 = list(tmp2.values)
        total = 0
        for item in tmp.values:
            total += int(item)
        y_perc = [item*100/total for item in y]
        return render_template('charts.html', x=x, y=y, x2=x2, y2=y2, y_perc=y_perc)


def gen_val():
    random_string = ""
    for _ in range(32):
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        random_string += (chr(random_integer))
    return random_string


def email_valid(em1: str, em2: str):
    user_collection = mongo.db.register_users
    user = user_collection.find_one({'email': em1})
    user_val = user_collection.find_one({'email': em2})

    validator_string = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    req = re.fullmatch(validator_string, user['email'])

    if user['email'] == user_val['email'] and req:
        return(True)
    else:
        return(False)


print(f'http://{host}:{port}/')

if __name__ == '__main__':
    app.secret_key = "ImaBarbieGirl"
    app.run(host=host, port=port)
