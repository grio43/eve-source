#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\service\mmosservicestub.py
import random
from projectdiscovery.client.projects.exoplanets.exoplanetssampleloader import ExoPlanetsSampleLoader
from projectdiscovery.client.projects.exoplanets.selection.transitselection import TransitSelection
from projectdiscovery.common.projects.exoplanets.parser import ExoPlanetsDataParser

class MMOSServiceStub(object):

    def __init__(self):
        self._loader = ExoPlanetsSampleLoader('../../packages/projectdiscovery/client/projects/exoplanets/sampledata', ExoPlanetsDataParser())
        self._task = None

    def new_task(self):
        names = ['UBhaQdJ6djfU66feJjzEZCc8OV8zIgyF.tab',
         'CiFbgfHTei94gnBtgO3WFw0tTC3AUgn6.tab',
         'ktwUJ8ZiqVjKTzCW1tguamCcsa6eYX4U.tab',
         'trappist_1.tab',
         's2qMiW0T85XoxyGtuDQ2F7BFXS1gPXLx.tab',
         'NrL96LGL5gKqLucekdJKvlEa5AbFTaYd.tab']
        index = random.randrange(0, len(names))
        self._task = self._loader.load_sample_via_name(names[index])
        return self._task.data

    def get_solution(self):
        solution_dictionary = self._task.solution if self._task else None
        if solution_dictionary:
            return solution_dictionary
        return []
