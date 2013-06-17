import os
from flask import Flask, request, redirect, url_for, session, flash, g, \
    render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import widgets, Form, SelectMultipleField, HiddenField
from flask.ext.oauth import OAuth
from models import Base, User, Batch, Person
import requests


#----------------------------------------
# initialization
#----------------------------------------
from wtforms import ValidationError, TextField, validators, PasswordField
from wtforms.widgets import CheckboxInput

app = Flask(__name__)
app.config.from_envvar('APP_SETTINGS')
Bootstrap(app)

import helpers
db = SQLAlchemy(app)

#----------------------------------------
# oauth
#----------------------------------------
oauth = OAuth()
twitter_oauth = oauth.remote_app('twitter',
                                 base_url='https://api.twitter.com/1.1/',
                                 request_token_url='https://api.twitter.com/oauth/request_token',
                                 access_token_url='https://api.twitter.com/oauth/access_token',
                                 authorize_url='https://api.twitter.com/oauth/authenticate',
                                 consumer_key=app.config['CONSUMER_KEY'],
                                 consumer_secret=app.config['CONSUMER_SECRET']
)


@twitter_oauth.tokengetter
def get_twitter_token():
    if 'token' in session and 'secret' in session:
        return session['token'], session['secret']


@app.route('/login')
def login():
    return twitter_oauth.authorize(callback=url_for('oauth_authorized',
                                                    next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@twitter_oauth.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    access_token = resp['oauth_token']
    access_secret = resp['oauth_token_secret']
    user = User(access_token, access_secret)
    session['user'] = user

    # revisit this later, let's hardcode for now
    #return redirect(next_url)
    return redirect(url_for('follow'))

#----------------------------------------
# forms
#----------------------------------------

class BatchForm(Form):
    batches = SelectMultipleField(
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
        choices=[(batch.id, batch.name) for batch in db.session.query(Batch).all()])

class HSLoginForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required()
    ])

#----------------------------------------
# controllers
#----------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if session.has_key('hs_auth') and session.has_key('user') :
        return redirect(url_for('follow'))

    form = HSLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        # auth with hacker school, if valid set session variable
        email = form.email.data
        password = form.password.data

        response = requests.get("https://www.hackerschool.com/auth",
                            params={"email":email, "password": password})
        if response.status_code == 200:
            session['hs_auth'] = True
            flash('You were logged in to hacker school', 'alert-success')
        elif response.status_code == 401:
            flash('Your hacker school login was incorrect' , 'alert-error')

    return render_template('index.html', form=form)


@app.route('/follow', methods=['GET', 'POST'])
def follow():
    if not 'user' in session:
        return redirect(url_for('login'))

    form = BatchForm()
    if request.method == 'POST':
        follow_from_batch(form.data['batches'])

    return render_template('follow.html', form=form)


def follow_from_batch(batches):
    if batches is None:
        flash('Please select at least one batch', 'alert-error')
        return

    # fetch each twitter id from the selected batches
    db_results = db.session.query(Person.twitter_screen_name).filter(Person.batch_id.in_(batches)).all()
    screen_names = [result.twitter_screen_name for result in db_results]

    try:
        new_following = helpers.follow(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'], session['user'].token, session['user'].secret, screen_names)
        flash('You are now following %s new hacker schoolers!' % new_following, 'alert-info')
    except:
        flash('Something went wrong. Try logging out and back in.', 'alert-error')

@app.route('/logout')
def logout():
    session.clear()
    flash('You were signed out')
    return redirect(url_for('index'))


@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='ico/favicon.ico')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404