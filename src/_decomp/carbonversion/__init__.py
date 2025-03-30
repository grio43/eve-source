#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonversion\__init__.py
import logging
import os
import re
import blue
import json
VERSION_PATTERN = 'v(\\d+\\.\\d+\\.\\d+)'
LOGGER = logging.getLogger(__name__)

def get_carbon_version(file_name = 'carbon.json'):
    if not blue.pyos.packaged:
        root = blue.paths.ResolvePath(u'root:/..')
    else:
        root = blue.paths.ResolvePath(u'root:/')
    return CarbonVersion(blue.paths.ResolvePath(u'{}/{}'.format(root, file_name)))


class CarbonVersion:

    def __init__(self, file_name):
        self._libraries = {}
        self._version = '0.0.0'
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                self.data = json.load(f)
            self._version = self.data['version']
            for lib_name, path in self.data['libraries'].items():
                path = path.strip()
                if lib_name == 'version':
                    self._version = path.strip()
                elif path.startswith('github.com'):
                    version = path.strip().split('/')[-1]
                    self._libraries[lib_name] = version

    def get_version(self):
        return self._version

    def get_library_version(self, library):
        tag = self._libraries.get(library)
        if tag is None:
            return ''
        else:
            match = re.search(VERSION_PATTERN, tag)
            if match:
                return match.group(0)
            return ''

    def get_library_tag(self, library):
        return self._libraries.get(library)

    def get_libraries(self):
        return self._libraries.keys()

    def get_json_data(self):
        return self.data
