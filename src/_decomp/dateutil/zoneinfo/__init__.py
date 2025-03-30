#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dateutil\zoneinfo\__init__.py
import logging
import os
import warnings
import tempfile
import shutil
import json
from tarfile import TarFile
from pkgutil import get_data
from io import BytesIO
from contextlib import closing
from dateutil.tz import tzfile
__all__ = ['get_zonefile_instance',
 'gettz',
 'gettz_db_metadata',
 'rebuild']
ZONEFILENAME = 'dateutil-zoneinfo.tar.gz'
METADATA_FN = 'METADATA'
tar_open = TarFile.open
if not hasattr(TarFile, '__exit__'):

    def tar_open(*args, **kwargs):
        return closing(TarFile.open(*args, **kwargs))


class tzfile(tzfile):

    def __reduce__(self):
        return (gettz, (self._filename,))


def getzoneinfofile_stream():
    try:
        return BytesIO(get_data(__name__, ZONEFILENAME))
    except IOError as e:
        warnings.warn('I/O error({0}): {1}'.format(e.errno, e.strerror))
        return None


class ZoneInfoFile(object):

    def __init__(self, zonefile_stream = None):
        if zonefile_stream is not None:
            with tar_open(fileobj=zonefile_stream, mode='r') as tf:
                self.zones = dict(((zf.name, tzfile(tf.extractfile(zf), filename=zf.name)) for zf in tf.getmembers() if zf.isfile() and zf.name != METADATA_FN))
                links = dict(((zl.name, self.zones[zl.linkname]) for zl in tf.getmembers() if zl.islnk() or zl.issym()))
                self.zones.update(links)
                try:
                    metadata_json = tf.extractfile(tf.getmember(METADATA_FN))
                    metadata_str = metadata_json.read().decode('UTF-8')
                    self.metadata = json.loads(metadata_str)
                except KeyError:
                    self.metadata = None

        else:
            self.zones = dict()
            self.metadata = None

    def get(self, name, default = None):
        return self.zones.get(name, default)


_CLASS_ZONE_INSTANCE = list()

def get_zonefile_instance(new_instance = False):
    if new_instance:
        zif = None
    else:
        zif = getattr(get_zonefile_instance, '_cached_instance', None)
    if zif is None:
        zif = ZoneInfoFile(getzoneinfofile_stream())
        get_zonefile_instance._cached_instance = zif
    return zif


def gettz(name):
    warnings.warn('zoneinfo.gettz() will be removed in future versions, to use the dateutil-provided zoneinfo files, instantiate a ZoneInfoFile object and use ZoneInfoFile.zones.get() instead. See the documentation for details.', DeprecationWarning)
    if len(_CLASS_ZONE_INSTANCE) == 0:
        _CLASS_ZONE_INSTANCE.append(ZoneInfoFile(getzoneinfofile_stream()))
    return _CLASS_ZONE_INSTANCE[0].zones.get(name)


def gettz_db_metadata():
    warnings.warn("zoneinfo.gettz_db_metadata() will be removed in future versions, to use the dateutil-provided zoneinfo files, ZoneInfoFile object and query the 'metadata' attribute instead. See the documentation for details.", DeprecationWarning)
    if len(_CLASS_ZONE_INSTANCE) == 0:
        _CLASS_ZONE_INSTANCE.append(ZoneInfoFile(getzoneinfofile_stream()))
    return _CLASS_ZONE_INSTANCE[0].metadata
