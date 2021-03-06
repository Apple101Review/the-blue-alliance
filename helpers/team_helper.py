import re
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import db

from models import Team

class TeamHelper(object):
    """
    Helper to sort teams and stuff
    """
    @classmethod
    def sortTeams(self, team_list):
        """
        Takes a list of Teams (not a Query object).
        """
        # Sometimes there are None objects in the list.
        team_list = filter(None, team_list)
        team_list = sorted(team_list, key=lambda team: team.team_number)
        
        return team_list

class TeamTpidHelper(object):
    
    # Separates tpids on the FIRST list of all teams.
    teamRe = re.compile(r'tpid=[A-Za-z0-9=&;\-:]*?"><b>\d+')
    # Extracts the team number from the team result.
    teamNumberRe = re.compile(r'\d+$')
    # Extracts the tpid from the team result.
    tpidRe = re.compile(r'\d+')
    # Extracts the link to the next page of results on the FIRST list of all teams.
    lastPageRe = re.compile(r'Next ->')
    
    @classmethod
    def scrapeTpid(self, number, skip=0, year=2011):
      """
      Searches the FIRST list of all teams for the requested team's tpid, caching
      all it encounters in the datastore. This has the side effect of creating Team
      objects along the way.
      
      This code is taken directly from Pat Fairbank's frclinks source and modified
      slightly to fit in the TBA framework. He has given us permission to borrow
      his code directly.
      """
      teams_to_put = list()
      while 1:
        logging.info("Fetching 250 teams based on %s data, skipping %s" % (year, skip))
        # TODO: Make this robust to season changes. -gregmarra 9 Jan 2011
        teamList = urlfetch.fetch(
            'https://my.usfirst.org/myarea/index.lasso?page=searchresults&' +
            'programs=FRC&reports=teams&sort_teams=number&results_size=250&' +
            'omit_searchform=1&season_FRC=%s&skip_teams=%s' % (year, skip),
            deadline=10)
        teamResults = self.teamRe.findall(teamList.content)
        tpid = None
        
        for teamResult in teamResults:
          teamNumber = self.teamNumberRe.findall(teamResult)[0]
          teamTpid = self.tpidRe.findall(teamResult)[0]
          if teamNumber == number:
            tpid = teamTpid
          
          logging.info("Team %s TPID was %s in year %s." % (teamNumber, teamTpid, year))
          
          team = Team.get_by_key_name('frc' + str(teamNumber))
          new_team = Team(
            team_number = int(teamNumber),
            first_tpid = int(teamTpid),
            first_tpid_year = int(year),
            key_name = "frc" + str(teamNumber)
          )
          if team is None:
            teams_to_put.append(new_team)
          else:
            team = TeamUpdater.updateMerge(new_team, team)
            teams_to_put.append(team)
        
        skip = int(skip) + 250
        db.put(teams_to_put)
        teams_to_put = list()
        
        if tpid:
          return tpid
        
        if len(self.lastPageRe.findall(teamList.content)) == 0:
          return None


class TeamUpdater(object):
    """
    Helper class to handle Team objects when we are not sure whether they
    already exist or not.
    """

    @classmethod
    def createOrUpdate(self, new_team):
        """
        Check if a team currently exists in the database based on team_number
        If it does, update the team.
        If it does not, create the team.
        """
        query = Team.all()

        # First, do the easy thing and look for an eid collision. 
        # This will only work on USFIRST teams.
        query.filter('team_number =', new_team.team_number)

        if query.count() > 0:
            old_team = query.get()
            new_team = self.updateMerge(new_team, old_team)

        new_team.put()
        return new_team

    @classmethod
    def updateMerge(self, new_team, old_team):
        """
        Given an "old" and a "new" Team object, replace the fields in the
        "old" team that are present in the "new" team, but keep fields from
        the "old" team that are null in the "new" team.
        """
        #FIXME: There must be a way to do this elegantly. -greg 5/12/2010

        if new_team.name is not None:
            old_team.name = new_team.name
        if new_team.nickname is not None:
            old_team.nickname = new_team.nickname
        if new_team.website is not None:
            old_team.website = new_team.website
        if new_team.address is not None:
            old_team.address = new_team.address
        
        # Take the new tpid and tpid_year iff the year is newer than the old one
        if (new_team.first_tpid_year > old_team.first_tpid_year):
            old_team.first_tpid_year = new_team.first_tpid_year
            old_team.first_tpid = new_team.first_tpid
        
        return old_team