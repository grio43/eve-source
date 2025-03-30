#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\evePhotosvc.py
import datetime
import numbers
import os
import rfc822
import shutil
import sys
import time
import logging
from carbon.common.script.sys.service import Service
from collections import defaultdict
import blue
import evetypes
import inventorycommon.const as const
import inventorycommon.typeHelpers
import localization
import requests
import trinity
import uthread
from carbon.common.script.util import commonutils, logUtil as log
from carbonui.control.browser import browserutil
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetBuffersize
from eve.client.script.ui.shared.maps.map2D import Map2D
from eve.common.script.sys import idCheckers
from evephotosvc.const import NONE_PATH
from fsdBuiltData.common import graphicIDs
from iconrendering2.const import IconRenderFormat, IconStyle, STYLE_STRINGS, BACKGROUND_PATHS
from iconrendering2.factory.recipe import GetBlueprintBackgroundAndOverlay
from iconrendering2.renderers.renderer_base import IconRenderInfo
from iconrendering2.renderers.renderer_fromfile import FromFileIconRenderer
from iconrendering2.utils import GetIconFileFromSheet
from industry.const import REACTION_GROUPS
from globalConfig import GetImageServerMissingImageRetryDelay, IMAGE_SERVER_MISSING_IMAGE_RETRY_DELAY_IN_SECONDS_DEFAULT
from monolithconfig import add_global_config_callback
logger = logging.getLogger(__name__)
NOT_AVAILABLE_PATH = 'res:/UI/Texture/notavailable.dds'
MAX_PORTRAIT_THREADS = 5
MAX_CACHE_AGE = 60 * 60 * 1
DEFAULT_PORTRAIT_SIZE = 512
DEFAULT_PORTRAIT_SAVE_SIZE = 1024
PORTRAIT_SIZES = (32,
 64,
 128,
 256,
 512)
CORP_ALLIANCE_SIZES = (64, 128, 512)
DEFAULT_MARKETING_TEST_IMAGE_SERVER = 'http://cdn1.eveonline.com/marketing/InGameVirtualGoodsStore/TestServersImages/'

def GetPictureFileName(typeID, graphicID, size):
    shaderModel = trinity.GetShaderModel()
    name = '%s_%s_%s_%s_%s.dds' % (shaderModel,
     graphicID or 0,
     evetypes.GetIconID(typeID) or 0,
     evetypes.GetRaceID(typeID) or 0,
     size)
    return name


def GetCachePath(typeID, graphicID, size, itemID, blueprint = None):
    if blueprint == IconStyle.BP_COPY:
        return u'cache:/Pictures/Blueprints/bpc_%s' % GetPictureFileName(typeID, graphicID, size)
    elif blueprint == IconStyle.BP_RELIC:
        return u'cache:/Pictures/Blueprints/relic_%s' % GetPictureFileName(typeID, graphicID, size)
    elif blueprint == IconStyle.BP_ORIGINAL:
        return u'cache:/Pictures/Blueprints/bp_%s' % GetPictureFileName(typeID, graphicID, size)
    elif blueprint == IconStyle.BP_DUST:
        return u'cache:/Pictures/Blueprints/dust_%s_%s_%s.dds' % (trinity.GetShaderModel(), typeID, size)
    else:
        return u'cache:/Pictures/Gids/' + GetPictureFileName(typeID, graphicID, size)


def GetRenderPath(graphicID, size, blueprint):
    if size > 64:
        size = 128
    else:
        size = 64
    if blueprint == IconStyle.BP_COPY:
        fileName = '%s_%s_%s.png' % (graphicID, 64, STYLE_STRINGS[blueprint].upper())
    elif blueprint == IconStyle.BP_ORIGINAL:
        fileName = '%s_%s_%s.png' % (graphicID, 64, STYLE_STRINGS[blueprint].upper())
    else:
        fileName = '%s_%s.png' % (graphicID, size)
    iconFolder = graphicIDs.GetIconFolder(graphicID)
    if iconFolder is not None:
        return iconFolder + '/' + fileName
    return fileName


def DoLogIt(path):
    if not commonutils.IsFullLogging() and 'portrait' in path.lower():
        return False
    return True


class EvePhoto(Service):
    __guid__ = 'svc.photo'
    __exportedcalls__ = {'GetPortrait': [],
     'AddPortrait': [],
     'GetAllianceLogo': [],
     'GetCorporationLogo': [],
     'OrderByTypeID': [],
     'CheckAvail': [],
     'GetTextureFromURL': [],
     'CheckDates': [],
     'GetIconByType': [],
     'SavePortraits': []}
    __startupdependencies__ = ['settings', 'machoNet']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        super(EvePhoto, self).__init__()
        self.notavail = {}
        self.imageServerQueue = defaultdict(list)
        self.currentlyFetching = defaultdict(list)
        self.fetchingFromImageServer = 0
        self.portraitregistrations = {}
        self.byTypeIDQue = []
        self.byTypeID_IsRunning = 0
        self.types = {}
        self.gidque = []
        self.gidrunning = 0
        self.gidcount = 0
        self.faceoptions = {}
        self.chappcache = None
        self.photoscene = None
        self.CheckDates(blue.paths.ResolvePathForWriting(u'cache:/Browser/Img'))
        self.CheckDates(blue.paths.ResolvePathForWriting(u'cache:/Pictures/Portraits'))
        self.CheckDates(blue.paths.ResolvePathForWriting(u'cache:/Pictures/Gids'))
        self.urlloading = {}
        self.pendingPI = {}
        self.portraits = None
        self.allianceLogos = None
        self.corpLogos = None
        self.storeBannerImages = None
        self.pendingPortraitGeneration = set()
        self.defaultImageServerForUser = None
        self.defaultMarketingImages = None
        if not blue.pyos.packaged:
            username = os.environ.get('USERNAME')
            if username is None:
                username = os.environ.get('USER')
            if username is not None:
                self.defaultImageServerForUser = 'http://%s.dev.image/' % username.replace('.', '_').lower()
                self.LogInfo('Guessing ImageServer url as we are not in a build client: ', self.defaultImageServerForUser)
                self.defaultMarketingImages = DEFAULT_MARKETING_TEST_IMAGE_SERVER

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' or 'corpid' in change:
            if session.corpid:
                for size in CORP_ALLIANCE_SIZES:
                    self.GetCorporationLogo(session.corpid, size)

        if 'charid' or 'allianceid' in change:
            if session.allianceid:
                for size in CORP_ALLIANCE_SIZES:
                    self.GetAllianceLogo(session.allianceid, size)

    def CheckAvail(self, path):
        pathLog = path if DoLogIt(path) else ''
        self.LogInfo('CheckAvail ', pathLog)
        if path in self.notavail:
            self.LogInfo('CheckAvail ', pathLog, ' is in notavail')
            return None
        elif blue.paths.exists(path):
            self.LogInfo('CheckAvail ', pathLog, ' exists')
            return path
        else:
            self.LogInfo('CheckAvail ', pathLog, " doesn't exist, and has been added to notavail")
            self.notavail[path] = 1
            return None

    def GetValidBlueprintPath(self, sprite, typeID, size = 64, blueprint = None):
        graphicID = evetypes.GetGraphicID(typeID)
        cachePath = GetCachePath(typeID, graphicID, size, None, blueprint)
        resFile = blue.ResFile()
        try:
            if resFile.Open(cachePath):
                self.LogInfo('GetValidBlueprintPath ', cachePath, ' exists')
                return cachePath
        finally:
            del resFile

        graphic = inventorycommon.typeHelpers.GetIcon(typeID)
        if graphic and graphic.iconFile:
            iconPath = graphic.iconFile.strip()
            iconPath = GetIconFileFromSheet(iconPath)
        else:
            iconPath = sprite.texture.resPath
        background, overlay = GetBlueprintBackgroundAndOverlay(blueprint if blueprint else IconStyle.BP_ORIGINAL)
        uthread.new(self.RenderBlueprint, sprite, cachePath, size, iconPath, background, overlay)
        self._RemovePathFromNotAvailList(cachePath)
        return cachePath

    def RenderBlueprint(self, sprite, cachePath, size, iconPath, background, overlay):
        renderInfo = IconRenderInfo(os.path.dirname(cachePath), os.path.basename(cachePath), size, IconRenderFormat.PNG)
        renderInfo.background = BACKGROUND_PATHS.get(background, None)
        renderInfo.overlay = overlay
        renderInfo.inputIcon = iconPath
        renderer = FromFileIconRenderer()
        renderer.useAsyncSave = False
        renderer.AddRenderInfo(renderInfo)
        renderer.Render()
        sprite.ReloadTexture()

    def DoBlueprint(self, sprite, typeID, size = 64, blueprint = None):
        if not sprite.texture:
            return
        texture = sprite.texture.resPath
        bpPath = self.GetValidBlueprintPath(sprite, typeID, size, blueprint)
        if sprite.texture.resPath == texture:
            sprite.texture.resPath = bpPath
            sprite.rectLeft = 0
            sprite.rectWidth = 0
            sprite.rectTop = 0
            sprite.rectHeight = 0

    def GetTextureFromURL(self, path, currentURL = None, ignoreCache = 0, dontcache = 0, fromWhere = None, sizeonly = 0, retry = 1):
        if path.endswith('.blue'):
            return self.GetPic_blue(path)
        fullPath = browserutil.ParseURL(path, currentURL)[0]
        if path.startswith('res:'):
            try:
                surface = trinity.Tr2HostBitmap()
                surface.CreateFromFile(path)
                w, h = surface.width, surface.height
                bw, bh = GetBuffersize(w), GetBuffersize(h)
                if sizeonly:
                    return (path,
                     w,
                     h,
                     bw,
                     bh)
                return self.ReturnTexture(path, w, h, bw, bh)
            except:
                self.LogError('Failed to load image', path)
                if self.urlloading.has_key(fullPath):
                    del self.urlloading[fullPath]
                sys.exc_clear()
                return self.ErrorPic(sizeonly)

        if ignoreCache:
            sm.GetService('imageCache').InvalidateImage(fullPath)
        while self.urlloading.has_key(fullPath):
            blue.pyos.BeNice()

        if not dontcache:
            cacheData = sm.GetService('imageCache').GetFromCache(fullPath)
            if cacheData and os.path.exists(cacheData[0].replace('cache:/', blue.paths.ResolvePath(u'cache:/'))):
                if sizeonly:
                    return cacheData
                return self.ReturnTexture(*cacheData)
        try:
            self.urlloading[fullPath] = 1
            ret = requests.get(fullPath)
            cacheID = int(str(blue.os.GetWallclockTime()) + str(uthread.uniqueId() or uthread.uniqueId()))
            imagestream = ret.content
            ret.headers = {key.lower():value for key, value in ret.headers.iteritems()}
            ext = None
            if 'content-type' in ret.headers.keys() and ret.headers['content-type'].startswith('image/'):
                ext = ret.headers['content-type'][6:]
            if ext == None or ext == 'png':
                header = imagestream[:16]
                for sig, sext in [('PNG', 'PNG'),
                 ('GIF', 'GIF'),
                 ('JFI', 'JPEG'),
                 ('BM8', 'BMP')]:
                    for i in xrange(0, 12):
                        if header[i:i + 3] == sig:
                            ext = sext
                            break

                if not ext:
                    header = imagestream[-16:]
                    for sig, sext in [('XFILE', 'TGA')]:
                        for i in xrange(0, 10):
                            if header[i:i + 5] == sig:
                                ext = sext
                                break

            if ext:
                filename = '%sBrowser/Img/%s.%s' % (blue.paths.ResolvePath(u'cache:/'), cacheID, ext)
                resfile = blue.classes.CreateInstance('blue.ResFile')
                if not resfile.Open(filename, 0):
                    resfile.Create(filename)
                resfile.Write(imagestream)
                resfile.Close()
                surface = trinity.Tr2HostBitmap()
                surface.CreateFromFile(filename)
                w, h = surface.width, surface.height
                bw, bh = GetBuffersize(w), GetBuffersize(h)
                cachePath = 'cache:/Browser/Img/%s.%s' % (cacheID, ext)
                if 'pragma' not in ret.headers.keys() or ret.headers['Pragma'].find('no-cache') == -1:
                    sm.GetService('imageCache').Cache(fullPath, (cachePath,
                     w,
                     h,
                     bw,
                     bh))
                del self.urlloading[fullPath]
                if sizeonly:
                    return (cachePath,
                     w,
                     h,
                     bw,
                     bh)
                return self.ReturnTexture(cachePath, w, h, bw, bh)
            del self.urlloading[fullPath]
            return self.ErrorPic(sizeonly)
        except Exception as e:
            if retry:
                sys.exc_clear()
                if self.urlloading.has_key(fullPath):
                    del self.urlloading[fullPath]
                return self.GetTextureFromURL(path, currentURL, ignoreCache, dontcache, fromWhere, sizeonly, 0)
            self.LogError(e, 'Failed to load image', repr(path))
            if self.urlloading.has_key(fullPath):
                del self.urlloading[fullPath]
            sys.exc_clear()
            return self.ErrorPic(sizeonly)

    def ErrorPic(self, sizeonly = 0):
        if sizeonly:
            return (NONE_PATH,
             32,
             32,
             32,
             32)
        tex = trinity.Tr2Sprite2dTexture()
        tex.resPath = NONE_PATH
        return (tex, 32, 32)

    def CleanExt(self, ext):
        validNot3Letters = ('jpeg',)
        for _ext in validNot3Letters:
            if ext.lower().startswith(_ext):
                return _ext

        return ext[:3]

    def ReturnTexture(self, path, width, height, bufferwidth, bufferheight):
        tex = trinity.Tr2Sprite2dTexture()
        tex.resPath = path
        return (tex, width, height)

    def CheckDates(self, path):
        now = long(time.time())
        rem = []
        for fileName in os.listdir(path):
            if fileName.split('.')[-1] in ('blue', 'dat', 'txt'):
                continue
            lastRead = os.path.getatime(path + '/' + fileName)
            age = now - lastRead
            if age / 2592000:
                rem.append(fileName)

        for each in rem:
            os.remove(path + '/' + each)

    def InitializePortraits(self):
        if self.portraits is None:
            imageServer = self.GetImageServerURL('imageserverurl', self.defaultImageServerForUser)
            self.portraits = RemoteImageCacher('Character', self, '.jpg', imageServer, self.machoNet)
            self.pendingPortraitGeneration = settings.user.ui.Get('pendingPortraitGeneration', set())
            for charID in self.pendingPortraitGeneration:
                self.LogInfo('Character', charID, 'is marked as newly customized.')
                self.portraits.AddToWatchList(charID, self.PortraitDownloaded)
                for size in PORTRAIT_SIZES:
                    if size == DEFAULT_PORTRAIT_SIZE:
                        continue
                    self.portraits.RemoveFromCache(charID, size)

    def PortraitDownloaded(self, charID):
        self.pendingPortraitGeneration = settings.user.ui.Get('pendingPortraitGeneration', set())
        if charID in self.pendingPortraitGeneration:
            self.pendingPortraitGeneration.discard(charID)
            settings.user.ui.Set('pendingPortraitGeneration', self.pendingPortraitGeneration)

    def GetPortrait(self, charID, size, sprite = None, orderIfMissing = True, callback = False, allowServerTrip = False):
        self.InitializePortraits()
        size = self.FindBestPortraitSize(size)
        defaultIcon = self.GetPortraitDefaultIcon(size)
        if charID in self.pendingPortraitGeneration:
            size = DEFAULT_PORTRAIT_SIZE
        callback = 'OnPortraitCreated' if callback else None
        path = self.GetImage(charID, size, self.portraits, sprite, orderIfMissing, callback, defaultIcon)
        if path == defaultIcon:
            return
        else:
            return path

    def GetPortraitDefaultIcon(self, size):
        if size > 64:
            defaultIcon = 'res:/UI/Texture/silhouette.png'
        else:
            defaultIcon = 'res:/UI/Texture/silhouette_64.png'
        return defaultIcon

    def SavePortraits(self, charIDs):
        if type(charIDs) != list:
            charIDs = [charIDs]
        uthread.new(self._SavePortraits, charIDs)

    def GetPortraitSaveSize(self):
        portraitSize = sm.GetService('machoNet').GetGlobalConfig().get('defaultPortraitSaveSize')
        if portraitSize is None:
            portraitSize = DEFAULT_PORTRAIT_SAVE_SIZE
        self.LogInfo('Portrait will be saved at', portraitSize)
        return int(portraitSize)

    def _SavePortraits(self, charIDs):
        length = len(charIDs)
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Shared/GeneratingPicture'), '', 0, length)
        portraitSaveSize = self.GetPortraitSaveSize()
        for i, charID in enumerate(charIDs):
            imagePath = self.portraits.GetImage(charID, portraitSaveSize, forceUpdate=True)
            if imagePath:
                cacheFile = blue.paths.ResolvePath(imagePath)
                try:
                    shutil.copy2(cacheFile, blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/capture/Portraits/%s.jpg' % charID)
                except WindowsError as e:
                    log.LogTraceback('Failed to copy character image')
                    self.LogError(e, 'Failed to copy character image')

            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Shared/GeneratingPicture'), '', i + 1, length)

        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Shared/GeneratingPicture'), '', length, length)

    def GetAllianceLogo(self, allianceID, size, sprite = None, orderIfMissing = True, callback = False):
        if self.allianceLogos is None:
            imageServer = self.GetImageServerURL('imageserverurl', self.defaultImageServerForUser)
            self.allianceLogos = RemoteImageCacher('Alliance', self, '.png', imageServer, self.machoNet)
        callback = 'OnAllianceLogoReady' if callback else None
        img = self.GetImage(allianceID, size, self.allianceLogos, sprite, orderIfMissing, callback, 'res:/UI/Texture/defaultAlliance.dds', isCorpOrAlliance=True)
        return img

    def GetCorporationLogo(self, corpID, size, sprite = None, orderIfMissing = True, callback = False):
        if self.corpLogos is None:
            imageServer = self.GetImageServerURL('imageserverurl', self.defaultImageServerForUser)
            self.corpLogos = RemoteImageCacher('Corporation', self, '.png', imageServer, self.machoNet)
        callback = 'OnCorpLogoReady' if callback else None
        img = self.GetImage(corpID, size, self.corpLogos, sprite, orderIfMissing, callback, 'res:/UI/Texture/defaultCorporation.dds', isCorpOrAlliance=True)
        return img

    def GetImage(self, itemID, size, handler, sprite = None, orderIfMissing = True, callback = None, defaultIcon = 'res:/UI/Texture/notavailable.dds', isCorpOrAlliance = False):
        if uicore.desktop.dpiScaling > 1.0 and not isCorpOrAlliance:
            size = size * 2
        if not isinstance(itemID, numbers.Integral):
            return defaultIcon
        path, isFresh = handler.GetCachedImage(itemID, size)
        if sprite is not None:
            sprite.LoadTexture(path or defaultIcon)
        if not isFresh and orderIfMissing and not handler.MissingFromServer(itemID, size):
            if (itemID, size, handler) in self.currentlyFetching:
                self.currentlyFetching[itemID, size, handler].append([sprite, callback])
            else:
                self.imageServerQueue[itemID, size, handler].append([sprite, callback])
            if len(self.imageServerQueue) > self.fetchingFromImageServer and self.fetchingFromImageServer < MAX_PORTRAIT_THREADS:
                self.fetchingFromImageServer += 1
                uthread.pool('photo::FetchRemoteImages', self.__FetchFromImageServer)
        elif handler.MissingFromServer(itemID, size) and path is None:
            return defaultIcon
        if isFresh:
            return path
        if path is not None:
            resolvedPath = blue.paths.ResolvePath(handler.GetCachePath(itemID, size))
            if os.path.exists(resolvedPath):
                return path
        return defaultIcon

    def __FetchFromImageServer(self):
        self.LogInfo('Starting a image server thread')
        try:
            while len(self.imageServerQueue) > 0:
                (itemID, size, handler), orders = self.imageServerQueue.popitem()
                image = handler.GetImage(itemID, size)
                self.currentlyFetching[itemID, size, handler] = []
                if image is None:
                    continue
                orders += self.currentlyFetching.pop((itemID, size, handler))
                for sprite, callback in orders:
                    if callback:
                        sm.ScatterEvent(callback, itemID, size)
                    elif sprite is not None:
                        try:
                            sprite.LoadTexture(image)
                        except:
                            log.LogException('Error adding portrait to sprite')
                            sys.exc_clear()

        finally:
            self.fetchingFromImageServer -= 1

    def AddPortrait(self, portraitPath, charID):
        self.LogInfo('Adding portrait of', charID, 'from path', portraitPath)
        try:
            shutil.copy2(portraitPath, blue.paths.ResolvePathForWriting(u'cache:/Pictures/Characters/%s_%s.jpg' % (charID, DEFAULT_PORTRAIT_SIZE)))
        except WindowsError as e:
            log.LogTraceback('Failed to copy default size character image')
            self.LogError(e, 'Failed to copy default size character image')

        try:
            shutil.copy2(portraitPath, blue.paths.ResolvePathForWriting(u'cache:/Pictures/Characters/%s_%s.jpg' % (charID, 256)))
        except WindowsError as e:
            log.LogTraceback('Failed to copy 256 px character image')
            self.LogError(e, 'Failed to copy 256 px character image')

        portraitCachePath = 'cache:/Pictures/Characters/%s_%s.jpg' % (charID, DEFAULT_PORTRAIT_SIZE)
        res = blue.resMan.GetResource(portraitCachePath, 'atlas')
        res.Reload()
        portraitCachePath_256 = 'cache:/Pictures/Characters/%s_%s.jpg' % (charID, 256)
        res = blue.resMan.GetResource(portraitCachePath_256, 'atlas')
        res.Reload()
        self.pendingPortraitGeneration = settings.user.ui.Get('pendingPortraitGeneration', set())
        self.pendingPortraitGeneration.add(charID)
        settings.user.ui.Set('pendingPortraitGeneration', self.pendingPortraitGeneration)
        if self.portraits is not None:
            self.portraits.missingImages.pop((charID, DEFAULT_PORTRAIT_SIZE), None)
            self.portraits.missingImages.pop((charID, 256), None)
            self.portraits.AddToWatchList(charID, self.PortraitDownloaded)

    def _RemovePathFromNotAvailList(self, cachename):
        try:
            del self.notavail[cachename]
            self.LogInfo('Deleted ', cachename, ' from not avail list')
        except:
            self.LogInfo(cachename, ' was not in the not avail list')

    def Do2DMap(self, sprite, ids, idLevel, drawLevel, size = 256):
        ssmap = Map2D()
        ssmap.Draw(ids, idLevel, drawLevel, size, sprite)

    def GetIconByType(self, sprite, typeID, itemID = None, size = None, ignoreSize = False, isCopy = False):
        if typeID is None or not evetypes.Exists(typeID):
            return
        actSize = size or 64
        categoryID = evetypes.GetCategoryID(typeID)
        groupID = evetypes.GetGroupID(typeID)
        blueprint = None
        if categoryID == const.categoryBlueprint:
            if groupID in REACTION_GROUPS:
                blueprint = IconStyle.BP_REACTION
            elif isCopy:
                blueprint = IconStyle.BP_COPY
            else:
                blueprint = IconStyle.BP_ORIGINAL
        elif categoryID == const.categoryInfantry:
            blueprint = IconStyle.BP_DUST
        elif categoryID == const.categoryAncientRelic:
            blueprint = IconStyle.BP_RELIC
        if itemID and groupID in (const.groupRegion, const.groupConstellation, const.groupSolarSystem):
            if not (idCheckers.IsSolarSystem(itemID) or idCheckers.IsConstellation(itemID) or idCheckers.IsRegion(itemID)):
                log.LogError('Not valid itemID for 2D map, itemID: ', itemID, ', typeID: ', typeID)
                log.LogTraceback()
            level = [const.groupRegion, const.groupConstellation, const.groupSolarSystem].index(groupID) + 1
            return self.Do2DMap(sprite, [itemID], level, level + 1, actSize)
        if evetypes.IsRenderable(typeID):
            if groupID == const.groupCharacter:
                return self.GetPortrait(itemID, actSize, sprite)
            else:
                return self.OrderByTypeID([[typeID,
                  sprite,
                  actSize,
                  itemID,
                  blueprint]])
        elif categoryID == const.categoryShipSkin:
            self.DoSkinLicenseIcon(typeID, sprite)
        else:
            iconInfo = inventorycommon.typeHelpers.GetIcon(typeID)
            if iconInfo and iconInfo.iconFile:
                icon = iconInfo.iconFile.strip()
                if icon:
                    if blueprint:
                        return self.DoBlueprint(sprite, typeID, size=actSize, blueprint=blueprint)
                    else:
                        return sprite.LoadIcon(icon, ignoreSize=ignoreSize)

    def DoSkinLicenseIcon(self, typeID, sprite):
        if not sprite.texture:
            return
        try:
            skin = sm.GetService('cosmeticsSvc').GetSkinByLicenseType(typeID)
            sprite.texture.resPath = skin.iconTexturePath
        except KeyError:
            sprite.texture.resPath = 'res:/UI/Texture/classes/skins/icons/default.png'

    def OrderByTypeID(self, orderlist):
        for each in orderlist:
            if len(each) == 4:
                typeID, wnd, size, itemID = each
                blueprint = None
            else:
                typeID, wnd, size, itemID, blueprint = each
            if uicore.desktop.dpiScaling > 1.0:
                size = size * 2
            if wnd is None or wnd.destroyed:
                orderlist.remove(each)
                continue
            foundPath = self.ExistsInCacheOrRenders(typeID, size, itemID, blueprint)
            if foundPath:
                wnd.LoadTexture(foundPath)
                orderlist.remove(each)
                continue
            wnd.LoadTexture('res:/UI/Texture/notavailable.dds')

        for each in orderlist:
            self.byTypeIDQue.append(each)

        if not self.byTypeID_IsRunning:
            uthread.pool('photo::OrderByTypeID', self.ProduceTypeIDs)
            self.byTypeID_IsRunning = 1

    def ExistsInCacheOrRenders(self, typeID, size, itemID, blueprint):
        graphicID = evetypes.GetGraphicID(typeID)
        if evetypes.GetGroupID(typeID) == const.groupStation:
            npcStation = cfg.mapSolarSystemContentCache.npcStations.get(itemID, None)
            if npcStation:
                graphicID = npcStation.graphicID
        renderPath = GetRenderPath(graphicID, size, blueprint)
        if blue.paths.exists(renderPath):
            return renderPath
        cachePath = GetCachePath(typeID, graphicID, size, itemID, blueprint)
        if self.CheckAvail(cachePath) is not None:
            return cachePath

    def ProduceTypeIDs(self):
        while self.byTypeIDQue:
            for order in self.byTypeIDQue:
                if len(order) == 4:
                    typeID, wnd, size, itemID = order
                    blueprint = None
                else:
                    typeID, wnd, size, itemID, blueprint = order
                if wnd is None or wnd.destroyed:
                    self.byTypeIDQue.remove(order)
                    continue
                if uicore.desktop.dpiScaling > 1.0:
                    size = size * 2
                foundPath = self.ExistsInCacheOrRenders(typeID, size, itemID, blueprint)
                if foundPath:
                    wnd.LoadTexture(foundPath)
                    self.byTypeIDQue.remove(order)
                    continue
                else:
                    self.LogError('The type', typeID, 'is missing a pre rendered icon!')
                    photopath = NOT_AVAILABLE_PATH
                if wnd is None or wnd.destroyed:
                    self.byTypeIDQue.remove(order)
                    continue
                if wnd.texture and wnd.texture.resPath != NOT_AVAILABLE_PATH:
                    self.byTypeIDQue.remove(order)
                    continue
                wnd.LoadTexture(photopath)
                if photopath == NOT_AVAILABLE_PATH:
                    self.byTypeIDQue.remove(order)
                    continue
                self.byTypeIDQue.remove(order)
                blue.pyos.synchro.Yield()

        self.byTypeID_IsRunning = 0

    def GetPlanetScene(self):
        scenepath = sm.GetService('sceneManager').GetScene()
        scene = trinity.Load(scenepath)
        scene.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
        if scene.backgroundEffect is not None:
            for node in scene.backgroundEffect.resources.Find('trinity.TriTextureParameter'):
                if node.name == 'NebulaMap':
                    node.resourcePath = scene.envMap1ResPath

        scene.backgroundRenderingEnabled = True
        return scene

    def GetImageServerURL(self, clientCfgValue = 'imageserverurl', defaultServer = None):
        imageServer = sm.GetService('machoNet').GetGlobalConfig().get(clientCfgValue)
        if imageServer is None:
            imageServer = defaultServer
        return imageServer

    def FindBestPortraitSize(self, size):
        for available_size in PORTRAIT_SIZES:
            if available_size >= size:
                return available_size

        return PORTRAIT_SIZES[-1]


NOT_MODIFIED = 304
TEMP_REDIRECT = 302
MAX_ATTEMPTS = 4
REQUEST_TIMEOUT_SEC = 10

class RemoteImageCacher(object):

    def __init__(self, cacheItem, logger, suffix, imageServer, machoNet):
        self.initialized = False
        self.LogInfo = logger.LogInfo
        self.LogWarn = logger.LogWarn
        self.LogError = logger.LogError
        self.LogInfo('Initializing Remote Image service for', cacheItem)
        self._machoNet = machoNet
        self._missingImagesRetryDelay = IMAGE_SERVER_MISSING_IMAGE_RETRY_DELAY_IN_SECONDS_DEFAULT
        add_global_config_callback(self._OnRefreshGlobalConfig)
        self.requestSession = requests.session()
        self.cacheItem = cacheItem
        self.cacheBasePath = 'cache:/Pictures/%ss/' % self.cacheItem
        self.cacheFile = '%s_%s' + suffix
        self.missingImages = {}
        self.watchList = {}
        if imageServer == '':
            imageServer = 'http://xxx.dev.image/'
        if imageServer is None:
            self.LogError('RemoteImageCacher can not operate without a server URL!', imageServer)
            return
        imageServer = imageServer.strip().encode('ascii')
        self.imageUri = imageServer
        if not imageServer.endswith('/'):
            self.imageUri += '/'
        self.imageUri += cacheItem + '/%s_%s' + suffix
        self.LogInfo('RemoteImageCacher initialized with imageUri', self.imageUri)
        self.initialized = True

    def Initialized(self):
        return self.initialized

    def _OnRefreshGlobalConfig(self):
        self._missingImagesRetryDelay = GetImageServerMissingImageRetryDelay(machoNet=self._machoNet)

    def AddToWatchList(self, itemID, callback):
        self.watchList[itemID] = callback

    def GetCachePath(self, itemID, size, createPath = False):
        basePath = self.cacheBasePath
        if self.cacheItem == 'Character' and size in (32, 64):
            basePath = '%sChat/%s/' % (self.cacheBasePath, itemID % 100)
        if createPath:
            pathToFile = blue.paths.ResolvePath(basePath)
            if not os.path.exists(pathToFile):
                os.makedirs(pathToFile)
        return basePath + self.cacheFile % (itemID, size)

    def GetCachedImage(self, itemID, size):
        if not self.Initialized():
            return (None, False)
        cachePath = self.GetCachePath(itemID, size)
        fileSystemPath = blue.paths.ResolvePath(cachePath)
        if os.path.exists(fileSystemPath):
            return (cachePath, self.__IsFresh(cachePath))
        return (None, False)

    def MissingFromServer(self, itemID, size):
        lastTry = self.missingImages.get((itemID, size), None)
        if lastTry is not None:
            if time.time() - lastTry > self._missingImagesRetryDelay:
                return False
            return True
        return False

    def GetImage(self, itemID, size, forceUpdate = False):
        if not self.Initialized() or self.MissingFromServer(itemID, size) and not forceUpdate:
            return
        lockID = str(itemID) + '_' + str(size)
        uthread.Lock(self, lockID)
        try:
            try:
                cachePath = self.GetCachePath(itemID, size, createPath=True)
            except Exception as e:
                self.LogError('Failed to get image cache folder', repr(e))
                self.initialized = False
                return

            cacheFile = blue.paths.ResolvePath(cachePath)
            lastModified = self.GetLastModified(cachePath)
            if forceUpdate or not self.__IsFresh(cachePath):
                self.LogInfo('Get image for', itemID, 'is fetching/refreshing image. Forced = ', forceUpdate)
                image, headerLastModifiedTime = self.__GetImageFromUrl(itemID, size, lastModified)
                if image is None:
                    self.LogInfo('No image found for', itemID, 'adding to missing images')
                    if self._missingImagesRetryDelay > 0:
                        self.missingImages[itemID, size] = time.time()
                    return
                if (itemID, size) in self.missingImages:
                    self.missingImages.pop((itemID, size), None)
                if image == NOT_MODIFIED:
                    self.LogInfo('Image has not been modified, updating cached image')
                    self.UpdateLastCheckedTime(cacheFile)
                else:
                    resfile = blue.classes.CreateInstance('blue.ResFile')
                    try:
                        if not resfile.Open(cachePath, 0):
                            try:
                                resfile.Create(cachePath)
                            except Exception as e:
                                self.LogError('Failed to get image cache folder', repr(e))
                                self.initialized = False
                                return

                        resfile.Write(image)
                        resfile.Close()
                        self.InvalidateResManagerForResource(cachePath)
                        self.FetchedCacheFile(cachePath, headerLastModifiedTime)
                    except Exception as e:
                        self.LogError('Failed to update cached image', repr(e))
                        return

                    if itemID in self.watchList:
                        self.LogInfo('RemoteImageCached removed item ', itemID, 'was an item in the watchlist.')
                        self.watchList[itemID](itemID)
                        del self.watchList[itemID]
        finally:
            uthread.UnLock(self, lockID)

        return cachePath

    def __GetImageFromUrl(self, itemID, size, lastModified):
        if not self.Initialized():
            return (None, None)
        url = (self.imageUri % (itemID, size)).strip().encode('ascii')
        headers = {}
        if lastModified:
            cacheTime = datetime.datetime.utcfromtimestamp(lastModified)
            cacheStamp = cacheTime.strftime('%a, %d %b %Y %H:%M:%S GMT')
            headers['If-Modified-Since'] = cacheStamp
            self.LogInfo('adding If-Modified-Since header for', cacheStamp)
        response = None
        exc = None
        image = None
        headerLastModifiedTime = None
        for attempt in range(MAX_ATTEMPTS):
            try:
                response = self.requestSession.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SEC, allow_redirects=False)
                break
            except Exception as e:
                exc = e
                if attempt + 1 < MAX_ATTEMPTS:
                    backoffSeconds = 2 ** attempt
                    logger.warn('Retrying requesting image for url: %s. Sleeping for %s seconds. Attempts done so far: (%s/%s). Exception: %s', url, backoffSeconds, attempt + 1, MAX_ATTEMPTS, exc)
                    blue.pyos.synchro.SleepWallclock(backoffSeconds * 1000)

        else:
            if blue.pyos.packaged:
                logger.exception('Retries exhausted for requesting an image for url: %s. Total attempts: %s. Last ex: %s.', url, MAX_ATTEMPTS, exc)
            else:
                logger.warn('Retries exhausted for requesting an image for url: %s. Total attempts: %s. Last ex: %s.', url, MAX_ATTEMPTS, exc)

        if response:
            contentType = response.headers.get('Content-Type', None)
            if response.status_code == NOT_MODIFIED:
                image = NOT_MODIFIED
                self.LogInfo('Not Modified', url, 'since', lastModified, time.ctime(lastModified))
            elif response.status_code == TEMP_REDIRECT:
                self.LogInfo('Temp Redirect while getting image', url)
            elif not contentType or not contentType.startswith('image/'):
                logger.exception('Did not receive image content type for url: %s. Response status code: %s' % (url, response.status_code))
            else:
                image = response.content
                rLastModified = response.headers.get('Last-Modified', None)
                if rLastModified:
                    headerLastModifiedTime = self.__FormatLastModifiedHeader(rLastModified)
                if not headerLastModifiedTime:
                    headerLastModifiedTime = time.time()
        return (image, headerLastModifiedTime)

    @staticmethod
    def __FormatLastModifiedHeader(lastModified):
        try:
            time_tuple = rfc822.parsedate(lastModified)
            return time.mktime(time_tuple)
        except Exception as e:
            log.LogException('Photo - Exception formatting last modified header', str(e))

    def GetLastModified(self, cachePath):
        filepath = blue.paths.ResolvePath(cachePath)
        if os.path.exists(filepath):
            return os.path.getmtime(filepath)

    def GetLastChecked(self, cachePath):
        return self.GetLastModified(cachePath)

    def InvalidateResManagerForResource(self, cacheFile):
        try:
            self.LogInfo('Reloading blue res', cacheFile)
            res = blue.resMan.GetResource(str(cacheFile), 'atlas')
            if res:
                res.Reload()
        except SystemError:
            sys.exc_clear()

    def FetchedCacheFile(self, cacheFile, headerLastModifiedTime):
        pass

    def UpdateLastCheckedTime(self, cacheFile):
        self.UpdateFileTimeStamp(cacheFile, None)

    def UpdateFileTimeStamp(self, cacheFile, timeStamp):
        try:
            with file(cacheFile, 'a'):
                os.utime(cacheFile, timeStamp)
        except Exception as e:
            pass

    def __IsFresh(self, cachePath):
        lastModified = self.GetLastChecked(cachePath)
        if lastModified is None:
            return False
        delta = time.time() - lastModified
        return delta < MAX_CACHE_AGE

    def RemoveFromCache(self, itemID, size):
        cachePath = self.GetCachePath(itemID, size)
        filepath = blue.paths.ResolvePath(cachePath)
        if os.path.exists(filepath):
            os.remove(filepath)
