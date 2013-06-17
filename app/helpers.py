import twitter
import requests
from models import *
from settings import Config

def follow(user, people):
    """
    user is of type models.User
    screen_names is a list of twitter screen names to follow
    """
    api = twitter.Api(
        consumer_key=Config.CONSUMER_KEY,
        consumer_secret=Config.CONSUMER_SECRET,
        access_token_key=user.token,
        access_token_secret=user.secret
    )

    twitter_user = api.VerifyCredentials()
    if twitter_user is None:
        raise Exception('Invalid twitter authentication for user.')

    # don't let a user follow themselves
    screen_names = [person.twitter_screen_name for person in people]
    if twitter_user.GetScreenName in screen_names: screen_names.remove(twitter_user.GetScreenName)

    followed = []
    not_followed = []

    for screen_name in screen_names:
        try:
            friendship = api.CreateFriendship(screen_name=screen_name)
            if friendship is not None:
                followed.append(screen_name)
        except twitter.TwitterError:
            not_followed.append(screen_name)

    return followed, not_followed

def authenticate_hackerschool(email, password):
    response = requests.get("https://www.hackerschool.com/auth",
                            params={"email":email, "password": password})

    return response.status_code == 200

# def tweet():
#     if not 'user' in session:
#         return redirect(url_for('login', next=request.url))
#
#     status = request.form['tweet']
#     if not status:
#         return redirect(url_for('index'))
#
#     resp = twitter.post('statuses/update.json', data={
#         'status': status
#     })
#     if resp.status == 403:
#         flash('Your tweet was too long.')
#     elif resp.status == 401:
#         flash('Authorization error with Twitter.')
#     else:
#         flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
#     return redirect(url_for('index'))

