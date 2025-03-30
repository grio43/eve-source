#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\technologyViewsTracker.py
from charactercreator.client.empireSelectionData import GetTechnologyData
from collections import defaultdict

class TechnologyViewsTracker(object):

    def __init__(self):
        self.tech_views_matrix = defaultdict(lambda : defaultdict(lambda : False))
        self.is_tech_switch_discovered = False
        technologies = GetTechnologyData()
        self.number_of_technologies = technologies.GetNumberOfTechs()

    def has_seen_all_technologies(self, race_id):
        for technology in xrange(1, self.number_of_technologies + 1):
            has_seen_technology = self.tech_views_matrix[race_id][technology]
            if not has_seen_technology:
                return False

        return True

    def has_seen_more_than_one_technology(self, race_id):
        number_of_techs_seen = 0
        for technology in xrange(1, self.number_of_technologies + 1):
            has_seen_technology = self.tech_views_matrix[race_id][technology]
            if has_seen_technology:
                number_of_techs_seen += 1

        return number_of_techs_seen > 1

    def has_discovered_technology_switch(self):
        return self.is_tech_switch_discovered

    def mark_technology_as_viewed(self, race_id, technology):
        self.tech_views_matrix[race_id][technology] = True

    def mark_technology_switch_as_discovered(self):
        self.is_tech_switch_discovered = True
