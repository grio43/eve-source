#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\scroll_const.py


class SortDirection(object):
    ASCENDING = 1
    DESCENDING = -1

    @staticmethod
    def flip(direction):
        if direction == SortDirection.ASCENDING:
            return SortDirection.DESCENDING
        if direction == SortDirection.DESCENDING:
            return SortDirection.ASCENDING
        raise ValueError('Unknown sort direction')

    @staticmethod
    def from_legacy_reversed_sort(reversed_sort):
        if reversed_sort:
            return SortDirection.DESCENDING
        else:
            return SortDirection.ASCENDING


def GetHiddenColumnsKey(scrollID):
    try:
        if not scrollID:
            return scrollID
        if not isinstance(scrollID, basestring):
            return scrollID
        parts = scrollID.split('__')
        return parts[0]
    except StandardError:
        import log
        log.LogException('Failed to get hidden columns key')
        return scrollID
