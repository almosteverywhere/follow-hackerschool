from __future__ import absolute_import
import requests
import pyquery as pq
import sys
from app import db
from app.models import *
import getpass

# Quick and dirty scraper for hacker school batch info.
# Borrowed heavily from https://github.com/einashaddad/follow

host = 'https://www.hackerschool.com'

def init_db():
    db.create_all()

def scrape_hs(hs_email, hs_password, host):
    """
    Returns a response object after creating an authenticated session with
    hackerschool
    """
    session = requests.session()

    #retrieving the csrf-token from the html
    page = pq.PyQuery(url = host+'/login')
    meta_content = page('meta')

    for m in pq.PyQuery(meta_content):
        if pq.PyQuery(m).attr('name') == 'csrf-token':
            csrf_token = pq.PyQuery(m).attr('content')

    payload = {
        'authenticity_token': csrf_token,
        'email': hs_email,
        'password': hs_password,
        'commit': 'Log In',
    }

    request = session.post(host+'/sessions', data=payload, verify=False)
    resp = session.get(host+'/private')

    return resp

def populate_database(resp):
    """
    Returns a dictionary of people to follow with their twitter usernames as values
    """
    content = resp.text
    content = pq.PyQuery(content)

    if not content('#batches'):
        print "Incorrect hacker-school username and/or password"
        sys.exit()

    # parse batch names first, since they're not part of each
    # batch element
    batch_root = content('#batches')
    batch_names = batch_root('h2')
    i = 1
    for name in reversed(batch_names):
        #batch 6 is missing from the website. mystery!
        if i == 6:
            i += 1

        batch = Batch(name.text_content().strip())
        db.session.add(batch)

        people = content('#batch%s .person' % i)

        for person in people:
            person = pq.PyQuery(person)
            person_class = person('div.name')
            icon_links = person('div.icon-links')

            for icon_link in icon_links:
                icon_link = pq.PyQuery(icon_link)
                anchors = icon_link('a')
                for anchor in anchors:
                    anchor = pq.PyQuery(anchor)
                    link = anchor.attr('href')
                    if 'twitter' in link:
                        twitter_username = link[20:]
                        person = Person(person_class.text(), twitter_username)
                        person.batch = batch
                        db.session.add(person)

        db.session.commit()
        i+=1

if __name__ == '__main__':
    host = 'https://www.hackerschool.com'

    hs_email =  raw_input("Hacker-School username: ")
    hs_password = getpass.getpass(prompt='Hacker-School password: ')

    response = scrape_hs(hs_email, hs_password, host)
    populate_database(response)