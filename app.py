# -*- coding: utf-8 -*-

# Imports
from scripts import tabledef
from scripts import forms
from scripts import helpers
import json
import sys
import os
import numpy as np
import datetime

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.resnet50 import ResNet50
from keras.applications.mobilenet_v2 import MobileNetV2

# Flask utils
from flask import Flask, redirect, url_for, render_template, request, session
from werkzeug.utils import secure_filename

# Clarifai API
from clarifai.rest import ClarifaiApp

# Stripe API
import stripe

app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only

# featuretoggle (to choose between the own or pretrained model and the api)
global feat_clarifai
feat_clarifai = True

# or define the model
global model
global model_to_load
model_to_load = "ResNet50"
model_to_load = "MobileNetV2"


# Heroku
# https://github.com/heroku-python/flask-heroku
# Heroku environment variable configurations for Flask.
# Postgres Database on Heroku
#from flask_heroku import Heroku
#heroku = Heroku(app)

# the upload directory
directory = "./uploads"

# make the directory if it dosen't exist
if not os.path.exists(directory):
    print("make dir: " + directory)
    os.makedirs(directory)

# Create your API key in your account's Application details page:
# https://clarifai.com/apps
clarifai_app = ClarifaiApp()

# Stripe Payment (insert your keys here)
pub_key = os.getenv('STRIPE_PUB_KEY')
secret_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = secret_key
stripe_amount = 500

# ToDo's:
# ToDo: Don't show the Plan's page when a user purchsed a plan

# Load the model to make the predictions before the first request
@app.before_first_request
def load_model():
    # Load the model
    if model_to_load == "ResNet50":
        model = ResNet50(weights='imagenet')
    elif model_to_load == 'MobileNetV2':
        model = MobileNetV2(weights='imagenet')
    print("model loaded")

# ======== Helper functions =========================================================== #
# -------- predict an image ----------------------------------------------------------- #
def model_predict(img_path):
    print("model_predict")

    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
    x = preprocess_input(x, mode='caffe')

    preds = model.predict(x)
    #del model, img, x
    return preds

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    print("login")
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    user = helpers.get_user()
    return render_template('home.html', user=user, pub_key=pub_key, amount=stripe_amount)


@app.route("/logout")
def logout():
    print("logout")
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("signup")
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    print("settings")
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))


# -------- Login ------------------------------------------------------------- #
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    print("analyze")
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user = helpers.get_user()
        print(user)
        info = helpers.get_plan(user.username)
        username, paid_plan = info
        print(info)
        # check if the user has paid and is allowed
        if not paid_plan:
            print("Free Plan")
            # get the time of the last anlayzed image
            # get last_uploaded time
            # analyzed time older than max_time
            print(helpers.get_last_image(user.username))
            username, last_image = helpers.get_last_image(user.username)
            if last_image:
                if (datetime.datetime.utcnow() - datetime.timedelta(seconds=120)) < last_image:
                    return redirect(url_for('login'))
        else:
            print("Premium Plan")


        return render_template('analyze.html', user=user)


# -------- Premium ------------------------------------------------------------- #
@app.route('/premium', methods=['GET', 'POST'])
def premium():
    print("premium")
    if not session.get('logged_in'):
        print("user is not logged in")
        return redirect(url_for('login'))
    else:
        user = helpers.get_user()
        print(user)
        return render_template('analyze.html', user=user)


# -------- Pay ------------------------------------------------------------- #
@app.route('/pay', methods=['POST'])
def pay():
    print(request.form)
    customer = stripe.Customer.create(email=request.form["stripeEmail"], source=request.form['stripeToken'])

    charge = stripe.Charge.create(customer=customer.id,
                                  amount=stripe_amount,
                                  currency='usd',
                                  description='Premium Plan')

    user = helpers.get_user()
    helpers.set_plan(user.username)
    return redirect(url_for('analyze'))

# -------- upload ---------------------------------------------------------- #
@app.route('/predict', methods=['GET', 'POST'])
def upload():
    print("upload")

    # save the prediction
    user = helpers.get_user()

    # if free plan
    # set last_uploaded time to actual time
    helpers.set_last_image(user.username)

    if request.method == 'POST':
        # Get the file from post request
        f = request.files['image']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        print("image saved")
        # Make the prediction with the clarifai api or the model
        if feat_clarifai:
            model = clarifai_app.public_models.general_model
            response = model.predict_by_filename(file_path)
            print(response)
            result = []
            items = response['outputs'][0]['data']['concepts']
            for item in items:
                # choose only the most relevant descriptions
                if item['value'] > 0.9:
                    print(item['name'] + " : " + str(int(item['value'] * 100)))
                    result.append(item['name'])
            result = ", ".join(result)
        else:
            # Make prediction
            preds = model_predict(file_path)

            # Process your result for human
            pred_class = preds.argmax(axis=-1)              # Simple argmax
            pred_class = decode_predictions(preds, top=1)   # ImageNet Decode
            result = str(pred_class[0][0][1])               # Convert to string
            print(result)
            print(decode_predictions(preds))
        return result
    return None


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
