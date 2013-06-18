import os
from flask import Flask, request, redirect, url_for, session, flash, g, \
    render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import widgets, Form, SelectMultipleField, HiddenField
from wtforms import ValidationError, TextField, validators, PasswordField, BooleanField
from wtforms.widgets import CheckboxInput
from flask.ext.oauth import OAuth
from database import db_session
from models import Base, User, Batch, Person
import requests
import helpers

#----------------------------------------
# initialization
#----------------------------------------

app = Flask(__name__)
app.config.from_object('app.settings.Config')
Bootstrap(app)

#----------------------------------------
# database
#----------------------------------------
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

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
    should_tweet = BooleanField(label='Yes! Tell the world.', default='y')
    batches = SelectMultipleField(
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
        choices=[(batch.id, batch.name) for batch in Batch.query.all()])

class HSLoginForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
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

        if helpers.authenticate_hackerschool(email, password):
            session['hs_auth'] = True
        else:
            flash('Your hacker school login was incorrect' , 'alert-error')

    return render_template('index.html', form=form)


@app.route('/follow', methods=['GET', 'POST'])
def follow():
    if not 'user' in session:
        return redirect(url_for('login'))

    form = BatchForm()
    if request.method == 'POST':
        batches = (form.data['batches'])
        if batches is None:
            flash('Please select at least one batch', 'alert-error')
        else:
            people = Person.people_in_batches(batches)

            try:
                followed, not_followed = helpers.follow(session['user'], people)

                if followed:
                    flash('You are now following %s new hacker schoolers!' % len(followed), 'alert-info')
                if not_followed:
                    flash('These was an error following some hacker schoolers. %s people not followed.' % len(not_followed), 'alert-error')

            except ValueError:
                flash('The twitter user is not properly authenticated. Please login again.', 'alert-error')
                return redirect(url_for('login'))

    return render_template('follow.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You were signed out')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='ico/favicon.ico')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404