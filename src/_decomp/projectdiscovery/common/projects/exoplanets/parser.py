#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\common\projects\exoplanets\parser.py
import re

class ExoPlanetsDataParser:

    def __init__(self):
        pass

    def parse(self, string_data):
        split_data = string_data.splitlines()[1:]
        return [ (float(point[0]), float(point[1])) for point in [ re.split('\\s+', data_point) for data_point in split_data ] ]
