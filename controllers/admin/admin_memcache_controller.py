import os

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util

from models import Team

# The view of a list of teams.
class AdminMemcacheMain(webapp.RequestHandler):
    def get(self):
        
        template_values = {
            "memcache_stats": memcache.get_stats(),
        }
        
        path = os.path.join(os.path.dirname(__file__), '../../templates/admin/memcache/index.html')
        self.response.out.write(template.render(path, template_values))
        
# The view of a single Team.
class AdminMemcacheFlush(webapp.RequestHandler):
    def get(self):
        flushed = list()
        
        if self.request.get('all') == "true":
            memcache.flush_all()
            flushed.append("all memcache values")
        
        template_values = { 
            'flushed' : flushed,
        }
        
        path = os.path.join(os.path.dirname(__file__), '../../templates/admin/memcache/flush.html')
        self.response.out.write(template.render(path, template_values))

