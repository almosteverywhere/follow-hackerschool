from flask import Flask, request, redirect, url_for, session, flash, render_template, g
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import widgets, Form, SelectMultipleField
from wtforms import TextField, validators, PasswordField, BooleanField
from flask.ext.oauth import OAuth
from database.database import db_session
from database.models import User, Batch, Person
from hackt.config import Config
import tasks
import requests

#----------------------------------------
# initialization
#----------------------------------------
app = Flask(__name__)
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
                                 consumer_key=Config.CONSUMER_KEY,
                                 consumer_secret=Config.CONSUMER_SECRET)


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

    session['token'] = resp['oauth_token']
    session['secret'] = resp['oauth_token_secret']

    # revisit this later, let's hardcode for now
    #return redirect(next_url)
    return redirect(url_for('follow'))


@app.before_request
def make_user():
    g.user = None
    if 'token' in session and 'secret' in session:
        g.user = User(session['token'], session['secret'])

#----------------------------------------
# forms
#----------------------------------------

class BatchForm(Form):
    should_tweet = BooleanField(label='Yes! Tell your friends', default='y')
    batches = SelectMultipleField(
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
        choices=[(batch.id, batch.name) for batch in Batch.query.all()])


class HSLoginForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [validators.Required()])

#----------------------------------------
# controllers
#----------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if session.has_key('hs_auth') and g.user is not None:
        return redirect(url_for('follow'))

    form = HSLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if authenticate_hackerschool(email, password):
            session['hs_auth'] = True
        else:
            flash('Your hacker school login was incorrect', 'alert-error')

    return render_template('index.html', form=form)


def authenticate_hackerschool(email, password):
    response = requests.get("https://www.hackerschool.com/auth",
                            params={"email": email, "password": password})
    return response.status_code == 200


@app.route('/follow', methods=['GET', 'POST'])
def follow():
    if g.user is None:
        return redirect(url_for('login'))

    form = BatchForm()
    if request.method == 'POST':
        batches = (form.data['batches'])
        if not batches:
            flash('Please select at least one batch', 'alert-error')
        else:
            if form.data['should_tweet']:
                tasks.tweet.delay(g.user)

            people = Person.people_in_batches(batches)
            tasks.follow.delay(g.user, people)
            flash('Great! Check your Twitter following page in a few minutes to find %s new people.' % len(people),
                  'alert-success')

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