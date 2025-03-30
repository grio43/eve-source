#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\bookmarkUtil.py
import eveicon
import localization
import HTMLParser
import blue
import cgi
import telemetry
from collections import defaultdict
from carbonui.control.contextMenu.menuConst import DISABLED_ENTRY0
from carbonui.control.contextMenu.menuEntryData import MenuEntryDataCaption, MenuEntryData
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import CENTERLEFT, UI_DISABLED
from carbonui.control.contextMenu.menuEntryView import MenuEntryView
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eve.common.lib import appConst
from eve.common.script.mgt.bookmarkConst import SHARED_BOOKMARK_DELAY
from eveservices.menu import GetMenuService
from localization import GetByLabel
from inventorycommon.const import ownerSystem
from menu import MenuList
BOOKMARK_RIGHTCLICK_GROUPING_THRESHOLD = 8
BOOKMARK_RIGHTCLICK_GROUPING_TOTAL_THRESHOLD = 30

def GetBookmarkMenu(bookmarks, isPersonal = True):

    def BookmarkMenuBuilder(bookmark):
        return GetMenuService().BookmarkMenu(bookmark)

    menu = MenuList()
    for i, bookmark in enumerate(bookmarks):
        hint, comment = sm.GetService('bookmarkSvc').UnzipMemo(bookmark.memo)
        hint = HTMLParser.HTMLParser().unescape(hint)
        hint = hint if len(hint) < 25 else hint[:25]
        hint = cgi.escape(hint)
        if isPersonal:
            menuClass = PersonalBookmarkMenuEntryView
        else:
            menuClass = SharedBookmarkMenuEntryView
        menu.append(MenuEntryData(hint, subMenuData=lambda _bookmark = bookmark: BookmarkMenuBuilder(_bookmark), menuEntryViewClass=menuClass, func=lambda _bookmark = bookmark: movementFunctions.WarpToBookmark(_bookmark, warpRange=0)))
        if i > 250:
            break

    return localization.util.Sort(menu, key=lambda x: x.text)


def GetFolderedMenuACL(bookmarksBySubfolder, subfolders, label, isPersonal, isSubMenu = True):
    ret = []
    nonFolderedBookmarks = []
    icon = eveicon.folder if isPersonal else eveicon.shared_folder
    for subfolderID, bookmarks in bookmarksBySubfolder.iteritems():
        if subfolderID is None:
            continue
        subMenu = GetBookmarkMenu(bookmarks, isPersonal=isPersonal)
        try:
            ret.append(MenuEntryData(ConvertSubfolderName(subfolders[subfolderID]), subMenuData=subMenu, texturePath=icon))
        except KeyError:
            nonFolderedBookmarks.extend(subMenu)

    ret = localization.util.Sort(ret, key=lambda x: x.text)
    nonFolderedBookmarks.extend(GetBookmarkMenu(bookmarksBySubfolder[None], isPersonal=isPersonal))
    ret.extend(nonFolderedBookmarks)
    if isSubMenu:
        ret = [MenuEntryData(label, subMenuData=ret, texturePath=icon)]
    else:
        ret = [MenuEntryData(label, texturePath=icon)] + ret
    return MenuList(ret)


@telemetry.ZONE_FUNCTION
def GetACLBookmarkMenuForSystem(bookmarks, folders, subfolders, includeTopLevel = True):
    ret = MenuList()
    now = blue.os.GetWallclockTime()
    validBookmarks = [ bookmark for bookmark in bookmarks.itervalues() if bookmark.locationID == session.locationid and IsBookmarkAvailable(bookmark.creatorID, bookmark.created, now) ]
    bookmarksByFolderBySubfolder = defaultdict(lambda : defaultdict(set))
    for bookmark in validBookmarks:
        bookmarksByFolderBySubfolder[bookmark.folderID][bookmark.subfolderID].add(bookmark)

    totalLength = 0
    foldersByFolderType = defaultdict(list)
    for folder in folders.itervalues():
        bookmarksBySubfolder = bookmarksByFolderBySubfolder[folder.folderID]
        bookmarkCount = sum((len(subfolder) for subfolder in bookmarksBySubfolder.itervalues()))
        if not bookmarkCount:
            continue
        entryLength = len(bookmarksBySubfolder)
        if None in bookmarksBySubfolder:
            entryLength += len(bookmarksBySubfolder[None])
            entryLength -= 1
        totalLength += entryLength + 1
        folderType = 'personalFolder' if folder.isPersonal else 'sharedFolder'
        foldersByFolderType[folderType].append((folder, entryLength))

    alwaysGroup = totalLength > BOOKMARK_RIGHTCLICK_GROUPING_TOTAL_THRESHOLD
    for folderType, labelPath in [('personalFolder', 'UI/PeopleAndPlaces/PersonalLocations'), ('sharedFolder', 'UI/PeopleAndPlaces/SharedLocations')]:
        foldersOfType = foldersByFolderType.get(folderType)
        if not foldersOfType:
            continue
        foldersOfType = localization.util.Sort(foldersOfType, key=lambda x: x[0].folderName)
        ret.append(MenuEntryDataCaption(GetByLabel(labelPath)))
        for eachFolder, entryLength in foldersOfType:
            isSubMenu = alwaysGroup
            folderMenu = GetFolderedMenuACL(bookmarksByFolderBySubfolder[eachFolder.folderID], subfolders, eachFolder.folderName, eachFolder.isPersonal, isSubMenu=isSubMenu)
            ret.extend(folderMenu)

    if len(ret) and includeTopLevel:
        ret = [MenuEntryData(GetByLabel('UI/PeopleAndPlaces/Locations'), subMenuData=ret, texturePath=eveicon.location)]
    return ret


def IsCoordinateBookmark(bookmark):
    return (bookmark.itemID == bookmark.locationID or bookmark.typeID == appConst.typeSolarSystem) and bookmark.x


def IsBookmarkAvailable(creatorID, created, now):
    if not creatorID:
        return True
    if creatorID == session.charid:
        return True
    if created + SHARED_BOOKMARK_DELAY < now:
        return True
    return False


def ConvertSubfolderName(subfolder):
    if subfolder.creatorID == ownerSystem:
        name = GetByLabel(subfolder.subfolderName)
    else:
        name = subfolder.subfolderName
    return name


class BaseBookmarkMenuEntryView(MenuEntryView):
    __guid__ = 'BookmarkMenuEntryView'
    texturePath = None


class PersonalBookmarkMenuEntryView(BaseBookmarkMenuEntryView):
    texturePath = None


class SharedBookmarkMenuEntryView(BaseBookmarkMenuEntryView):
    texturePath = None


class PersonalFolderMenuEntryView(BaseBookmarkMenuEntryView):
    texturePath = eveicon.folder


class SharedFolderMenuEntryView(BaseBookmarkMenuEntryView):
    texturePath = eveicon.shared_folder
