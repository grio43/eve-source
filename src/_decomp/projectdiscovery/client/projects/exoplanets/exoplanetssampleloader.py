#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetssampleloader.py
import os
from os import walk
from projectdiscovery.client.projects.exoplanets.problem import Problem
import random
import blue
import json
try:
    from blue import pyos, paths
except ImportError:
    pyos = None
    paths = None

class ExoPlanetsSampleLoader:
    file_ending = 'tab'

    def __init__(self, sample_directory, exoplanets_data_parser):
        self.parser = exoplanets_data_parser
        self.sample_files = []
        if pyos:
            if pyos.packaged:
                path = paths.ResolvePath(u'bin:/') + 'exoplanets/'
            else:
                path = blue.paths.ResolvePath(sample_directory)
        else:
            path = blue.paths.ResolvePath(sample_directory)
        for dir_path, dir_names, file_names in walk(path):
            for filename in file_names:
                self.sample_files.append(os.path.join(dir_path, filename))

        self.sample_files = [ sample for sample in self.sample_files if sample.endswith(self.file_ending) ]

    def load_sample_via_name(self, sample_name):
        indexes = [ i for i in xrange(len(self.sample_files)) if self.sample_files[i].endswith(sample_name) ]
        index = None if not indexes else indexes[0]
        if index is None:
            return
        return self.load_specific_sample(index)

    def load_specific_sample(self, index_of_file):
        if not self.sample_files:
            return None
        sample_file = open(self.sample_files[index_of_file])
        data = sample_file.read()
        sample_file.close()
        return Problem(self.parser.parse(data), None)
