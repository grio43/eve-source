#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\browser\imageCacheSvc.py
import os.path
import sys
import blue
from carbon.common.script.sys.service import Service
from carbonui.util.settings import SettingSection

class ImageCache(Service):
    __guid__ = 'svc.imageCache'

    def Run(self, *etc):
        super(ImageCache, self).Run(*etc)
        self.imgindex = None
        paths = [blue.paths.ResolvePath(u'cache:/'), blue.paths.ResolvePathForWriting(u'cache:/Browser'), blue.paths.ResolvePathForWriting(u'cache:/Browser/Img')]
        for path in paths:
            try:
                os.makedirs(path)
            except OSError as e:
                sys.exc_clear()

        self.Load()

    def Stop(self, *etc):
        super(ImageCache, self).Stop(*etc)
        self.Save()

    def GetFromCache(self, cacheID):
        if self.imgindex is None:
            self.Load()
        f = self.imgindex.img.Get(cacheID, None)
        if f:
            if os.path.exists(f[0].replace('cache:/', blue.paths.ResolvePath(u'cache:/'))):
                return f
            self.ClearCache(cacheID)

    def Cache(self, cacheID, cacheData, fromWhere = None):
        if not self.imgindex:
            self.Load()
        self.ClearCache(cacheID)
        self.imgindex.img.Set(cacheID, cacheData)

    def ClearCache(self, cacheID):
        if not self.imgindex:
            self.Load()
        self.imgindex.img.Delete(cacheID)

    def InvalidateImage(self, url):
        self.CheckForIndexFile()
        self.ClearCache(url)

    def Load(self):
        if self.imgindex:
            self.imgindex.Unload()
            self.imgindex = None
        self.imgindex = SettingSection('cache', blue.paths.ResolvePathForWriting(u'cache:/Browser/Img/index.dat'), 62, service=self)
        self.imgindex.CreateGroup('img')
        cachefiles = [ self.imgindex.img.Get(each, None)[0].replace('cache:/', blue.paths.ResolvePath(u'cache:/')) for each in self.imgindex.img.keys() ]
        for f in os.listdir(blue.paths.ResolvePathForWriting(u'cache:/Browser/Img')):
            if f == 'index.dat':
                continue
            f1 = blue.paths.ResolvePathForWriting(u'cache:/Browser/Img') + f
            if f1 not in cachefiles:
                try:
                    if os.path.exists(f1):
                        os.unlink(f1)
                except:
                    sys.exc_clear()

    def GetImgIndex(self):
        return self.imgindex

    def Save(self):
        self.imgindex.Unload()
        self.imgindex = None

    def CheckForIndexFile(self):
        file = blue.ResFile()
        if not file.Open(blue.paths.ResolvePathForWriting(u'cache:/Browser/Img/index.dat')):
            self.Load()
        else:
            file.Close()
