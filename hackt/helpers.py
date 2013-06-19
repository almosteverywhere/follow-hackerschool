import twitter
import requests
from hackt.config import Config

def get_api(user):
    api = twitter.Api(
        consumer_key=Config.CONSUMER_KEY,
        consumer_secret=Config.CONSUMER_SECRET,
        access_token_key=user.token,
        access_token_secret=user.secret
    )

    twitter_user = api.VerifyCredentials()
    if twitter_user is None:
        raise ValueError('Invalid twitter authentication for user.')

    return api


def follow(user, people):
    """
    user is of type models.User
    screen_names is a list of twitter screen names to follow

    Ideally, this task should run in a background process or worker,
    but those features are not supported by a free heroku instance
    """
    api = get_api(user)
    current_screen_name = api.VerifyCredentials().GetScreenName()

    # don't let a user follow themselves
    screen_names = [person.twitter_screen_name for person in people]
    if current_screen_name in screen_names: screen_names.remove(current_screen_name)

    followed = []
    not_followed = []

    for screen_name in screen_names:
        try:
            api.CreateFriendship(screen_name=screen_name)
            followed.append(screen_name)
        except twitter.TwitterError:
            not_followed.append(screen_name)

    return followed, not_followed


def tweet(user):
    api = get_api(user)
    msg = 'I used hackt to follow @hackerschool batches on twitter. You can too at http://bit.ly/try_hackt'

    try:
        api.PostUpdate(msg)
    except twitter.TwitterError as error:
        return {'msg': error.message[0]['message']}


def authenticate_hackerschool(email, password):
    response = requests.get("https://www.hackerschool.com/auth",
                            params={"email": email, "password": password})

    return response.status_code == 200