#!/usr/bin/env python
#

import os

from google.appengine.dist import use_library
use_library('django', '1.2')
from django.conf import settings
try:
    settings.configure(INSTALLED_APPS=('stub',))
except Exception, e:
    pass


from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util

from controllers.main_controller import MainHandler, ContactHandler, ThanksHandler, SearchHandler, PageNotFoundHandler

from controllers.event_controller import EventList, EventDetail, EventRss
from controllers.match_controller import MatchList, MatchDetail
from controllers.team_controller import TeamList, TeamDetail



def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/contact', ContactHandler),
                                          ('/events', EventList),
                                          ('/event/(.*)/feed', EventRss),
                                          ('/events/(.*)', EventList),
                                          ('/event/(.*)', EventDetail),
                                          ('/match/list', MatchList),
                                          ('/match/(.*)', MatchDetail),
                                          ('/search', SearchHandler),
                                          ('/teams', TeamList),
                                          ('/team/([0-9]*)', TeamDetail),
                                          ('/team/([0-9]*)/(.*)', TeamDetail),
                                          ('/thanks', ThanksHandler),
                                          ('/.*', PageNotFoundHandler)
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
