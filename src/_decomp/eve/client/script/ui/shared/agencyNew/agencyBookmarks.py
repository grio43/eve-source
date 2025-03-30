#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\agencyBookmarks.py
from eve.client.script.ui.shared.agencyNew import agencySignals, agencyEventLog
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupProvider import IsContentGroupValid
_bookmarks = None
MAX_NUM_BOOKMARKS = 6

def _CheckInitBookmarks():
    global _bookmarks
    if _bookmarks is None:
        _bookmarks = settings.char.ui.Get('agencyBookmarks', [])
        _bookmarks = [ contentGroupID for contentGroupID in _bookmarks if IsContentGroupValid(contentGroupID) ]


def ClearBookmarksVariable():
    global _bookmarks
    _bookmarks = None


def AddBookmark(contentGroupID, index = None):
    _CheckInitBookmarks()
    if len(_bookmarks) >= MAX_NUM_BOOKMARKS:
        return
    if contentGroupID in _bookmarks:
        _bookmarks.remove(contentGroupID)
    if index:
        _bookmarks.insert(index, contentGroupID)
    else:
        _bookmarks.append(contentGroupID)
    _PersistBookmarks()
    agencySignals.on_bookmarks_changed(_bookmarks[:])
    agencyEventLog.LogEventBookmarkAdded(contentGroupID)


def RemoveBookmark(contentGroupID):
    _CheckInitBookmarks()
    if contentGroupID in _bookmarks:
        _bookmarks.remove(contentGroupID)
    _PersistBookmarks()
    agencySignals.on_bookmarks_changed(_bookmarks[:])


def _PersistBookmarks():
    settings.char.ui.Set('agencyBookmarks', _bookmarks)


def GetBookmarks():
    _CheckInitBookmarks()
    return _bookmarks[:]
