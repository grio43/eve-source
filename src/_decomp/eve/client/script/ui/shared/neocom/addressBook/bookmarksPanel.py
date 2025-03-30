#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\bookmarksPanel.py
import itertools
import eve.common.lib.appConst as appConst
import blue
import eveicon
import localization
import telemetry
import threadutils
import uthread
from carbonui import TextColor, uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.addressBookEntries import PlaceEntry
from eve.client.script.ui.shared.bookmarks.standaloneBookmarkWnd import StandaloneBookmarkWnd
from menu import MenuLabel
from caching.memoize import Memoize
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util.format import FmtDate
from carbonui.control.scrollentries import SE_GenericCore
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.bookmarks.bookmarkContainerWindow import BookmarkContainerWindow
from eve.client.script.ui.shared.bookmarks.bookmarkSubfolderWindow import BookmarkSubfolderWindow
from eve.client.script.util.bookmarkUtil import IsCoordinateBookmark, IsBookmarkAvailable, ConvertSubfolderName
from inventorycommon.const import ownerSystem
from localization import GetByLabel, GetByMessageID
from localization.util import Sort
from sensorsuite.overlay.bookmarkvisibilitymanager import GetBookmarkFolderVisibilityManager
from eve.client.script.ui.control import eveIcon, eveScroll
from evePathfinder.core import IsUnreachableJumpCount
import evetypes
from carbonui.uicore import uicore
from utillib import KeyVal
import inventorycommon.const as invConst
COLOR_SELECTED = eveColor.LEAFY_GREEN
COLOR_POSTTEXT = Color(*TextColor.SECONDARY).GetHex()
COLOR_WARNING_POSTTEXT = Color(*TextColor.WARNING).GetHex()
MAX_BOOKMARKS_DISPLAYED_IN_GROUP = 3000
placesHeaders = [GetByLabel('UI/PeopleAndPlaces/Label'),
 GetByLabel('UI/Common/Type'),
 GetByLabel('UI/PeopleAndPlaces/Jumps'),
 GetByLabel('UI/PeopleAndPlaces/Sol'),
 GetByLabel('UI/PeopleAndPlaces/Con'),
 GetByLabel('UI/PeopleAndPlaces/Reg'),
 GetByLabel('UI/Common/Date'),
 GetByLabel('UI/AclBookmarks/Expiry'),
 GetByLabel('UI/PeopleAndPlaces/Creator')]

class BookmarksPanel(Container):
    __guid__ = 'BookmarksPanel'
    default_name = 'BookmarksPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.semaphore = uthread.Semaphore()
        self.scroll = BookmarksScroll(parent=self, id='bookmarksPanelScroll', pushContent=True)
        self.adminFolderId = ('bookmarks', 'adminFolders')
        uicore.registry.SetListGroupOpenState(self.adminFolderId, 0)

    def Setup(self):
        self.ShowPlaces()

    def DropInPlacesFolder(self, folderKey, nodes, *args):
        folderID, subfolderID = folderKey[1]
        forceCopy = uicore.uilib.Key(uiconst.VK_SHIFT)
        bookmarkIDsToMove = set()
        for node in nodes:
            guid = getattr(node, '__guid__', None)
            if guid == 'listentry.PlaceEntry':
                if node.bm is not None:
                    bookmarkIDsToMove.add(node.bm.bookmarkID)

        if bookmarkIDsToMove:
            sm.GetService('bookmarkSvc').MoveOrCopyBookmarks(folderID, subfolderID, bookmarkIDsToMove, forceCopy)

    def BookmarkCurrentLocation(self, *args):
        sm.GetService('addressbook').BookmarkCurrentLocation(*args)

    def RefreshScroll(self):
        if not self.destroyed:
            self.ShowPlaces()

    @threadutils.threaded
    def ShowPlaces(self):
        with self.semaphore:
            self.scroll.ShowLoading()
            locations = set()
            for bm in sm.GetService('bookmarkSvc').GetAllBookmarks().itervalues():
                if bm.itemID is not None:
                    locations.add(bm.itemID)
                if bm.locationID is not None:
                    locations.add(bm.locationID)

            if len(locations):
                cfg.evelocations.Prime(locations, 0)
            scrolllist = self.GetFolderSectionList()
            scrolllist.extend(self.GetAgentPlacesScrollList())
            self.scroll.sr.iconMargin = 18
            scrollToProportion = self.scroll.GetScrollProportion()
            self.scroll.Load(contentList=scrolllist, fixedEntryHeight=None, headers=placesHeaders, scrollTo=scrollToProportion, noContentHint=GetByLabel('UI/PeopleAndPlaces/NoKnownPlaces'), showCollapseIcon=True)
            self.scroll.HideLoading()

    def GetAgentPlacesScrollList(self):
        missiongroupState = uicore.registry.GetListGroupOpenState(('missiongroups', 'agentmissions'))
        agentGroup = uicore.registry.GetLockedGroup('missiongroups', 'agentmissions', GetByLabel('UI/PeopleAndPlaces/AgentMissions'), openState=missiongroupState)
        groupEntry = GetFromClass(ListGroup, {'GetSubContent': self.GetPlacesSubContent_AgentMissions,
         'RefreshScroll': self.RefreshScroll,
         'label': agentGroup['label'],
         'id': agentGroup['id'],
         'groupItems': sm.GetService('bookmarkSvc').GetAgentBookmarks(),
         'headers': placesHeaders,
         'showlen': 0,
         'state': 'locked',
         'showicon': eveicon.agent_mission})
        scrolllist = []
        Sort(scrolllist, key=lambda x: x.label)
        return [groupEntry] + scrolllist

    def GetPlacesSubContent_AgentMissions(self, nodedata, newitems = 0):
        if newitems:
            nodedata.groupItems = sm.GetService('bookmarkSvc').GetAgentBookmarks()
        agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
        scrolllist = []
        headers = [GetByLabel('UI/PeopleAndPlaces/Label'),
         GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/Date'),
         GetByLabel('UI/PeopleAndPlaces/Sol'),
         GetByLabel('UI/PeopleAndPlaces/Con'),
         GetByLabel('UI/PeopleAndPlaces/Reg')]
        if agentMenu:
            for missionNameID, bms, agentID in agentMenu:
                if bms:
                    if isinstance(missionNameID, basestring):
                        missionName = missionNameID
                    else:
                        missionName = GetByMessageID(missionNameID)
                    missionID = unicode(missionNameID) + unicode(agentID)
                    scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetPlacesSubContent_AgentMissions2,
                     'RefreshScroll': self.RefreshScroll,
                     'label': missionName,
                     'id': (missionID, missionName),
                     'groupItems': nodedata.groupItems,
                     'headers': headers,
                     'iconMargin': 18,
                     'showlen': 0,
                     'state': 'locked',
                     'sublevel': 1,
                     'showicon': None}))

        return scrolllist

    def GetPlacesSubContent_AgentMissions2(self, nodedata, newitems = 0):
        if newitems:
            nodedata.groupItems = sm.GetService('bookmarkSvc').GetAgentBookmarks()
        groupID = nodedata.id
        places = [ bm for bm in nodedata.groupItems.itervalues() if bm.missionName == groupID[0] ]
        return self.GetPlacesScrollList(places, groupID, sublevel=2)

    @telemetry.ZONE_METHOD
    def GetFolderSectionList(self):
        contList = []
        self.bookmarksBySubfolderByFolder = sm.GetService('bookmarkSvc').GetBookmarksBySubfolderByFolder()
        folders = sm.GetService('bookmarkSvc').GetFolders().values()
        personalBookmarkCount = 0
        sharedBookmarkCount = 0
        for folder in folders:
            if not folder.isActive:
                continue
            if folder.isPersonal:
                personalBookmarkCount += sum((len(subfolder) for subfolder in self.bookmarksBySubfolderByFolder[folder.folderID].itervalues()))
            else:
                sharedBookmarkCount += sum((len(subfolder) for subfolder in self.bookmarksBySubfolderByFolder[folder.folderID].itervalues()))

        contList.append(GetFromClass(LocalLocationsFolder, {'label': GetByLabel('UI/AclBookmarks/LocationsInSystem', system=cfg.evelocations.Get(session.solarsystemid2).name),
         'id': ('myPlaces', 'localLocations'),
         'headers': placesHeaders,
         'GetSubContent': self.GetLocalLocationsScrollList,
         'open': False,
         'state': 'locked',
         'showicon': eveicon.folder,
         'showlen': False}))
        for isPersonal in [True, False]:
            if isPersonal:
                iconPath = eveicon.folder
                label = GetByLabel('UI/PeopleAndPlaces/PersonalLocations')
                id = ('myPlaces', 'personalFolders')
                count = personalBookmarkCount
            else:
                iconPath = eveicon.shared_folder
                label = GetByLabel('UI/PeopleAndPlaces/SharedLocations')
                id = ('myPlaces', 'sharedFolders')
                count = sharedBookmarkCount
            groupEntry = GetFromClass(ListGroup, {'GetSubContent': self.GetLocationFolderScrollList,
             'label': label,
             'id': id,
             'groupItems': [],
             'folders': folders,
             'isPersonal': isPersonal,
             'headers': placesHeaders,
             'open': False,
             'posttext': '<color=%s>[%d]</color>' % (COLOR_POSTTEXT, count),
             'showlen': False,
             'state': 'locked',
             'showicon': iconPath})
            contList.append(groupEntry)

        return contList

    def GetLocalLocationsScrollList(self, nodedata, newitems = 0):
        bookmark_service = sm.GetService('bookmarkSvc')
        bookmarks = bookmark_service.GetBookmarksForLocationID(session.solarsystemid2)
        return self.GetPlacesScrollList(places=bookmarks, groupID=nodedata.id, sublevel=1, isGroupPersonal=True)

    @telemetry.ZONE_METHOD
    def GetLocationFolderScrollList(self, nodedata, newitems = 0):
        if newitems:
            self.bookmarksBySubfolderByFolder = sm.GetService('bookmarkSvc').GetBookmarksBySubfolderByFolder()
        contList = []
        folders = nodedata.folders
        isPersonal = nodedata.isPersonal
        maxCount = appConst.MAX_BOOKMARKS_IN_PERSONAL_FOLDER if isPersonal else appConst.MAX_BOOKMARKS_IN_SHARED_FOLDER
        activeFolders = [ f for f in folders if f.isActive ]
        activeFolders.sort(key=lambda fld: (-fld.isPersonal, fld.folderName.lower()))
        for folder in activeFolders:
            if folder.isPersonal != isPersonal:
                continue
            folderID = folder.folderID
            count = sum((len(subfolder) for subfolder in self.bookmarksBySubfolderByFolder[folderID].itervalues()))
            if count > maxCount:
                postText = '<color=%s>[%d]</color>' % (COLOR_WARNING_POSTTEXT, count)
                hint = GetByLabel('UI/AclBookmarks/TooManyBookmarksInFolderHint', currentBookmarks=count, maxBookmarks=maxCount)
            else:
                postText = '<color=%s>[%d]</color>' % (COLOR_POSTTEXT, count)
                hint = None
            if isPersonal:
                iconPath = eveicon.folder
            else:
                iconPath = eveicon.shared_folder
            entry = GetFromClass(BookmarkFolderGroup, {'GetSubContent': self.GetPlacesSubfolders,
             'DropData': self.DropInPlacesFolder,
             'hint': hint,
             'label': folder.folderName,
             'folderName': folder.folderName,
             'posttext': postText,
             'id': ('myPlaces', (folderID, None)),
             'groupItems': self.bookmarksBySubfolderByFolder[folderID],
             'folderID': folderID,
             'folder': folder,
             'state': 'locked',
             'showicon': iconPath,
             'showlen': False,
             'sublevel': 1,
             'isDragObject': True,
             'MenuFunction': self.BookmarkACLFolderMenu,
             'allowGuids': ['listentry.PlaceEntry', 'xtriui.InvItem', 'listentry.InvItem']})
            contList.append(entry)

        inactiveFolders = [ x for x in folders if not x.isActive and x.isPersonal == isPersonal ]
        if inactiveFolders:
            inactiveFolders.sort(key=lambda fl: fl.folderName.lower())
            inactiveFoldersEntry = self._GetEntryForInactiveFolders(inactiveFolders, self.bookmarksBySubfolderByFolder)
            contList.append(inactiveFoldersEntry)
        if not isPersonal:
            contList.extend(self.GetAdminFoldersScrollList())
        return contList

    def _GetEntryForInactiveFolders(self, inactiveFolders, bookmarksBySubfolderByFolder):
        entry = GetFromClass(ListGroup, {'GetSubContent': self._GetInactiveFolders,
         'label': GetByLabel('UI/AclBookmarks/InactiveFolders'),
         'id': ('inactiveFolders', None),
         'groupItems': inactiveFolders,
         'bookmarksBySubfolderByFolder': bookmarksBySubfolderByFolder,
         'state': 'locked',
         'showicon': 'hide',
         'showlen': False,
         'sublevel': 1})
        return entry

    def _GetInactiveFolders(self, nodedata, newitems = 0):
        scrollList = []
        for folder in nodedata.groupItems:
            if folder.isPersonal:
                texturePath = eveicon.folder
                iconHint = GetByLabel('UI/AclBookmarks/PersonalFolderType')
            else:
                texturePath = eveicon.shared_folder
                iconHint = GetByLabel('UI/AclBookmarks/SharedFolderType')
            entry = GetFromClass(InactiveFolderEntry, {'label': folder.folderName,
             'folderName': folder.folderName,
             'id': ('inactiveFolder_%s' % folder.folderID, None),
             'folderID': folder.folderID,
             'folder': folder,
             'state': 'locked',
             'texturePath': texturePath,
             'iconHint': iconHint,
             'GetMenu': self.GetMenuForInactiveFolders,
             'sublevel': 2})
            scrollList.append(entry)

        return scrollList

    def GetMenuForInactiveFolders(self, entry):
        return self.BookmarkACLFolderMenu(entry.sr.node)

    def BookmarkACLFolderMenu(self, node):
        menuList = [(MenuLabel('UI/AclBookmarks/FolderInformation'), self.ShowBookmarkFolderInfo, (node.folderID,))]
        if node.folder.accessLevel in (appConst.ACCESS_PERSONAL, appConst.ACCESS_ADMIN):
            menuList.append((MenuLabel('UI/AclBookmarks/EditBookmarkFolder'), self.EditACLFolder, (node.folderID,)))
            menuList.append((MenuLabel('UI/AclBookmarks/DeleteBookmarkFolder'), self.DeleteACLFolder, (node.folderID,)))
        if not node.folder.isPersonal:
            menuList.append((MenuLabel('UI/AclBookmarks/ForgetBookmarkFolder'), self.ForgetFolder, (node.folderID,)))
        if node.folder.isActive:
            menuList.append((MenuLabel('UI/AclBookmarks/MarkFolderAsInactive'), self.MarkFolderAsInactive, (node.folderID,)))
            if node.folder.accessLevel != appConst.ACCESS_VIEW:
                menuList.append((MenuLabel('UI/AclBookmarks/CreateSubfolder'), self.CreateSubFolderInFolder, (node.folderID,)))
        else:
            menuList.append((MenuLabel('UI/AclBookmarks/MarkFolderActive'), self.MarkFolderAsActive, (node.folderID,)))
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            menuList.append(('GM: FolderID: ' + str(node.folderID), blue.pyos.SetClipboardData, (str(node.folderID),)))
        return menuList

    @telemetry.ZONE_METHOD
    def GetSubfolderEntry(self, subfolder, folderID, bookmarks, isPersonal):
        if isPersonal:
            iconPath = eveicon.folder
        else:
            iconPath = eveicon.shared_folder
        if subfolder.creatorID is not None:
            if subfolder.creatorID == invConst.ownerSystem:
                label = GetByLabel(subfolder.subfolderName)
            else:
                label = GetByLabel('UI/PeopleAndPlaces/FolderName', folderName=subfolder.subfolderName, creator=subfolder.creatorID)
        else:
            label = subfolder.subfolderName
        count = len(bookmarks)
        maxCount = MAX_BOOKMARKS_DISPLAYED_IN_GROUP
        if count > maxCount:
            text = GetByLabel('UI/AclBookmarks/TruncatedBookmarksInSubfolder', maxBookmarks=maxCount, currentBookmarks=count)
            postText = '<color=%s>[%s]</color>' % (COLOR_WARNING_POSTTEXT, text)
            hint = GetByLabel('UI/AclBookmarks/TooManyBookmarksInSubfolderHint', currentBookmarks=count, maxBookmarks=maxCount)
        else:
            postText = '<color=%s>[%d]</color>' % (COLOR_POSTTEXT, count)
            hint = None
        return GetFromClass(BaseFolderGroup, {'GetSubContent': self.GetPlacesSubEntries,
         'DropData': self.DropInPlacesFolder,
         'hint': hint,
         'label': label,
         'id': ('myPlaces', (folderID, subfolder.subfolderID)),
         'folderID': folderID,
         'groupItems': bookmarks,
         'posttext': postText,
         'showlen': False,
         'sublevel': 2,
         'subfolderID': subfolder.subfolderID,
         'subfolder': subfolder,
         'MenuFunction': self.BookmarkSubfolderMenu,
         'state': 'locked',
         'showicon': iconPath,
         'isPersonal': isPersonal,
         'allowGuids': ['listentry.PlaceEntry', 'xtriui.InvItem', 'listentry.InvItem']})

    @telemetry.ZONE_METHOD
    def GetPlacesSubEntries(self, nodedata, newitems = 0):
        if newitems:
            places = sm.GetService('bookmarkSvc').GetBookmarksBySubfolderByFolder()[nodedata.folderID][nodedata.subfolderID]
        else:
            places = nodedata.groupItems
        isPersonal = nodedata.isPersonal
        return self.GetPlacesScrollList(places, nodedata.subfolderID, sublevel=3, isGroupPersonal=isPersonal)

    @telemetry.ZONE_METHOD
    def GetPlacesSubfolders(self, nodedata, newitems = 0):
        folderID = nodedata.folderID
        bookmarkSvc = sm.GetService('bookmarkSvc')
        subfolders = bookmarkSvc.GetSubfoldersInFolder(folderID)
        if newitems:
            bookmarksBySubfolder = bookmarkSvc.GetBookmarksBySubfolderByFolder()[folderID]
        else:
            bookmarksBySubfolder = nodedata.groupItems
        entries = []
        isPersonal = nodedata.folder.isPersonal
        for subfolder in Sort(subfolders.values(), key=ConvertSubfolderName):
            entry = self.GetSubfolderEntry(subfolder, folderID, bookmarksBySubfolder[subfolder.subfolderID], isPersonal)
            entries.append(entry)

        entries.extend(self.GetPlacesScrollList(bookmarksBySubfolder[None], (folderID, None), sublevel=2, isGroupPersonal=isPersonal))
        return entries

    def BookmarkSubfolderMenu(self, node):
        folder = sm.GetService('bookmarkSvc').GetBookmarkFolder(node.subfolder.folderID)
        m = []
        if folder.accessLevel != appConst.ACCESS_VIEW and (folder.accessLevel != appConst.ACCESS_USE or node.subfolder.creatorID == session.charid):
            if node.subfolder.creatorID != ownerSystem:
                m += [(MenuLabel('UI/AclBookmarks/EditSubfolder'), self.EditSubfolder, (node.subfolderID,))]
            m += [(MenuLabel('UI/AclBookmarks/DeleteSubfolder'), self.DeleteSubfolder, (node.subfolderID,))]
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            m += [('GM: subfolderID: ' + str(node.subfolderID), blue.pyos.SetClipboardData, (str(node.subfolderID),))]
        return m

    def CreateACLFolder(self, *args):
        wnd = BookmarkContainerWindow.Open()
        wnd.Maximize()

    def ShowBookmarkFolderInfo(self, folderID):
        sm.GetService('bookmarkSvc').ShowBookmarkFolderInfo(folderID)

    def EditACLFolder(self, folderID):
        folder = sm.GetService('bookmarkSvc').GetBookmarkFolder(folderID, refresh=True)
        windowID = '%s_%s' % (BookmarkContainerWindow.default_windowID, folderID)
        wnd = BookmarkContainerWindow.Open(folder=folder, windowID=windowID)
        wnd.Maximize()

    def DeleteACLFolder(self, folderID):
        if sm.GetService('bookmarkSvc').onlyPartiallyLoaded:
            msg = 'ConfirmDeleteFolderPartiallyLoaded'
        else:
            msg = 'ConfirmDeleteFolder'
        if eve.Message(msg, {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('bookmarkSvc').DeleteBookmarkFolder(folderID)

    def ForgetFolder(self, folderID):
        if eve.Message('ConfirmForgetFolder', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('bookmarkSvc').RemoveFromKnownFolders(folderID)

    def MarkFolderAsInactive(self, folderID):
        sm.GetService('bookmarkSvc').UpdateFolderActiveState(folderID, False)

    def MarkFolderAsActive(self, folderID):
        sm.GetService('bookmarkSvc').UpdateFolderActiveState(folderID, True)

    def CreateSubFolderInFolder(self, folderID):
        windowID = '%s_newSub_%s' % (BookmarkSubfolderWindow.default_windowID, folderID)
        wnd = BookmarkSubfolderWindow.Open(folderID=folderID, windowID=windowID)
        wnd.Maximize()

    def CreateSubfolder(self, *args):
        validFolders = sm.GetService('bookmarkSvc').GetFilteredFolders()
        if len(validFolders) == 0:
            if eve.Message('CreateBookmarkFolderAsNoneValid', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
                wnd = BookmarkContainerWindow.Open()
                wnd.Maximize()
            return
        wnd = BookmarkSubfolderWindow.Open()
        wnd.Maximize()

    def EditSubfolder(self, subfolderID):
        subfolder = sm.GetService('bookmarkSvc').GetSubfolder(subfolderID)
        windowID = '%s_%s' % (BookmarkSubfolderWindow.default_windowID, subfolderID)
        wnd = BookmarkSubfolderWindow.Open(subfolder=subfolder, windowID=windowID)
        wnd.Maximize()

    def DeleteSubfolder(self, subfolderID):
        if sm.GetService('bookmarkSvc').onlyPartiallyLoaded:
            msg = 'ConfirmDeleteSubfolderPartiallyLoaded'
        else:
            msg = 'ConfirmDeleteSubfolder'
        if eve.Message(msg, {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('bookmarkSvc').DeleteSubfolder(subfolderID)

    @telemetry.ZONE_METHOD
    def GetPlacesScrollList(self, places, groupID, sublevel, isGroupPersonal = False):
        addressbook = sm.GetService('addressbook')
        bookmarkSvc = sm.GetService('bookmarkSvc')
        scrolllist = []
        unreachabelText = GetByLabel('UI/Common/unreachable')
        coordinateText = GetByLabel('UI/PeopleAndPlaces/Coordinate')
        now = blue.os.GetWallclockTime()
        maxCount = MAX_BOOKMARKS_DISPLAYED_IN_GROUP
        if len(places) > maxCount:
            places = itertools.islice(places, maxCount)
        for bookmark in places:
            hint, comment = bookmarkSvc.UnzipMemo(bookmark.memo)
            sol, con, reg = addressbook.GetSolConReg(bookmark)
            typename = self.GetGroupName(bookmark.typeID)
            date = FmtDate(bookmark.created, 'ls')
            expiry = FmtDate(bookmark.expiry, 'ls') if bookmark.expiry else '-'
            if bookmark and IsCoordinateBookmark(bookmark):
                typename = coordinateText
            jumps = 0
            if 40000000 > bookmark.itemID > 30000000:
                jumps = self.GetJumpCount(session.solarsystemid2, bookmark.itemID)
                if IsUnreachableJumpCount(jumps):
                    jumps = sm.GetService('clientPathfinderService').GetNoRouteFoundText(bookmark.itemID)
            elif 40000000 > bookmark.locationID > 30000000:
                jumps = self.GetJumpCount(session.solarsystemid2, bookmark.locationID)
                if IsUnreachableJumpCount(jumps):
                    jumps = sm.GetService('clientPathfinderService').GetNoRouteFoundText(bookmark.locationID)
            creatorID = getattr(bookmark, 'creatorID', None)
            creatorName = self.GetCreatorName(creatorID)
            isBookmarkAvailable = IsBookmarkAvailable(creatorID, bookmark.created, now)
            folderID = getattr(bookmark, 'folderID', None)
            if folderID is not None:
                _, isPersonal = bookmarkSvc.GetFolderNamesAndType(folderID, subfolderID=getattr(bookmark, 'subfolderID', None))
            else:
                isPersonal = creatorID == session.charid
            text = '<t>'.join((unicode(x) for x in (hint,
             typename,
             jumps,
             sol,
             con,
             reg,
             date,
             expiry,
             creatorName)))
            hintForBookmark = hint
            if getattr(bookmark, 'note', None):
                truncatedNote = bookmark.note[:50] + '...' if len(bookmark.note) > 50 else bookmark.note
                hintForBookmark += '<br>- %s' % truncatedNote
            scrolllist.append(GetFromClass(PlaceEntry, {'bm': bookmark,
             'DropData': lambda *args: self.DropOnBookmark(bookmark, *args),
             'itemID': bookmark.bookmarkID,
             'tabs': [],
             'hint': hintForBookmark,
             'comment': comment,
             'label': text,
             'sublevel': sublevel,
             'listGroupID': groupID,
             'isGroupPersonal': isPersonal,
             'isBookmarkAvailable': isBookmarkAvailable,
             'GetSortValue': self.GetLocationSortValue}))
            blue.pyos.BeNice()

        return scrolllist

    def GetLocationSortValue(self, node, by, sortDirection, idx):
        label = node.label
        strings = label.split('<t>')
        if idx is not None and len(strings) > idx:
            value = strings[idx].lower()
            try:
                value = float(value)
                return value
            except ValueError:
                return value

        val = label.lower()
        return val

    @Memoize
    def GetCreatorName(self, creatorID):
        if creatorID is not None:
            creatorName = cfg.eveowners.Get(creatorID).name
        else:
            creatorName = ''
        return creatorName

    @Memoize
    def GetGroupName(self, typeID):
        return evetypes.GetGroupName(typeID)

    @Memoize(2)
    def GetJumpCount(self, solarsystemID, itemID):
        pathfinder = sm.GetService('clientPathfinderService')
        return pathfinder.GetAutopilotJumpCount(solarsystemID, itemID)

    def DropOnBookmark(self, bookmark, dragNode, nodes, *args):
        if not hasattr(bookmark, 'folderID'):
            return
        groupKey = (None, (bookmark.folderID, bookmark.subfolderID))
        self.DropInPlacesFolder(groupKey, nodes)

    @telemetry.ZONE_METHOD
    def GetAdminFoldersScrollList(self):
        iconPath = eveicon.corporation_folder
        id = self.adminFolderId
        hint = GetByLabel('UI/AclBookmarks/AdminFolderHint')
        groupEntry = GetFromClass(ListGroup, {'GetSubContent': self.GetAdminFolders,
         'RefreshScroll': self.RefreshScroll,
         'label': GetByLabel('UI/AclBookmarks/FolderWithAdminAccess'),
         'id': id,
         'groupItems': [],
         'headers': placesHeaders,
         'hint': hint,
         'open': False,
         'showlen': 0,
         'state': 'locked',
         'showicon': iconPath,
         'sublevel': 1})
        return [groupEntry]

    @telemetry.ZONE_METHOD
    def GetAdminFolders(self, *args):
        searchResults = self.FetchAdminSearchResults()
        scrollList = []
        knownFolders = sm.GetService('bookmarkSvc').foldersNew
        for folder in searchResults:
            name = folder.folderName
            if folder.folderID in knownFolders:
                isKnown = True
                if knownFolders[folder.folderID].isActive:
                    postText = GetByLabel('UI/AclBookmarks/SubscribedActive')
                else:
                    postText = GetByLabel('UI/AclBookmarks/SubscribedInactive')
            else:
                isKnown = False
                postText = GetByLabel('UI/AclBookmarks/NotSubscribed')
            label = '%s  <color=%s>[%s]</color>' % (name, COLOR_POSTTEXT, postText)
            scrollList.append(GetFromClass(AdminFolder, {'hint': postText,
             'label': label,
             'OnDblClick': self.OnDblClickAdminFolder,
             'OnGetMenu': self.ShowMenuAdminFolders,
             'folderID': folder.folderID,
             'folderName': folder.folderName,
             'isKnown': isKnown,
             'sublevel': 2}))

        if not scrollList:
            scrollList.append(GetFromClass(SE_GenericCore, {'label': GetByLabel('UI/AclBookmarks/NoAdminFolderFound'),
             'sublevel': 2}))
        return scrollList

    def FetchAdminSearchResults(self):
        bookmarkSvc = sm.GetService('bookmarkSvc')
        resultFolders = bookmarkSvc.SearchFoldersWithAdminAccess()
        return resultFolders

    def OnDblClickAdminFolder(self, entry):
        node = entry.sr.node
        if node.isKnown:
            self.EditACLFolder(node.folderID)
        else:
            sm.GetService('bookmarkSvc').ShowBookmarkFolderInfo(node.folderID)

    def ShowMenuAdminFolders(self, entry):
        node = entry.sr.node
        menuList = []
        if node.isKnown:
            menuList += [(MenuLabel('UI/AclBookmarks/FolderInformation'), self.ShowBookmarkFolderInfo, (node.folderID,)), (MenuLabel('UI/AclBookmarks/ForgetBookmarkFolder'), self.ForgetFolder, (node.folderID,))]
        else:
            menuList += [(MenuLabel('UI/AclBookmarks/AddFolder'), self.ShowBookmarkFolderInfo, (node.folderID,))]
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            menuList += [('GM: FolderID: ' + str(node.folderID), blue.pyos.SetClipboardData, (str(node.folderID),))]
        return menuList


class BookmarksScroll(eveScroll.Scroll):

    def CollectSubNodes(self, node, nodes = None, clear = 1):
        if nodes is None:
            nodes = []
        for subnode in node.get('subNodes', []):
            if subnode is None:
                continue
            self.CollectSubNodes(subnode, nodes, clear)
            nodes.append(subnode)

        if clear:
            node.subNodes = []
        return nodes


class BaseFolderGroup(ListGroup):

    def Startup(self, *etc):
        ListGroup.Startup(self, *etc)
        self.overlayButton = ButtonIcon(name='overlayButton', parent=self.sr.labelClipper, align=uiconst.CENTERLEFT, width=14, height=14, iconSize=16, left=200, texturePath=eveicon.visibility, func=self.OnChangeSensorOverlayVisibility, colorSelected=COLOR_SELECTED, isSelectedBgUsed=False)

    def Load(self, node):
        ListGroup.Load(self, node)
        self.folderKey = node.id[1]
        self.overlayButton.left = self.sr.label.width + self.sr.label.left + 8
        self.SetIsVisible(GetBookmarkFolderVisibilityManager().IsFolderVisible(self.folderKey))

    def OnChangeSensorOverlayVisibility(self):
        bmVisibilityMgr = GetBookmarkFolderVisibilityManager()
        isVisible = not bmVisibilityMgr.IsFolderVisible(self.folderKey)
        bmVisibilityMgr.SetFolderVisibility(self.folderKey, isVisible)
        sm.ScatterEvent('OnRefreshBookmarks')
        self.SetIsVisible(isVisible)

    def SetIsVisible(self, isVisible):
        if isVisible:
            hint = GetByLabel('UI/PeopleAndPlaces/RemoveLocationFolderFromSensorOverlay')
            self.overlayButton.SetSelected()
        else:
            hint = GetByLabel('UI/PeopleAndPlaces/ShowLocationFolderInSensorOverlay')
            self.overlayButton.SetDeselected()
        self.overlayButton.hint = hint


class BookmarkFolderGroup(BaseFolderGroup):
    isDragObject = True

    def GetDragData(self):
        if self.sr.node.folder.isPersonal:
            return []
        ret = KeyVal(nodeType='BookmarkFolderEntry', folderID=self.sr.node.folderID, label=self.sr.node.folderName)
        return [ret]


class InactiveFolderEntry(Generic):
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.icon = Sprite(parent=self, align=uiconst.CENTERLEFT, pos=(60, 0, 16, 16), state=uiconst.UI_DISABLED)

    def Load(self, node):
        Generic.Load(self, node)
        sublevelCorrection = self.sr.node.scroll.sr.get('sublevelCorrection', 0)
        sublevel = max(0, node.Get('sublevel', 0) - sublevelCorrection)
        iconLeft = 5 + 16 * sublevel
        self.icon.texturePath = node.texturePath
        self.icon.hint = node.iconHint
        self.icon.left = iconLeft
        self.sr.label.left = self.icon.left + 20
        self.sr.label.opacity = self.icon.opacity = 0.6

    def GetDragData(self):
        if self.sr.node.folder.isPersonal:
            return []
        ret = KeyVal(nodeType='BookmarkFolderEntry', folderID=self.sr.node.folderID, label=self.sr.node.folderName)
        return [ret]


class AdminFolder(SE_GenericCore):
    isDragObject = True

    def ApplyAttributes(self, attributes):
        SE_GenericCore.ApplyAttributes(self, attributes)
        self.sr.icon = eveIcon.Icon(icon=eveicon.corporation_folder, parent=self, pos=(37, 2, 16, 16), align=uiconst.RELATIVE, ignoreSize=True, state=uiconst.UI_DISABLED)

    def Load(self, node):
        SE_GenericCore.Load(self, node)
        sublevelCorrection = self.sr.node.scroll.sr.get('sublevelCorrection', 0)
        sublevel = max(0, node.Get('sublevel', 0) - sublevelCorrection)
        self.sr.icon.left = 5 + 16 * sublevel
        self.sr.label.left = self.sr.icon.left + 20

    def GetDragData(self):
        ret = KeyVal(nodeType='BookmarkFolderEntry', folderID=self.sr.node.folderID, label=self.sr.node.folderName)
        return [ret]


class LocalLocationsFolder(ListGroup):

    def Startup(self, *etc):
        super(LocalLocationsFolder, self).Startup(*etc)
        ButtonIcon(parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, idx=self.sr.labelClipper.GetOrder()), align=uiconst.CENTER, texturePath=eveicon.open_window, hint=localization.GetByLabel('UI/Common/OpenInWindow'), func=StandaloneBookmarkWnd.Open, args=())
