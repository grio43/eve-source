#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bookmarks\bookmarkSvc.py
import heapq
from collections import defaultdict
import blue
import telemetry
import threadutils
import uthread
import locks
import utillib
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.bookmarks.linkedBookmarkFolderWindow import LinkedBookmarkFolderWindow
from eve.client.script.util.bookmarkUtil import IsBookmarkAvailable, GetACLBookmarkMenuForSystem
from eve.common.lib import appConst
from eve.common.script.mgt import bookmarkConst
from eve.common.script.mgt.bookmarkConst import SHARED_BOOKMARK_DELAY, MAX_BOOKMARKS_SENT_TO_CLIENT
from eve.common.script.sys import idCheckers
from eveexceptions import UserError
from evetypes import GetCategoryID
from localization import GetByLabel
from sensorsuite.overlay.bookmarkvisibilitymanager import ReleaseBookmarkFolderVisibilityManager
CACHE_EXPIRATION_TIME = 5 * appConst.MIN
MIN_DELAYED_UI_REFRESH_TIME = 5 * appConst.SEC

class BookmarkSvc(Service):
    __guid__ = 'svc.bookmarkSvc'
    __startupdependencies__ = ['machoNet']
    __notifyevents__ = ['OnSharedBookmarksFolderUpdated',
     'OnSharedBookmarksFolderDeleted',
     'OnSharedBookmarksFoldersAccessLost',
     'OnSharedBookmarksFoldersAccessChanged',
     'OnSessionReset']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.Initialize()

    def Initialize(self):
        self.accessGroupBookmarkMgr = sm.RemoteSvc('accessGroupBookmarkMgr')
        self.lastUpdateTime = None
        self.validCategories = (appConst.categoryCelestial,
         appConst.categoryAsteroid,
         appConst.categoryStation,
         appConst.categoryShip,
         appConst.categoryStarbase,
         appConst.categoryPlanetaryInteraction)
        self.bookmarksPrimed = False
        self.foldersNew = {}
        self.bookmarkCache = {}
        self.bookmarkIDsBySolarystemID = defaultdict(set)
        self.subfolders = {}
        self.delayedUpdateQueue = []
        self.delayedUpdateThread = None
        self.onlyPartiallyLoaded = False

    def OnSessionReset(self):
        if self.delayedUpdateThread is not None:
            self.delayedUpdateThread.kill()
        ReleaseBookmarkFolderVisibilityManager()
        self.SearchFoldersWithAdminAccess.clear_memoized()
        self.Initialize()

    @telemetry.ZONE_METHOD
    def GetBookmarks(self):
        self.PrimeAndCleanupBookmarks()
        return self.bookmarkCache

    def PrimeAndCleanupBookmarks(self):
        if not self.bookmarksPrimed:
            self.ACLPrimeBookmarks()
        if self.DoesCacheNeedUpdating():
            self.RefreshACLBookmarks()
            self.lastUpdateTime = blue.os.GetWallclockTime()

    def GetBookmarksForLocationID(self, locationID):
        self.PrimeAndCleanupBookmarks()
        ret = []
        bookmarksForLocationID = self.bookmarkIDsBySolarystemID.get(locationID, set())
        if not bookmarksForLocationID:
            return ret
        for eachBookmarkID in bookmarksForLocationID:
            bm = self.GetBookmark(eachBookmarkID)
            if bm:
                ret.append(bm)

        return ret

    def DoesCacheNeedUpdating(self):
        if self.lastUpdateTime is None:
            return True
        timeSinceLastUpdate = blue.os.GetWallclockTime() - self.lastUpdateTime
        return timeSinceLastUpdate > CACHE_EXPIRATION_TIME

    def GetBookmark(self, bookmarkID):
        return self.bookmarkCache[bookmarkID]

    @threadutils.Throttled(2)
    def RefreshUIOnUpdate(self):
        sm.ScatterEvent('OnRefreshBookmarks')

    def GetPersonalAndSharedFolders(self):
        personal = set()
        shared = set()
        for eachFolderID, eachFolder in self.GetFolders().iteritems():
            if eachFolder.isPersonal:
                personal.add(eachFolderID)
            else:
                shared.add(eachFolderID)

        return (personal, shared)

    def GetAgentBookmarks(self):
        bookmarks = {}
        agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
        if agentMenu:
            for missionNameID, bms, agentID in agentMenu:
                missionName = unicode(missionNameID) + unicode(agentID)
                for bm in bms:
                    c = bm.copy()
                    c.missionName = missionName
                    c.hint = bm.hint
                    c.memo = c.hint + '\t'
                    c.missionNameID = missionNameID
                    c.bookmarkID = ('agentmissions',
                     c.agentID,
                     c.locationType,
                     c.locationNumber)
                    c.expiry = None
                    bookmarks[c.bookmarkID] = c

        return bookmarks

    def GetAllBookmarks(self):
        bms = self.GetBookmarks().copy()
        bms.update(self.GetAgentBookmarks())
        return bms

    def UnzipMemo(self, s):
        if s is None:
            s = ''
        if '\t' in s:
            split = s.split('\t')
        else:
            split = [ each.replace('\\|', '|') for each in s.split('||') ]
        if len(split) == 1:
            return (split[0], '')
        return split[:2]

    @telemetry.ZONE_METHOD
    def ACLPrimeBookmarks(self):
        if self.bookmarksPrimed:
            return
        with locks.TempLock('PrimeACLBookmarks'):
            if self.bookmarksPrimed:
                return
            folders, bookmarks, subfolders = self.accessGroupBookmarkMgr.GetMyActiveBookmarks()
            self.foldersNew = {folder.folderID:folder for folder in folders}
            for eachBookmark in bookmarks:
                self.bookmarkCache[eachBookmark.bookmarkID] = eachBookmark
                self.bookmarkIDsBySolarystemID[eachBookmark.locationID].add(eachBookmark.bookmarkID)

            self.subfolders = {subfolder.subfolderID:subfolder for subfolder in subfolders}
            self.lastUpdateTime = blue.os.GetWallclockTime()
            self.bookmarksPrimed = True
            if len(bookmarks) >= MAX_BOOKMARKS_SENT_TO_CLIENT:
                self.onlyPartiallyLoaded = True
            if not self.foldersNew:
                self.CreateDefaultFolder()
            self.CheckBookmarksForDelayedUpdate(bookmarks)

    @telemetry.ZONE_METHOD
    def RefreshACLBookmarks(self):
        self.LogNotice('RefreshACLBookmarks called')
        self.RemoveExpiredBookmarks()
        self.RefreshUIOnUpdate()

    def RemoveExpiredBookmarks(self):
        for bookmarkID, bookmark in self.bookmarkCache.items():
            if bookmark.expiry and bookmark.expiry < blue.os.GetWallclockTime():
                del self.bookmarkCache[bookmarkID]
                self.bookmarkIDsBySolarystemID[bookmark.locationID].discard(bookmark.bookmarkID)

    def CheckBookmarksForDelayedUpdate(self, bookmarks):
        refreshDelayedAt = []
        for bookmark in bookmarks:
            if not bookmark.creatorID or bookmark.creatorID == session.charid:
                continue
            if bookmark.created + SHARED_BOOKMARK_DELAY > blue.os.GetWallclockTime():
                refreshDelayedAt.append(bookmark.created + SHARED_BOOKMARK_DELAY)

        if refreshDelayedAt:
            self.RefreshUIDelayed(refreshDelayedAt)

    def RefreshUIDelayed(self, timeStamps):
        for timeStamp in timeStamps:
            heapq.heappush(self.delayedUpdateQueue, timeStamp)

        if self.delayedUpdateThread:
            return
        self.delayedUpdateThread = uthread.worker('bookmarkSvc::DelayedUpdateThread', self.DelayedUpdateThread)

    @telemetry.ZONE_METHOD
    def DelayedUpdateThread(self):
        time = 0
        while self.delayedUpdateQueue:
            while self.delayedUpdateQueue:
                time = heapq.heappop(self.delayedUpdateQueue)
                if time > blue.os.GetWallclockTime():
                    break

            sleep = int(max(MIN_DELAYED_UI_REFRESH_TIME, time - blue.os.GetWallclockTime()) / 10000)
            blue.pyos.synchro.SleepWallclock(sleep)
            self.RefreshUIOnUpdate()

        self.delayedUpdateThread = None

    @telemetry.ZONE_METHOD
    def OnSharedBookmarksFolderUpdated(self, updates):
        for target, updateType, updateArgs in updates:
            if updateType == bookmarkConst.BOOKMARKS_MOVED:
                bookmarks, oldFolderID, newFolderID = updateArgs
                if newFolderID not in self.foldersNew or not self.foldersNew[newFolderID].isActive:
                    if oldFolderID in self.foldersNew and self.foldersNew[oldFolderID].isActive:
                        bookmarkIDs = [ bm.bookmarkID for bm in bookmarks ]
                        self._RemoveBookmarksFromCache(bookmarkIDs)
                else:
                    self._AddBookmarksToCache(bookmarks)
                continue
            folderID = target[0]
            if folderID not in self.foldersNew or not self.foldersNew[folderID].isActive:
                self.LogInfo('Tried to update folder, which is not an active folder', folderID)
                continue
            if updateType == bookmarkConst.BOOKMARKS_ADDED:
                bookmarks = updateArgs
                self._AddBookmarksToCache(bookmarks)
            elif updateType == bookmarkConst.BOOKMARKS_REMOVED:
                deletedBookmarkIDs = updateArgs
                self._RemoveBookmarksFromCache(deletedBookmarkIDs)
            elif updateType == bookmarkConst.BOOKMARKS_UPDATED:
                bookmarks = updateArgs
                self._AddBookmarksToCache(bookmarks)
                continue
            elif updateType == bookmarkConst.FOLDER_UPDATED:
                name, description = updateArgs
                self._UpdateFolderInCache(folderID, name, description)
            elif updateType == bookmarkConst.SUBFOLDER_ADDED:
                subfolder = updateArgs
                self._AddSubfolderToCache(subfolder)
            elif updateType == bookmarkConst.SUBFOLDER_UPDATED:
                subfolderID, subfolderName = updateArgs
                self._UpdateSubfolderName(subfolderID, subfolderName)
            elif updateType == bookmarkConst.SUBFOLDER_REMOVED:
                subfolderID = updateArgs
                self._RemoveSubfolderFromCache(subfolderID)

        self.RefreshUIOnUpdate()

    def _AddBookmarksToCache(self, bookmarks):
        for bm in bookmarks:
            self.bookmarkCache[bm.bookmarkID] = bm
            self.bookmarkIDsBySolarystemID[bm.locationID].add(bm.bookmarkID)

        self.CheckBookmarksForDelayedUpdate(bookmarks)

    def _RemoveBookmarksFromCache(self, deletedBookmarkIDs):
        for bookmarkID in deletedBookmarkIDs:
            bm = self.bookmarkCache.pop(bookmarkID, None)
            if bm:
                self.bookmarkIDsBySolarystemID[bm.locationID].discard(bm.bookmarkID)

    def _UpdateFolderInCache(self, folderID, folderName, description):
        if folderID not in self.foldersNew:
            return
        self.foldersNew[folderID].folderName = folderName
        self.foldersNew[folderID].description = description

    def _AddSubfolderToCache(self, subfolder):
        self.subfolders[subfolder.subfolderID] = subfolder

    def _UpdateSubfolderName(self, subfolderID, subfolderName):
        if subfolderID not in self.subfolders:
            return
        self.subfolders[subfolderID].subfolderName = subfolderName

    def _RemoveSubfolderFromCache(self, subfolderID):
        self.subfolders.pop(subfolderID, None)

    def GetFolderNamesAndType(self, folderID, subfolderID):
        folder = self.foldersNew.get(folderID, None)
        isPersonal = folder.isPersonal if folder else True
        subfolder = self.subfolders.get(subfolderID, None)
        folderNames = []
        if folder:
            folderNames.append(folder.folderName)
        if subfolder:
            folderNames.append(subfolder.subfolderName)
        return (folderNames, isPersonal)

    def OnSharedBookmarksFolderDeleted(self, folderID):
        if folderID not in self.foldersNew:
            self.LogInfo('Tried to remove folder, which is not a known folder: ', folderID)
            return
        self.foldersNew.pop(folderID, None)
        self.RemoveFolderContentFromCache([folderID])
        self.RefreshUIOnUpdate()

    def OnSharedBookmarksFoldersAccessLost(self, folderIDs):
        for folderID in folderIDs:
            if folderID not in self.foldersNew:
                self.LogInfo('Tried to remove folder, which is not a known folder: ', folderID)
                continue
            self.foldersNew.pop(folderID, None)

        self.RemoveFolderContentFromCache(folderIDs)
        self.RefreshUIOnUpdate()

    def OnSharedBookmarksFoldersAccessChanged(self, accessChanged):
        for folderID, accessLevel in accessChanged.iteritems():
            if folderID in self.foldersNew:
                self.foldersNew[folderID].accessLevel = accessLevel

    def AddToKnownFolders(self, folderID, isActive):
        maxKnownFolders = appConst.MAX_KNOWN_BOOKMARK_FOLDERS
        if folderID in self.foldersNew:
            self.LogWarn('Tried to add a folder, which has been added already: ', folderID)
            return
        if len(self.foldersNew) >= maxKnownFolders:
            raise UserError('TooManyKnownFolders', {'maxKnownFolders': maxKnownFolders})
        folder, bookmarks, subfolders = self.accessGroupBookmarkMgr.AddToKnownFolders(folderID, isActive)
        self.foldersNew[folderID] = folder
        if folder.isActive:
            for eachBookmark in bookmarks:
                self.bookmarkCache[eachBookmark.bookmarkID] = eachBookmark
                self.bookmarkIDsBySolarystemID[eachBookmark.locationID].add(eachBookmark.bookmarkID)

            self.subfolders.update({subfolder.subfolderID:subfolder for subfolder in subfolders})
            self.CheckBookmarksForDelayedUpdate(bookmarks)
            if len(bookmarks) >= MAX_BOOKMARKS_SENT_TO_CLIENT:
                self.onlyPartiallyLoaded = True
        if isActive and not folder.isActive:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/AclBookmarks/FolderAddedAsInactiveFolder')})
        self.RefreshUIOnUpdate()

    @telemetry.ZONE_METHOD
    def GetActiveBookmarksFiltered(self, solarSystemID = None, usePersonalFilter = False, personal = True):
        filteredFolderIDs = set()
        if usePersonalFilter:
            personalFolderIDs, sharedFolderIDs = self.GetPersonalAndSharedFolders()
            if personal:
                filteredFolderIDs = personalFolderIDs
            else:
                filteredFolderIDs = sharedFolderIDs
        now = blue.os.GetWallclockTime()
        filteredBookmarks = {}
        for bmID, bm in self.GetBookmarks().iteritems():
            if solarSystemID and bm.locationID != solarSystemID:
                continue
            if usePersonalFilter and bm.folderID not in filteredFolderIDs:
                continue
            if IsBookmarkAvailable(bm.creatorID, bm.created, now):
                filteredBookmarks[bmID] = bm

        return filteredBookmarks

    @telemetry.ZONE_METHOD
    def GetFilteredFoldersAndSubfolders(self, forcedFolderID = None):
        filteredFolders = []
        filteredFolderIDs = []
        for folder in self.foldersNew.itervalues():
            if folder.accessLevel == appConst.ACCESS_VIEW:
                continue
            if not folder.isActive:
                continue
            bmCount = sum((1 for bm in self.bookmarkCache.itervalues() if bm.folderID == folder.folderID))
            maxBookmarks = appConst.MAX_BOOKMARKS_IN_PERSONAL_FOLDER if folder.isPersonal else appConst.MAX_BOOKMARKS_IN_SHARED_FOLDER
            if bmCount >= maxBookmarks and (not forcedFolderID or forcedFolderID != folder.folderID):
                continue
            filteredFolders.append(folder)
            filteredFolderIDs.append(folder.folderID)

        filteredSubfolders = [ subfolder for subfolder in self.subfolders.itervalues() if subfolder.folderID in filteredFolderIDs ]
        return (filteredFolders, filteredSubfolders)

    def GetBookmarksFoldersAndSubfolders(self):
        return (self.GetBookmarks(), self.foldersNew, self.subfolders)

    def GetBookmarksBySubfolderByFolder(self):
        bookmarksBySubfolderByFolder = defaultdict(lambda : defaultdict(set))
        for bookmark in self.GetBookmarks().itervalues():
            bookmarksBySubfolderByFolder[bookmark.folderID][bookmark.subfolderID].add(bookmark)

        return bookmarksBySubfolderByFolder

    def CreateBookmarkFolder(self, isPersonal, folderName, description, adminGroupID, manageGroupID, useGroupID, viewGroupID):
        folder = self.accessGroupBookmarkMgr.AddFolder(isPersonal, folderName, description, adminGroupID, manageGroupID, useGroupID, viewGroupID)
        if folder:
            self.foldersNew[folder.folderID] = folder
            self.RefreshUIOnUpdate()
        return folder

    def CreateDefaultFolder(self):
        name = GetByLabel('UI/AclBookmarks/DefaultFolderName')
        self.CreateBookmarkFolder(True, name, '', None, None, None, None)

    @telemetry.ZONE_METHOD
    def UpdateBookmarkFolder(self, folderID, folderName, description, adminGroupID, manageGroupID, useGroupID, viewGroupID):
        if folderID not in self.foldersNew:
            raise UserError('BookmarkFolderNoLongerThere')
        accessLevel = self.accessGroupBookmarkMgr.UpdateFolder(folderID, folderName, description, adminGroupID, manageGroupID, useGroupID, viewGroupID)
        if accessLevel == appConst.ACCESS_NONE:
            self.foldersNew.pop(folderID, None)
            self.RemoveFolderContentFromCache([folderID])
        else:
            self.foldersNew[folderID].update({'folderName': folderName,
             'description': description,
             'adminGroupID': adminGroupID,
             'manageGroupID': manageGroupID,
             'useGroupID': useGroupID,
             'viewGroupID': viewGroupID,
             'accessLevel': accessLevel})
        self.RefreshUIOnUpdate()

    def DeleteBookmarkFolder(self, folderID):
        self.accessGroupBookmarkMgr.DeleteFolder(folderID)
        self.foldersNew.pop(folderID, None)
        self.RemoveFolderContentFromCache([folderID])
        self.RefreshUIOnUpdate()

    def RemoveFromKnownFolders(self, folderID):
        self.accessGroupBookmarkMgr.RemoveFromKnownFolders(folderID)
        self.foldersNew.pop(folderID, None)
        self.RemoveFolderContentFromCache([folderID])
        self.RefreshUIOnUpdate()

    def RemoveFolderContentFromCache(self, folderIDs):
        for bookmarkID, bookmark in self.bookmarkCache.items():
            if bookmark.folderID in folderIDs:
                del self.bookmarkCache[bookmarkID]
                self.bookmarkIDsBySolarystemID[bookmark.locationID].discard(bookmarkID)

        for subfolderID, subfolder in self.subfolders.items():
            if subfolder.folderID in folderIDs:
                del self.subfolders[subfolderID]

    @telemetry.ZONE_METHOD
    def UpdateFolderActiveState(self, folderID, isActive):
        if isActive:
            self.ValidateActiveFolderCount(folderID)
        try:
            folder, bookmarks, subfolders = self.accessGroupBookmarkMgr.UpdateKnownFolderState(folderID, isActive)
        except UserError as e:
            if e.msg in ('BookmarkFolderNoLongerThere', 'FolderAccessDenied'):
                self.foldersNew.pop(folderID, None)
                self.RefreshUIOnUpdate()
            raise

        self.foldersNew[folderID] = folder
        if isActive:
            for eachBookmark in bookmarks:
                self.bookmarkCache[eachBookmark.bookmarkID] = eachBookmark
                self.bookmarkIDsBySolarystemID[eachBookmark.locationID].add(eachBookmark.bookmarkID)

            self.subfolders.update({subfolder.subfolderID:subfolder for subfolder in subfolders})
            self.CheckBookmarksForDelayedUpdate(bookmarks)
            if len(bookmarks) >= MAX_BOOKMARKS_SENT_TO_CLIENT:
                self.onlyPartiallyLoaded = True
        else:
            self.RemoveFolderContentFromCache([folderID])
        self.RefreshUIOnUpdate()

    def ValidateActiveFolderCount(self, folderID):
        folder = self.foldersNew[folderID]
        if folder.isPersonal:
            maxActiveFolders = appConst.MAX_ACTIVE_PERSONAL_BOOKMARK_FOLDERS
            activeFolder = sum((1 for f in self.foldersNew.itervalues() if f.isPersonal and f.isActive))
        else:
            maxActiveFolders = appConst.MAX_ACTIVE_SHARED_BOOKMARK_FOLDERS
            activeFolder = sum((1 for f in self.foldersNew.itervalues() if not f.isPersonal and f.isActive))
        if activeFolder >= maxActiveFolders:
            raise UserError('TooManyActiveFolders', {'maxPersonalFolders': appConst.MAX_ACTIVE_PERSONAL_BOOKMARK_FOLDERS,
             'maxSharedFolders': appConst.MAX_ACTIVE_SHARED_BOOKMARK_FOLDERS})

    def GetBookmarkFolder(self, folderID, refresh = False):
        if refresh:
            folder = self.accessGroupBookmarkMgr.GetFolderInfo(folderID)
            folder.isActive = self.foldersNew[folderID].isActive
            self.foldersNew[folderID] = folder
        return self.foldersNew[folderID]

    def GetFolderInfo(self, folderID):
        if folderID in self.foldersNew:
            return self.foldersNew[folderID]
        else:
            return self.accessGroupBookmarkMgr.GetFolderInfo(folderID)

    def GetFolders(self):
        return self.foldersNew

    def GetFilteredFolders(self):
        filteredFolders = []
        for folder in self.foldersNew.itervalues():
            if folder.accessLevel == appConst.ACCESS_VIEW:
                continue
            if not folder.isActive:
                continue
            filteredFolders.append(folder)

        return filteredFolders

    def ShowBookmarkFolderInfo(self, folderID):
        alreadyKnown = folderID in self.foldersNew
        try:
            folder = self.GetFolderInfo(folderID)
        except UserError as e:
            if e.msg == 'FolderAccessDenied':
                eve.Message('CustomInfo', {'info': GetByLabel('UI/AclBookmarks/NoAccessToBookmarkFolder')})
                return
            raise

        wnd = LinkedBookmarkFolderWindow.GetIfOpen()
        if wnd:
            if wnd.folder.folderID == folderID:
                return wnd.Maximize()
            wnd.Close()
        LinkedBookmarkFolderWindow.Open(folder=folder, alreadyKnown=alreadyKnown)

    def CreateSubfolder(self, folderID, subfolderName):
        subfolder = self.accessGroupBookmarkMgr.CreateSubfolder(folderID, subfolderName)
        if subfolder:
            self.subfolders[subfolder.subfolderID] = subfolder
            self.RefreshUIOnUpdate()

    def UpdateSubfolder(self, folderID, subfolderID, subfolderName):
        if self.accessGroupBookmarkMgr.UpdateSubfolder(folderID, subfolderID, subfolderName):
            self.subfolders[subfolderID].subfolderName = subfolderName
            self.RefreshUIOnUpdate()
        else:
            raise UserError('BookmarkSubfolderNoLongerThere')

    def DeleteSubfolder(self, subfolderID):
        if subfolderID not in self.subfolders:
            raise UserError('BookmarkSubfolderNoLongerThere')
        subfolder = self.subfolders[subfolderID]
        folder = self.foldersNew[subfolder.folderID]
        if folder.accessLevel == appConst.ACCESS_USE:
            for bookmark in self.bookmarkCache.itervalues():
                if bookmark.subfolderID == subfolderID and bookmark.creatorID != session.charid:
                    raise UserError('CouldNotDeleteBookmarksInSubfolder')

        deletedBookmarkIDs = self.accessGroupBookmarkMgr.DeleteSubfolder(subfolder.folderID, subfolderID)
        self.subfolders.pop(subfolderID, None)
        for bookmarkID in deletedBookmarkIDs:
            bm = self.bookmarkCache.pop(bookmarkID, None)
            if bm:
                self.bookmarkIDsBySolarystemID[bm.locationID].discard(bm.bookmarkID)

        self.RefreshUIOnUpdate()

    def GetSubfolder(self, subfolderID):
        return self.subfolders[subfolderID]

    def GetSubfolders(self):
        return self.subfolders

    def GetSubfoldersInFolder(self, folderID):
        return {subfolder.subfolderID:subfolder for subfolder in self.subfolders.itervalues() if subfolder.folderID == folderID}

    @telemetry.ZONE_METHOD
    def ACLBookmarkLocation(self, itemID, folderID, name, comment, itemTypeID, expiry, subfolderID = None):
        categoryID = GetCategoryID(itemTypeID)
        if idCheckers.IsRegion(itemID) or idCheckers.IsConstellation(itemID) or idCheckers.IsSolarSystem(itemID) or idCheckers.IsStation(itemID) or idCheckers.IsStructure(categoryID):
            bookmarkID, itemID, typeID, x, y, z, locationID, expiryDate = self.accessGroupBookmarkMgr.BookmarkStaticLocation(itemID, folderID, name, comment, expiry, subfolderID=subfolderID)
        else:
            bp = sm.StartService('michelle').GetRemotePark()
            if not bp:
                raise UserError('BkmMustBeInFlight')
            bookmarkID, itemID, typeID, x, y, z, locationID, expiryDate = bp.BookmarkLocation(itemID, folderID, name, comment, expiry, subfolderID=subfolderID)
        if bookmarkID:
            self.NewBookmarkCreated(bookmarkID, folderID, itemID, typeID, name, comment, expiryDate, locationID, x, y, z, subfolderID, itemTypeID)

    @telemetry.ZONE_METHOD
    def ACLBookmarkScanResult(self, locationID, name, comment, resultID, folderID, expiry, subfolderID = None):
        itemID, typeID = sm.GetService('sensorSuite').GetPositionalSiteItemIDFromTargetID(resultID)
        if itemID is not None:
            self.ACLBookmarkLocation(itemID, folderID, name, comment, typeID, expiry, subfolderID=subfolderID)
            return
        bookmarkID, itemID, typeID, x, y, z, locationID, expiryDate = sm.StartService('michelle').GetRemotePark().BookmarkScanResult(locationID, name, comment, resultID, folderID, expiry, subfolderID=subfolderID)
        if bookmarkID:
            self.NewBookmarkCreated(bookmarkID, folderID, None, typeID, name, comment, expiryDate, locationID, x, y, z, subfolderID, None)

    def NewBookmarkCreated(self, bookmarkID, folderID, itemID, typeID, name, comment, expiryDate, locationID, x, y, z, subfolderID, itemTypeID):
        bm = utillib.KeyVal(bookmarkID=bookmarkID, folderID=folderID, itemID=itemID, typeID=typeID, flag=None, memo=name, created=blue.os.GetWallclockTimeNow(), expiry=expiryDate, x=x, y=y, z=z, locationID=locationID, note=comment, subfolderID=subfolderID, creatorID=session.charid)
        self.bookmarkCache[bookmarkID] = bm
        self.bookmarkIDsBySolarystemID[bm.locationID].add(bm.bookmarkID)
        self.RefreshUIOnUpdate()
        sm.ScatterEvent('OnBookmarkCreated', bookmarkID, comment, itemTypeID)

    def UpdateACLBookmark(self, bookmarkID, folderID, name, note, subfolderID, newFolderID, expiryCancel):
        if bookmarkID not in self.bookmarkCache:
            raise UserError('BookmarkNotAvailable')
        bookmark = self.bookmarkCache[bookmarkID]
        self.accessGroupBookmarkMgr.UpdateBookmark(bookmarkID, folderID, name, note, subfolderID, newFolderID, expiryCancel)
        bookmark.folderID = newFolderID
        bookmark.memo = name
        bookmark.note = note
        bookmark.subfolderID = subfolderID
        if expiryCancel:
            bookmark.expiry = None
        self.RefreshUIOnUpdate()

    def DeleteBookmarks(self, bookmarkIDs):
        bookmarksByFolder = defaultdict(set)
        for bookmarkID in bookmarkIDs:
            bookmark = self.bookmarkCache[bookmarkID]
            bookmarksByFolder[bookmark.folderID].add(bookmarkID)

        deletedBookmarks = []
        for folderID, bookmarks in bookmarksByFolder.iteritems():
            deleted = self.accessGroupBookmarkMgr.DeleteBookmarks(folderID, bookmarks)
            deletedBookmarks.extend(deleted)

        if not deletedBookmarks:
            raise UserError('CouldNotDeleteBookmark')
        for bookmarkID in deletedBookmarks:
            bm = self.bookmarkCache.pop(bookmarkID, None)
            if bm:
                self.bookmarkIDsBySolarystemID[bm.locationID].discard(bookmarkID)

        self.RefreshUIOnUpdate()

    @telemetry.ZONE_METHOD
    def MoveOrCopyBookmarks(self, folderID, subfolderID, bookmarkIDs, forceCopy):
        bookmarksToMoveBySourceFolder = defaultdict(set)
        bookmarksToCopyBySourceFolder = defaultdict(set)
        for bookmarkID in bookmarkIDs:
            bookmark = self.bookmarkCache[bookmarkID]
            if bookmark.subfolderID == subfolderID and bookmark.folderID == folderID:
                continue
            if forceCopy or self.foldersNew[bookmark.folderID].accessLevel not in (appConst.ACCESS_PERSONAL, appConst.ACCESS_MANAGE, appConst.ACCESS_ADMIN):
                bookmarksToCopyBySourceFolder[bookmark.folderID].add(bookmarkID)
            else:
                bookmarksToMoveBySourceFolder[bookmark.folderID].add(bookmarkID)

        for oldFolderID, bookmarkIDs in bookmarksToMoveBySourceFolder.iteritems():
            rows, message = self.accessGroupBookmarkMgr.MoveBookmarksToFolderAndSubfolder(oldFolderID, folderID, subfolderID, bookmarkIDs)
            if message is not None:
                uthread.new(eve.Message, *message)
            for row in rows:
                try:
                    self.bookmarkCache[row.bookmarkID].folderID = row.folderID
                    self.bookmarkCache[row.bookmarkID].subfolderID = row.subfolderID
                except KeyError:
                    self.LogInfo('Bookmark not found in cache after moving it:', row.bookmarkID)

        for oldFolderID, bookmarkIDs in bookmarksToCopyBySourceFolder.iteritems():
            newBookmarks, message = self.accessGroupBookmarkMgr.CopyBookmarksToFolderAndSubfolder(oldFolderID, folderID, subfolderID, bookmarkIDs)
            if message is not None:
                uthread.new(eve.Message, *message)
            for eachBookmark in newBookmarks.itervalues():
                self.bookmarkIDsBySolarystemID[eachBookmark.locationID].add(eachBookmark.bookmarkID)

            self.bookmarkCache.update(newBookmarks)

        self.RefreshUIOnUpdate()

    @Memoize(2)
    def SearchFoldersWithAdminAccess(self):
        result = self.accessGroupBookmarkMgr.SearchFoldersWithAdminAccess()
        return result

    def GetBookmarkMenuForNavigation(self, includeTopLevel = True):
        m = []
        bookmarks, folders, subfolders = self.GetBookmarksFoldersAndSubfolders()
        bookmarkMenu = GetACLBookmarkMenuForSystem(bookmarks, folders, subfolders, includeTopLevel)
        if bookmarkMenu:
            m += bookmarkMenu
        return m
