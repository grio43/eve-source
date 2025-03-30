#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bookmarks\standaloneBookmarkWnd.py
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.shared.addressBookEntries import PlaceEntry
from eve.client.script.util.bookmarkUtil import IsBookmarkAvailable
import blue
from localization import GetByLabel

class StandaloneBookmarkWnd(Window):
    __notifyevents__ = ['OnRefreshBookmarks', 'OnSessionChanged']
    default_windowID = 'standaloneBookmarkWnd'
    default_isCompact = True
    default_scope = uiconst.SCOPE_INFLIGHT
    default_minSize = (100, 100)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.scroll = Scroll(parent=self.sr.main, id='StandaloneBookmarkWndScroll', pushContent=True)
        self.LoadBookmarkScroll()
        self.UpdateCaption()
        sm.RegisterNotify(self)

    def OnRefreshBookmarks(self):
        self.LoadBookmarkScroll()

    def OnSessionChanged(self, isRemote, session, change):
        if session.solarsystemid2 and 'solarsystemid2' in change:
            self.LoadBookmarkScroll()
        self.UpdateCaption()

    def UpdateCaption(self):
        text = GetByLabel('UI/AclBookmarks/LocationsInSystem', system=cfg.evelocations.Get(session.solarsystemid2).name)
        self.SetCaption(text)

    def LoadBookmarkScroll(self):
        if not session.solarsystemid2:
            return
        bookmarkSvc = sm.GetService('bookmarkSvc')
        bookmarks = bookmarkSvc.GetBookmarksForLocationID(session.solarsystemid2)
        now = blue.os.GetWallclockTime()
        headers = [GetByLabel('UI/PeopleAndPlaces/Label'), GetByLabel('UI/AclBookmarks/FolderHeader'), GetByLabel('UI/AclBookmarks/Expiry')]
        entries = []
        labelSortText = 'sort_%s' % GetByLabel('UI/PeopleAndPlaces/Label')
        folderSortText = 'sort_%s' % GetByLabel('UI/AclBookmarks/FolderHeader')
        expirySortText = 'sort_%s' % GetByLabel('UI/AclBookmarks/Expiry')
        for bookmark in bookmarks:
            if not bookmark:
                continue
            if bookmark.locationID != session.solarsystemid2:
                continue
            if not IsBookmarkAvailable(bookmark.creatorID, bookmark.created, now):
                continue
            hint, comment = bookmarkSvc.UnzipMemo(bookmark.memo)
            expiry = FmtDate(bookmark.expiry, 'ls') if bookmark.expiry else '-'
            creatorID = getattr(bookmark, 'creatorID', None)
            isBookmarkAvailable = IsBookmarkAvailable(creatorID, bookmark.created, now)
            folderNames, isPersonal = bookmarkSvc.GetFolderNamesAndType(bookmark.folderID, bookmark.subfolderID)
            folderText = ' / '.join(folderNames)
            hintForBookmark = hint
            if getattr(bookmark, 'note', None):
                truncatedNote = bookmark.note[:50] + '...' if len(bookmark.note) > 50 else bookmark.note
                hintForBookmark += '<br>- %s' % truncatedNote
            entry = GetFromClass(PlaceEntry, {'bm': bookmark,
             'itemID': bookmark.bookmarkID,
             'tabs': [],
             'hint': hintForBookmark,
             'comment': comment,
             'label': '<t>'.join((unicode(x) for x in (hint, folderText, expiry))),
             'isGroupPersonal': isPersonal,
             'isBookmarkAvailable': isBookmarkAvailable,
             labelSortText: hint.lower(),
             folderSortText: [ x.lower() for x in folderNames ],
             expirySortText: expiry})
            entries.append(entry)

        noContentHint = GetByLabel('UI/AclBookmarks/NoLocalSavedLocation')
        self.scroll.Load(contentList=entries, headers=headers, noContentHint=noContentHint)
