#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\resource\shared\planetary_resources_data.py


class PlanetaryResourcesData(object):

    def __init__(self, power_by_planet, workforce_by_planet, reagent_by_planet, resource_version):
        self.version = resource_version
        self.power_by_planet = power_by_planet
        self.workforce_by_planet = workforce_by_planet
        self.reagent_by_planet = reagent_by_planet

    def __eq__(self, other):
        return self.version == other.version and self.power_by_planet == other.power_by_planet and self.reagent_by_planet == other.reagent_by_planet and self.workforce_by_planet == other.workforce_by_planet
