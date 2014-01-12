"""
Wiki things.
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoBagError, NoTiddlerError
from tiddlyweb.web.util import get_route_value
from tiddlyweb.wikitext import render_wikitext

from tiddlywebplugins.templates import get_template

WIKI_TEMPLATE = 'wiki.html'


def private_policy(username):
    return Policy(owner=username,
            read=[username],
            write=[username],
            create=[username],
            delete=[username],
            manage=[username],
            accept=['NONE'])


def protected_policy(username):
    return Policy(owner=username,
            read=[],
            write=[username],
            create=[username],
            delete=[username],
            manage=[username],
            accept=['NONE'])


def public_policy(username):
    return Policy(owner=username,
            read=[],
            write=[],
            create=[],
            delete=[],
            manage=[username],
            accept=['NONE'])


WIKI_MODES = {
    'private': private_policy,
    'protected': protected_policy,
    'public': public_policy,
}



def create_wiki(environ, name, mode='private', username=None):
    """
    Create a wiki with the name, name.

    For now a wiki is just a bag a policy.
    """
    store = environ['tiddlyweb.store']
    if username is None:
        username = environ['tiddlyweb.usersign']['name']

    bag = Bag(name)

    # We want this get to fail.
    try:
        store.get(bag)
        return False
    except NoBagError:
        pass

    try:
        bag.policy = WIKI_MODES[mode](username)
    except KeyError:
        bag.policy = WIKI_MODES['private'](username)
    store.put(bag)

    return bag


def wiki_page(environ, start_response):
    """
    Present a single tiddler from a given tank.
    """
    tank_name = get_route_value(environ, 'bag_name')
    try:
        tiddler_name = get_route_value(environ, 'tiddler')
    except KeyError:
        tiddler_name = 'index'

    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']

    try:
        bag = store.get(Bag(tank_name))
    except NoBagError:
        raise HTTP404('no tank found for %s' % tank_name)

    # let permissions problems raise
    bag.policy.allows(usersign, 'read')

    try:
        tiddler = Tiddler(tiddler_name, tank_name)
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        tiddler.type = 'text/x-markdown'
        tiddler.text = '## This tiddler does not yet exist\n'

    if tiddler.type == 'text/x-markdown':
        html = render_wikitext(tiddler, environ)
        wiki_template = get_template(environ, WIKI_TEMPLATE)
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=UTF-8'),
            ('Cache-Control', 'no-cache')])
        return wiki_template.generate({
            'user': usersign['name'],
            'tiddler': tiddler,
            'html': html,
            'bag': bag,
        })
    else:
        return tiddler_get(environ, start_response)

