"""
Stubbing in the stubs.
"""

from tiddlyweb.util import merge_config

from tiddlywebplugins.oauth import init as oauth_init
from tiddlywebplugins.utils import replace_handler

from .config import config as tank_config
from .home import home, dash

def establish_web(config):
    oauth_init(config)

    selector = config['selector']
    replace_handler(selector, '/', dict(GET=home))
    selector.add('/dash', GET=dash)

def init(config):
    merge_config(config, tank_config, reconfig=True)
    if 'selector' in config:
        establish_web(config)
