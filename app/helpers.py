import twitter

def follow(consumer_key, consumer_secret, token, secret, args):
    api = twitter.Api(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=token,
        access_token_secret=secret
    )

    user = api.VerifyCredentials()
    if not (token, secret, args, user):
        raise Exception('Arguments are missing or token and secret are not valid')

    # don't let a user follow themselves
    args.remove(user.GetScreenName)

    following = 0
    for screen_name in args:
        try:
            followed = api.CreateFriendship(screen_name=screen_name)
            if followed is not None:
                following += 1
        except twitter.TwitterError as error:
            # todo beef up the error handling
            print ('An error occurred: %s' % error.message)

    return following


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

