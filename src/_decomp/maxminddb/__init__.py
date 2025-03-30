#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\maxminddb\__init__.py
import os
import maxminddb.reader
try:
    import maxminddb.extension
except ImportError:
    maxminddb.extension = None

from maxminddb.const import MODE_AUTO, MODE_MMAP, MODE_MMAP_EXT, MODE_FILE, MODE_MEMORY
from maxminddb.decoder import InvalidDatabaseError

def open_database(database, mode = MODE_AUTO):
    has_extension = maxminddb.extension and hasattr(maxminddb.extension, 'Reader')
    if mode == MODE_AUTO and has_extension or mode == MODE_MMAP_EXT:
        if not has_extension:
            raise ValueError('MODE_MMAP_EXT requires the maxminddb.extension module to be available')
        return maxminddb.extension.Reader(database)
    if mode in (MODE_AUTO,
     MODE_MMAP,
     MODE_FILE,
     MODE_MEMORY):
        return maxminddb.reader.Reader(database, mode)
    raise ValueError('Unsupported open mode: {0}'.format(mode))


def Reader(database):
    return open_database(database)


__title__ = 'maxminddb'
__version__ = '1.3.0'
__author__ = 'Gregory Oschwald'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2014 Maxmind, Inc.'
