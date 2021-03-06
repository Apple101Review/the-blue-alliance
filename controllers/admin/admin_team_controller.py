import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util

from models import Team

# The view of a list of teams.
class AdminTeamList(webapp.RequestHandler):
    def get(self):
        
        teams = Team.all().order('team_number').fetch(10000)
        
        template_values = {
            "teams": teams,
        }
        
        path = os.path.join(os.path.dirname(__file__), '../../templates/admin/teams/list.html')
        self.response.out.write(template.render(path, template_values))
        
# The view of a single Team.
class AdminTeamDetail(webapp.RequestHandler):
    def get(self, team_number):
        
        team = Team.get_by_key_name("frc" + team_number)                
        
        template_values = { 
            'team' : team,
        }
        
        path = os.path.join(os.path.dirname(__file__), '../../templates/admin/teams/details.html')
        self.response.out.write(template.render(path, template_values))

