#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveicon\icon_data.py
import os
if False:
    from typing import Iterable
ICON_LIBRARY_ROOT = 'res:/UI/Texture/eveicon'

def is_icon_in_library(icon):
    if isinstance(icon, IconData):
        return True
    elif isinstance(icon, (str, unicode)):
        root_normalized = os.path.normpath(ICON_LIBRARY_ROOT)
        try:
            path_normalized = os.path.normpath(icon)
        except Exception:
            return False

        return path_normalized.startswith(root_normalized)
    else:
        return False


class IconData(object):

    def __init__(self, icon_id, name, group_id, group, sizes, tags):
        self._icon_id = icon_id
        self._name = name
        self._group_id = group_id
        self._group = group
        self._sizes = tuple(sorted(sizes))
        self._tags = frozenset(tags)
        if len(self._sizes) == 0:
            raise ValueError('Icons must have at least one available size')

    @property
    def icon_id(self):
        return self._icon_id

    @property
    def name(self):
        return self._name

    @property
    def group_id(self):
        return self._group_id

    @property
    def group(self):
        return self._group

    @property
    def sizes(self):
        return self._sizes

    @property
    def tags(self):
        return self._tags

    def resolve(self, size):
        desired_size = int(round(size))
        best_available_size = None
        for size in self._sizes:
            best_available_size = size
            if size >= desired_size:
                break

        if best_available_size is None:
            raise RuntimeError('Failed to resolve {} for size {}'.format(self._icon_id, desired_size))
        return self._format_res_path(best_available_size)

    def _format_res_path(self, size):
        return '{root}/{group}/{id}_{size}px.png'.format(root=ICON_LIBRARY_ROOT, group=self._group_id, id=self._icon_id, size=size)

    def __eq__(self, other):
        return self is other or isinstance(other, IconData) and self._icon_id == other._icon_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._icon_id)
