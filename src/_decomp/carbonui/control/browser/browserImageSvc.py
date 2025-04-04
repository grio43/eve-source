#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\browser\browserImageSvc.py
import os
import sys
import blue
import trinity
import uthread
from carbon.common.script.sys.service import Service
from carbonui.control.browser import browserutil
from carbonui.util.various_unsorted import GetBuffersize

class BrowserImage(Service):
    __guid__ = 'svc.browserImage'
    __exportedcalls__ = {}
    __startupdependencies__ = ['imageCache']

    def __init__(self):
        self._urlloading = {}
        super(BrowserImage, self).__init__()

    def GetTextureInfoFromURL(self, path, currentURL = None, fromWhere = None):
        if path.endswith('.blue'):
            return self._GetPic_blue(path)
        fullPath = browserutil.ParseURL(path, currentURL)[0]
        cacheData = self.imageCache.GetFromCache(fullPath)
        if not cacheData:
            cacheData = self.GetTextureFromURL(path, currentURL, fromWhere=fromWhere, sizeonly=1)
        if cacheData and os.path.exists(cacheData[0].replace('cache:/', blue.paths.ResolvePath(u'cache:/'))):
            return cacheData

    def GetTextureFromURL(self, path, currentURL = None, ignoreCache = 0, dontcache = 0, fromWhere = None, sizeonly = 0, retry = 1):
        if path.endswith('.blue'):
            return self._GetPic_blue(path)
        dev = trinity.device
        fullPath = browserutil.ParseURL(path, currentURL)[0]
        if path.startswith('res:'):
            try:
                bmp = trinity.Tr2HostBitmap()
                bmp.CreateFromFile(path)
                w, h = bmp.width, bmp.height
                bw, bh = GetBuffersize(w), GetBuffersize(h)
                if sizeonly:
                    return (path,
                     w,
                     h,
                     bw,
                     bh)
                return self._ReturnTexture(path, w, h, bw, bh)
            except:
                self.LogError('Failed to load image', path)
                if self._urlloading.has_key(fullPath):
                    del self.urlloading[fullPath]
                sys.exc_clear()
                return self._ErrorPic(sizeonly)

        if ignoreCache:
            self.imageCache.InvalidateImage(fullPath)
        while self._urlloading.has_key(fullPath):
            blue.pyos.BeNice()

        if not dontcache:
            cacheData = self.imageCache.GetFromCache(fullPath)
            if cacheData and os.path.exists(cacheData[0].replace('cache:/', blue.paths.ResolvePath(u'cache:/'))):
                if sizeonly:
                    return cacheData
                return self._ReturnTexture(*cacheData)
        try:
            self._urlloading[fullPath] = 1
            ret = browserutil.GetStringFromURL(fullPath)
            cacheID = int(str(blue.os.GetWallclockTime()) + str(uthread.uniqueId() or uthread.uniqueId()))
            imagestream = ret.read()
            ext = None
            if 'content-type' in ret.headers.keys() and ret.headers['content-type'].startswith('image/'):
                ext = ret.headers['content-type'][6:]
            if ext == None or ext == 'png':
                header = imagestream[:16]
                for sig, sext in [('PNG', 'PNG'), ('JFI', 'JPEG'), ('BM8', 'BMP')]:
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
                bmp = trinity.Tr2HostBitmap()
                bmp.CreateFromFile(filename)
                w, h = bmp.width, bmp.height
                bw, bh = GetBuffersize(w), GetBuffersize(h)
                cachePath = 'cache:/Browser/Img/%s.%s' % (cacheID, ext)
                if 'pragma' not in ret.headers.keys() or ret.headers['Pragma'].find('no-cache') == -1:
                    self.imageCache.Cache(fullPath, (cachePath,
                     w,
                     h,
                     bw,
                     bh))
                del self._urlloading[fullPath]
                if sizeonly:
                    return (cachePath,
                     w,
                     h,
                     bw,
                     bh)
                return self._ReturnTexture(cachePath, w, h, bw, bh)
            del self._urlloading[fullPath]
            return self._ErrorPic(sizeonly)
        except Exception as e:
            if retry:
                sys.exc_clear()
                if fullPath in self._urlloading:
                    del self._urlloading[fullPath]
                return self.GetTextureFromURL(path, currentURL, ignoreCache, dontcache, fromWhere, sizeonly, 0)
            self.LogError(type(e), 'on line', sys.exc_traceback.tb_lineno, 'in browserImage service')
            self.LogError(e, 'Failed to load image', path)
            if fullPath in self._urlloading:
                del self._urlloading[fullPath]
            sys.exc_clear()
            return self._ErrorPic(sizeonly)

    def _ErrorPic(self, sizeonly = 0):
        if sizeonly:
            return ('res:/uicore/texture/none.dds', 32, 32, 32, 32)
        return self._ReturnTexture('res:/uicore/texture/none.dds', 32, 32, 32, 32)

    def _ReturnTexture(self, path, width, height, bufferwidth, bufferheight):
        tex = trinity.Tr2Sprite2dTexture()
        tex.resPath = str(path)
        return (tex, width, height)

    def _GetPic_blue(self, path):
        tex = blue.resMan.LoadObject(path)
        w = int(tex.pixelBuffer.width * (tex.scaling.x / (tex.texCoordIndex * 2 or 1))) or 32
        h = int(tex.pixelBuffer.height * (tex.scaling.y / (tex.texCoordIndex * 2 or 1))) or 32
        return (tex, w, h)
