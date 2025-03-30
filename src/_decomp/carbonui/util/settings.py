#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\settings.py
import blue
import log
import os
import signals
import types
import yaml
import traceback
import uthread
import uthread2
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.util.settingsYamlLoader import UnicodeConvertingYamlLoader
from carbonui.util.bunch import Bunch
from carbonui.util.various_unsorted import GetAttrs
from carbonui.util import defaultsetting
from copy import deepcopy

class SettingSection():

    def __init__(self, name, filepath, autoStoreInterval, service):
        self._name = name
        self._filepath = filepath
        self._dirty = False
        self._service = service
        self.datastore = {}
        self.timeoutTimer = None
        self._scatterSettingsChangedThreads = {}
        self._messenger = signals.Messenger()
        self.LoadFromFile(filepath, autoStoreInterval)

    def __str__(self):
        return '%s\nSetting section, %s; holding %s groups.\nFileLocation: %s' % ('-' * 60,
         self._name,
         len(self.datastore),
         repr(self._filepath))

    def __repr__(self):
        s = self.__str__() + '\n'
        for groupName, groupValue in self.datastore.iteritems():
            s += '%s:\n' % groupName
            for settingName, settingValue in groupValue.iteritems():
                s += '    %s: %s\n' % (settingName, settingValue)

        return s

    class Group(dict):

        def __init__(self, name, section):
            self.__dict__['name'] = name
            self.__dict__['section'] = section

        def __getattr__(self, attrName):
            if hasattr(self, 'section'):
                return self.section.Get(self.name, attrName)

        def Get(self, attrName, defValue = None):
            retVal = self.__getattr__(attrName)
            if retVal is None:
                return defValue
            return retVal

        def __setattr__(self, attrName, value):
            if hasattr(self, 'section'):
                self.section.Set(self.name, attrName, value)

        Set = __setattr__

        def Release(self):
            self.section = None

        def HasKey(self, attrName):
            return self.section.HasKey(self.name, attrName)

        def Delete(self, attrName):
            self.section.Delete(self.name, attrName)

        def GetValues(self):
            return self.section.GetValues(self.name)

    def LoadFromFile(self, filepath, autoStoreInterval):
        data = None
        try:
            fn = blue.paths.ResolvePath(filepath)
            data = blue.AtomicFileRead(fn)
        except:
            pass

        if data:
            try:
                self.datastore = blue.marshal.Load(data)
                for k, v in self.datastore.iteritems():
                    self.CreateGroup(k)

            except StandardError:
                log.LogException('Error loading settings data file')

        self.timeoutTimer = AutoTimer(autoStoreInterval * 1000, self.WriteToDisk)

    def GetValues(self, groupName):
        return self.datastore[groupName]

    def Get(self, groupName, settingName):
        if groupName not in self.datastore:
            self.CreateGroup(groupName)
        if settingName in self.datastore[groupName]:
            value = self.datastore[groupName][settingName][1]
            self.datastore[groupName][settingName] = (blue.os.GetWallclockTime(), value)
            return value
        else:
            n = settingName
            if type(n) == types.UnicodeType:
                n = n.encode('UTF-8')
            return GetAttrs(defaultsetting, self._name, groupName, n)

    def HasKey(self, groupName, settingName):
        return settingName in self.datastore[groupName]

    def Delete(self, groupName, settingName):
        if self.HasKey(groupName, settingName):
            del self.datastore[groupName][settingName]
            self._ScatterSettingsChanged(groupName, settingName)

    def Set(self, groupName, settingName, value):
        if groupName not in self.datastore:
            self.CreateGroup(groupName)
        self.datastore[groupName][settingName] = (blue.os.GetWallclockTime(), value)
        self.FlagDirty()
        self._ScatterSettingsChanged(groupName, settingName)

    def Remove(self, groupName, settingName = None):
        if groupName in self.datastore:
            group = self.datastore[groupName]
            if settingName:
                if settingName in group:
                    del group[settingName]
            else:
                del self.datastore[groupName]
            self.FlagDirty()

    def HasGroup(self, groupName):
        return groupName in self.__dict__ and groupName in self.datastore

    def DuplicateGroup(self, oldGroupName, newGroupName):
        if not self.HasGroup(oldGroupName) or self.HasGroup(newGroupName):
            return
        self.CreateGroup(newGroupName)
        self.datastore[newGroupName] = deepcopy(self.datastore[oldGroupName])
        self.FlagDirty()

    def RenameGroup(self, oldGroupName, newGroupName):
        if not self.HasGroup(oldGroupName):
            return
        self.CreateGroup(newGroupName)
        self.datastore[newGroupName] = deepcopy(self.datastore[oldGroupName])
        del self.__dict__[oldGroupName]
        del self.datastore[oldGroupName]
        self.FlagDirty()

    def RemoveGroup(self, groupName):
        if not self.HasGroup(groupName):
            return
        del self.__dict__[groupName]
        del self.datastore[groupName]
        self.FlagDirty()

    def ClearGroup(self, groupName):
        if not self.HasGroup(groupName):
            return
        self.datastore[groupName] = {}
        self.FlagDirty()

    def CreateGroup(self, groupName):
        if groupName not in self.__dict__:
            self.__dict__[groupName] = self.Group(groupName, self)
        if groupName not in self.datastore:
            self.datastore[groupName] = {}

    def FlagDirty(self):
        self._dirty = True

    def WriteToDiskImmediate(self):
        self.WriteToDisk()

    def WriteToDisk(self):
        if self._dirty:
            self._dirty = False
            fn = blue.paths.ResolvePathForWriting(self._filepath)
            try:
                if os.access(fn, os.F_OK) and not os.access(fn, os.W_OK):
                    os.chmod(fn, 438)
                k = blue.marshal.Save(self.datastore)
                blue.AtomicFileWrite(fn, k)
            except Exception as e:
                log.LogError('Failed writing to disk', str(self), '-', repr(e))

    def Unload(self):
        self.timeoutTimer = None
        self.FlushOldEntries()
        self.WriteToDisk()

    def Save(self):
        self.FlushOldEntries()
        self.WriteToDisk()

    def FlushOldEntries(self):
        lastModified = blue.os.GetWallclockTime() - const.WEEK * 6
        for k, v in self.datastore.iteritems():
            for key in v.keys():
                if v[key][0] <= lastModified:
                    del v[key]

        self.FlagDirty()

    def SetDatastore(self, datastore):
        self.datastore = datastore

    def GetDatastore(self):
        return self.datastore

    def KillTimer(self):
        if self.timeoutTimer is not None:
            self.timeoutTimer.KillTimer()
            self.timeoutTimer = None

    def Subscribe(self, groupName, settingName, handler):
        self._messenger.SubscribeToMessage(u'{}.{}'.format(groupName, settingName), handler)

    def Unsubscribe(self, groupName, settingName, handler):
        self._messenger.UnsubscribeFromMessage(u'{}.{}'.format(groupName, settingName), handler)

    def _ScatterSettingsChanged(self, groupName, settingName):
        self._messenger.SendMessage(u'{}.{}'.format(groupName, settingName))
        settingsID = (groupName, settingName)
        if settingsID not in self._scatterSettingsChangedThreads:
            self._scatterSettingsChangedThreads[settingsID] = uthread2.start_tasklet(self._ScatterSettingsChangedThread, groupName, settingName)

    def _ScatterSettingsChangedThread(self, groupName, settingName):
        uthread2.Sleep(0.1)
        self._scatterSettingsChangedThreads.pop((groupName, settingName), None)
        sm.ScatterEvent('OnClientSettingsChanged', self._name, groupName, settingName)


class YAMLSettingSection(SettingSection):

    def __init__(self, name, filepath, autoStoreInterval, service):
        SettingSection.__init__(self, name, filepath, autoStoreInterval, service)

    def LoadFromFile(self, filepath, autoStoreInterval):
        data = None
        try:
            fn = blue.paths.ResolvePath(filepath)
            data = blue.AtomicFileRead(fn)
        except:
            pass

        if data:
            try:
                self.datastore = yaml.load(data, Loader=UnicodeConvertingYamlLoader)
                for k, v in self.datastore.iteritems():
                    self.CreateGroup(k)

            except:
                log.LogError('Error loading settings data file -- ', traceback.format_exc())

        self.timeoutTimer = AutoTimer(autoStoreInterval * 1000, self.WriteToDisk)

    def WriteToDisk(self):
        uthread.new(self._WriterThreadFunc)

    def WriteToDiskImmediate(self):
        self._WriterThreadFunc()

    def _WriterThreadFunc(self):
        if self._dirty:
            self._dirty = False
            fn = blue.paths.ResolvePathForWriting(self._filepath)
            try:
                if os.access(fn, os.F_OK) and not os.access(fn, os.W_OK):
                    os.chmod(fn, 438)
                k = yaml.dump(self.datastore, Dumper=yaml.CSafeDumper)
                blue.AtomicFileWrite(fn, k)
            except Exception as e:
                log.LogError('Failed writing to disk', str(self), '-', repr(e))


def LoadBaseSettings():
    import __builtin__
    if not hasattr(__builtin__, 'settings'):
        __builtin__.settings = Bunch()
    sections = (('user', session.userid, 'dat'), ('char', session.charid, 'dat'), ('public', None, 'yaml'))

    def _LoadSettingsIntoBuiltins(sectionName, identifier, settingsClass, extension):
        key = '%s%s' % (sectionName, identifier)
        filePath = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', extension))
        section = settingsClass(sectionName, filePath, 62, service=None)
        __builtin__.settings.Set(sectionName, section)

    for sectionName, identifier, format in sections:
        _LoadSettingsIntoBuiltins(sectionName, identifier, SettingSection, 'dat')

    settings.public.CreateGroup('generic')
    settings.public.CreateGroup('device')
    settings.public.CreateGroup('ui')
    settings.public.CreateGroup('audio')
    settings.user.CreateGroup('tabgroups')
    settings.user.CreateGroup('windows')
    settings.user.CreateGroup('suppress')
    settings.user.CreateGroup('ui')
    settings.user.CreateGroup('cmd')
    settings.user.CreateGroup('localization')
    settings.char.CreateGroup('windows')
    settings.char.CreateGroup('ui')
    settings.char.CreateGroup('zaction')
