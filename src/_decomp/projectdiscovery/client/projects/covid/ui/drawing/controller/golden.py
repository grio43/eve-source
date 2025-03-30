#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\golden.py
from projectdiscovery.client.projects.covid.ui.drawing.controller import update
from projectdiscovery.client.projects.covid.ui.drawing import models

class GoldenController(object):

    def __init__(self):
        self.polygons = []
        self.updater = update.UpdateController()

    def add_polygon(self, verticies):
        self.polygons.append(models.Polygon([ models.Coord(v[0], v[1]) for v in verticies ]))
        self.updater.tick()
        self.updater.report_update()

    def clear(self):
        self.polygons = []
        self.updater.tick()
        self.updater.report_update()

    def scale(self, ratio):
        for p in self.polygons:
            p.scale(ratio)

        self.updater.tick()
        self.updater.report_update()
