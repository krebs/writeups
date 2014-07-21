#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Krebsminister'
SITENAME = 'Krebs CTF Writeups'
SITEURL = 'http://krebsco.de'
#SITESUBTITLE = 'A collection of pseudocode snippets'

TIMEZONE = 'Europe/Berlin'
THEME = './gum/'
DEFAULT_LANG = 'en'
#DEFAULT_CATEGORY = 'misc'
# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
STATIC_PATHS = ['extra/robots.txt','data' ]
EXTRA_PATH_METADATA = { 'extra/robots.txt': {'path': 'robots.txt'}, }

# Blogroll
LINKS =  ( ( 'Hosts Files', 'http://krebsco.de/retiolum/hosts.tar.gz'),
( 'Supernodes File', 'http://euer.krebsco.de/retiolum/supernodes.tar.gz'),
( 'Retiolum Graphs', 'http://pigstarter.krebsco.de/graphs/retiolum'),
        ('makefu\'s Blog', 'http://euer.krebsco.de'),)

# Social widget
SOCIAL = (('@krebsbob', 'http://twitter.com/krebsbob'),
        ('irc.freenode.net#krebs','irc://irc.freenode.net#krebs'))
DEFAULT_PAGINATION = 10

# DISQUS_SITENAME = ''
#GOOGLE_ANALYTICS = ""
# PIWIK_URL='mediengewitter.krebsco.de:10000'
# PIWIK_SITE_ID=1

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
MENUITEMS = ( ( 'RSS', '/atom.xml',),)
