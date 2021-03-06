import logging

from google.appengine.ext import db

from models import Match, Team

class MatchHelper(object):
    """
    Helper to put matches into sub-dictionaries for the way we render match tables
    """
    @classmethod
    def organizeMatches(self, match_list):
        match_list = match_list.order("set_number").order("match_number").fetch(500)
        
        # Eh, this could be better. -gregmarra 17 oct 2010
        # todo: abstract this so we can use it in the team view.
        # todo: figure out how slow this is
        [match.unpack_json() for match in match_list]
        
        # Cleanup invalid. This does database calls. This is a wildly inappropriate place
        # to be doing this. -gregmarra
        match_list = filter(None, [MatchHelper.cleanUpIfInvalidMatch(match) for match in match_list])
        
        matches = dict([(comp_level, list()) for comp_level in Match.COMP_LEVELS])
        matches["num"] = len(match_list)
        while len(match_list) > 0:
            match = match_list.pop(0)
            matches[match.comp_level].append(match)
        
        return matches
    
    @classmethod
    def cleanUpIfInvalidMatch(self, match):
        invalid = MatchHelper.isIncompleteElim(match)
        if invalid:
            #MatchUpdater.delete(match)
            logging.warning("Deleting invalid match: %s" % match.key().name())
            return None
        else:
            return match
    
    @classmethod
    def isIncompleteElim(self, match):
        if match.comp_level not in set(["ef", "qf", "sf", "f"]):
            return False
        
        for alliance in match.alliances:
            if match.alliances[alliance]["score"] > -1:
                return False
        
        # No alliances had non-zero scores
        return True

class MatchUpdater(object):
    """
    Helper class to handle Match objects when we are not sure whether they
    already exist or not.
    """
    @classmethod
    def createOrUpdate(self, new_match):
        """
        Get a handle on a Match, then write it down.
        """
        new_match = self.findOrSpawn(new_match)
        new_match.put()
        return new_match
    
    @classmethod
    def findOrSpawn(self, new_match):
        """
        Check whether a match already exists. 
        If it does, update the data, and send it back.
        If it doesn't, send it back.
        """
        match = Match.get_by_key_name(new_match.get_key_name())
        if match is not None:
            new_match = self.updateMerge(new_match, match)
        
        return new_match
    
    @classmethod
    def updateMerge(self, new_match, old_match):
        """
        Merges the information in a new match object with the existing object
        representing that match.
        """
        #FIXME: There must be a way to do this elegantly. -greg 5/12/2010
        
        if new_match.time is not None:
            old_match.time = new_match.time
        if new_match.game is not None:
            old_match.game = new_match.game
        if new_match.comp_level is not None:
            old_match.comp_level = new_match.comp_level
        if new_match.set_number is not None:
            old_match.set_number = new_match.set_number
        if new_match.team_key_names is not None:
            old_match.team_key_names = new_match.team_key_names
        if new_match.alliances_json is not None:
            old_match.alliances_json = new_match.alliances_json
        
        return old_match