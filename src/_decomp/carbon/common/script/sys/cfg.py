#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\cfg.py
import sys
import types
import copy
import blue
import carbon.common.script.sys.basesession as base
import carbon.common.script.sys.crowset as crowset
import carbon.common.script.sys.service as service
import carbon.common.script.util.format as formatUtil
import fsdBuiltData.common.character as fsdchar
import localization
import log
import telemetry
import uthread
import utillib
from carbon.common.script.sys.row import Row as utilRow
from eve.common.script.sys import idCheckers
from carbon.common.lib import const
from eveprefs import boot
from utillib import strx
LogError = None
LogInfo = None
LogWarn = None
LogNotice = None

class DataConfig(service.CoreService):
    __guid__ = 'svc.dataconfig'
    __startupdependencies__ = []
    __servicename__ = 'dataconfig'
    __displayname__ = 'Data and Configuration Service'
    __exportedcalls__ = {'GetStartupData': [service.ROLE_SERVICE]}
    __notifyevents__ = ['OnCfgDataChanged', 'ProcessLoginProgressDone']

    def __init__(self):
        service.CoreService.__init__(self)
        self.cfg = None

    def _CreateConfig(self):
        return Config()

    def Run(self, memStream = None):
        global LogWarn
        global LogError
        global LogInfo
        global LogNotice
        service.CoreService.Run(self, memStream)
        self.state = service.SERVICE_START_PENDING
        import __builtin__
        if not hasattr(__builtin__, 'cfg'):
            __builtin__.cfg = self._CreateConfig()
            LogError = cfg.LogError = self.LogError
            LogInfo = cfg.LogInfo = self.LogInfo
            LogWarn = cfg.LogWarn = self.LogWarn
            LogNotice = cfg.LogNotice = self.LogNotice
            cfg.GetStartupData()
        self.state = service.SERVICE_RUNNING

    def Stop(self, memStream = None):
        tmp = cfg
        import __builtin__
        delattr(__builtin__, 'const')
        delattr(__builtin__, 'cfg')
        tmp.Release()
        service.CoreService.Stop(self)

    def ProcessLoginProgressDone(self):
        self.LogInfo('Login progress done, loading cfg data')
        cfg.LoadCfgData()

    def OnCfgDataChanged(self, what, data):
        uthread.new(cfg.OnCfgDataChanged, what, data)

    def DeleteRowTheHardWay(self, rs, keyIDs, keyCols):
        keyID, keyID2, keyID3 = keyIDs
        keyCol1, keyCol2, keyCol3 = keyCols
        delRow = None
        if keyCol3:
            for r in rs:
                if r[keyCol1] == keyID and r[keyCol2] == keyID2 and r[keyCol3] == keyID3:
                    delRow = r
                    break

        elif keyCol2:
            for r in rs:
                if r[keyCol1] == keyID and r[keyCol2] == keyID2:
                    delRow = r
                    break

        else:
            for r in rs:
                if r[keyCol1] == keyID:
                    delRow = r
                    break

        if delRow:
            rs.remove(delRow)

    def GetStartupData(self):
        self.LogInfo('Getting startup data')
        cfg.GetStartupData()


class ProxyServiceBroker():

    def ConnectToService(self, name):
        sess = base.GetServiceSession('cfg')
        return sess.ConnectToRemoteService(name)


class Config():
    __guid__ = 'util.config'

    def __init__(self):
        self.servicebroker = None
        self.client = 0
        self.server = 0
        self.totalLogonSteps = 10
        self.fmtMapping = {}
        self.fmtMapping[const.UE_DATETIME] = lambda value, value2: formatUtil.FmtDate(value)
        self.fmtMapping[const.UE_DATE] = lambda value, value2: formatUtil.FmtDate(value, 'ln')
        self.fmtMapping[const.UE_TIME] = lambda value, value2: formatUtil.FmtDate(value, 'nl')
        self.fmtMapping[const.UE_TIMESHRT] = lambda value, value2: formatUtil.FmtDate(value, 'ns')
        self.fmtMapping[const.UE_MSGARGS] = lambda value, value2: cfg.GetMessage(value[0], value[1]).text
        self.fmtMapping[const.UE_LOC] = lambda value, value2: self._GetLocalization(value, value2)
        self.fmtMapping[const.UE_MESSAGEID] = lambda value, value2: self._GetLocalizationByID(value, value2)
        self.fmtMapping[const.UE_LIST] = lambda value, value2: self._GetList(value, value2)

    def UpdateCfgData(self, data, object, guid):
        if guid == Recordset.__guid__:
            keyidx = object.keyidx or object.header.index(object.keycolumn)
            object.data[data[keyidx]] = data
        elif guid == crowset.CFilterRowset.__guid__:
            keyidx = object.columnName
            index = data[keyidx]
            if index in object:
                object[data[keyidx]].append(data)
            else:
                object[data[keyidx]] = [data]
        else:
            raise RuntimeError('Call to OnCfgDataChanged unsupported container type.')

    def OnCfgDataChanged(self, what, data):
        if not hasattr(self, what):
            raise RuntimeError('Call to OnCfgDataChanged with invalid container reference.')
        object = getattr(self, what)
        if not object:
            raise RuntimeError('Call to OnCfgDataChanged failed to get a valid container.')
        if type(object) == types.DictType:
            object[data[0]] = data[1]
            return
        if not hasattr(object, '__guid__'):
            raise RuntimeError('Call to OnCfgDataChanged for unknown container type.')
        guid = getattr(object, '__guid__')
        if not guid:
            raise RuntimeError('Call to OnCfgDataChanged failed to get container type.')
        self.UpdateCfgData(data, object, guid)
        sm.ScatterEvent('OnPostCfgDataChanged', what, data)

    def Release(self):
        self.messages = None
        self.LogError = None

    def GetConfigSvc(self):
        if not self.servicebroker:
            sess = base.GetServiceSession('cfg')
            if 'config' in sm.services or boot.role == 'server':
                config = sess.ConnectToService('config')
                self.servicebroker = sess
                self.server = 1
            elif boot.role == 'proxy':
                self.servicebroker = ProxyServiceBroker()
                self.client = 1
            else:
                self.servicebroker = sess.ConnectToService('connection')
                self.client = 1
        return self.servicebroker.ConnectToService('config')

    def GetSvc(self, serviceid):
        if not self.servicebroker:
            sess = base.GetServiceSession('cfg')
            self.servicebroker = sess
            self.server = 1
        return self.servicebroker.ConnectToService(serviceid)

    def GetStartupData(self):
        if boot.role != 'server':
            return
        self.AppGetStartupData()

    def AppGetStartupData(self):
        pass

    def ConvertData(self, src, dst):
        dst.data.clear()
        dst.header = src.columns
        keycol = src.columns.index(dst.keycolumn)
        for i in src:
            dst.data[i[keycol]] = i

    @telemetry.ZONE_METHOD
    def LoadCfgData(self):
        self.LogInfo('LoadCfgData')
        self.paperdollModifierLocations = fsdchar.GetModifierLocationRows()
        self.paperdollResources = fsdchar.GetResourceRows()
        self.paperdollSculptingLocations = fsdchar.GetSculptingLocationRows()
        self.paperdollColors = fsdchar.GetColorLocationRows()
        self.paperdollColorNames = fsdchar.GetColorNameRows()
        self.paperdollPortraitResources = fsdchar.GetPortraitResourceRows()

    def GetMessage(self, key, dict = None, onNotFound = 'return', onDictMissing = 'error'):
        if key not in self.messages:
            if onNotFound == 'return':
                return self.GetMessage('ErrMessageNotFound', {'msgid': key,
                 'args': dict})
            if onNotFound == 'raise':
                raise RuntimeError('ErrMessageNotFound', {'msgid': key,
                 'args': dict})
            else:
                if onNotFound == 'pass':
                    return
                raise RuntimeError('GetMessage: WTF', onNotFound)
        msg = self.messages[key]
        text, title, suppress = msg.messageText, None, 0
        if dict == -1:
            pass
        elif dict is not None:
            try:
                if dict is not None and dict != -1:
                    dict = self.__prepdict(dict)
                if text is not None:
                    text = text % dict
            except KeyError as e:
                if onNotFound == 'raise':
                    raise
                sys.exc_clear()
                return self.GetMessage('ErrMessageKeyError', {'msgid': key,
                 'text': msg.messageText,
                 'args': dict,
                 'err': strx(e)})

        elif onDictMissing == 'error':
            if text and text.find('%(') != -1:
                if onNotFound == 'raise':
                    raise RuntimeError('ErrMessageDictMissing', {'msgid': key,
                     'text': msg.messageText})
                return self.GetMessage('ErrMessageDictMissing', {'msgid': key,
                 'text': msg.messageText})
        if text is not None:
            ix = text.find('::')
            if ix != -1:
                title, text = text.split('::')
                suppress = 0
            else:
                ix = text.find(':s:')
                if ix != -1:
                    title, text = text.split(':s:')
                    suppress = 1
        else:
            text, title, suppress = (None, None, 0)
        return utillib.KeyVal(text=text, title=title, type=msg.dialogType, audio=msg.urlAudio, icon=msg.urlIcon, suppress=suppress)

    def _GetLocalization(self, key, keyArgs = None):
        if boot.role == 'server':
            if keyArgs is None:
                return key
            else:
                return key + ' - ' + str(keyArgs)
        else:
            if keyArgs is None:
                return localization.GetByLabel(key)
            for k, v in keyArgs.iteritems():
                if type(v) != types.TupleType:
                    continue
                value2 = None
                if len(v) >= 3:
                    value2 = v[2]
                keyArgs[k] = self.FormatConvert(v[0], v[1], value2)

            return localization.GetByLabel(key, **keyArgs)

    def _GetLocalizationByID(self, key, keyArgs = None):
        if boot.role == 'server':
            if keyArgs is None:
                return 'MessageID: ' + str(key)
            else:
                return 'MessageID: ' + str(key) + ' - ' + str(keyArgs)
        else:
            if keyArgs is None:
                return localization.GetByMessageID(key)
            for k, v in keyArgs.iteritems():
                if type(v) != types.TupleType:
                    continue
                value2 = None
                if len(v) >= 3:
                    value2 = v[2]
                keyArgs[k] = self.FormatConvert(v[0], v[1], value2)

            return localization.GetByMessageID(key, **keyArgs)

    def _GetList(self, fmtList, separator = None):
        results = []
        for each in fmtList:
            value2 = None
            if len(each) >= 3:
                value2 = each[2]
            results.append(self.FormatConvert(each[0], each[1], value2))

        if separator is not None:
            return separator.join(results)
        else:
            return localization.formatters.FormatGenericList(results)

    def __prepdict(self, dict):
        dict = copy.deepcopy(dict)
        for k, v in dict.iteritems():
            if type(v) != types.TupleType:
                continue
            value2 = None
            if len(v) >= 3:
                value2 = v[2]
            dict[k] = self.FormatConvert(v[0], v[1], value2)

        return dict

    __numberstrings__ = {1: 'one',
     2: 'two',
     3: 'three',
     4: 'four',
     5: 'five',
     6: 'six',
     7: 'seven',
     8: 'eight',
     9: 'nine',
     10: 'ten',
     11: 'eleven',
     12: 'twelve',
     13: 'thirteen',
     14: 'fourteen',
     15: 'fifteen',
     16: 'sixteen',
     17: 'seventeen',
     18: 'eighteen',
     19: 'nineteen',
     20: 'twenty',
     30: 'thirty',
     40: 'forty',
     50: 'fifty',
     60: 'sixty',
     70: 'seventy',
     80: 'eighty',
     90: 'ninety'}
    for each in range(19, 0, -1):
        __numberstrings__[each * 100] = __numberstrings__[each] + ' hundred'
        __numberstrings__[each * 1000] = __numberstrings__[each] + ' thousand'
        __numberstrings__[each * 100000] = __numberstrings__[each] + ' hundred thousand'
        __numberstrings__[each * 1000000] = __numberstrings__[each] + ' million'
        __numberstrings__[each * 1000000000] = __numberstrings__[each] + ' billion'

    def FormatConvert(self, formatType, value, value2 = None):
        if type(value) == types.TupleType:
            value2 = None
            if len(value) >= 3:
                value2 = value[2]
            value = self.FormatConvert(value[0], value[1], value2)
        if self.fmtMapping.has_key(formatType):
            return self.fmtMapping[formatType](value, value2)
        else:
            return 'INVALID FORMAT TYPE %s, value is %s' % (formatType, value)

    def Format(self, key, dict = None):
        msg = self.GetMessage(key, dict, onNotFound='raise')
        if msg.title:
            return '%s - %s' % (msg.title, msg.text)
        else:
            return msg.text


class Recordset():
    __guid__ = 'cfg.Recordset'

    def __init__(self, rowclass, keycolumn, dbfetcher = None, dbMultiFetcher = None, clientLocalFetcher = None):
        self.rowclass = rowclass
        self.dbfetcher = dbfetcher
        self.dbMultiFetcher = dbMultiFetcher
        if boot.role == 'client':
            self.clientLocalFetcher = clientLocalFetcher
        else:
            self.clientLocalFetcher = None
        self.header = []
        self.data = {}
        self.keyidx = None
        self.keycolumn = keycolumn
        self.locks = {}
        self.waitingKeys = set()
        self.knownLuzers = set([None])
        self.singlePrimeCount = 0
        self.singlePrimeTimestamp = 0
        if isinstance(self.dbfetcher, (list, tuple)):
            header, data = self.dbfetcher
            self.PopulateDataset(header, data)

    def PopulateDataset(self, header, data):
        self.header = header
        self.keyidx = self.header.index(self.keycolumn)
        self.__PopulateDataset(data)

    def GetKeyColumn(self):
        return self.keycolumn

    def GetLine(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        try:
            ret = '<Instance of Recordset.%s>\r\n' % (self.rowclass.__name__,)
            ret = ret + 'Key column: %s' % (self.keycolumn,)
            if len(self.header):
                ret = ret + ', Cache entries: %d\r\n' % (len(self),)
                ret = ret + 'Field names: '
                for i in self.header:
                    ret = ret + i + ', '

                ret = ret[:-2]
            else:
                ret = ret + ', No cache entries.'
            return ret
        except:
            sys.exc_clear()
            return '<Instance of Recordset containing crappy data>'

    def __LoadData(self, key):
        if self.dbfetcher is None:
            return
        if type(self.dbfetcher) == types.StringType:
            conf = cfg.GetConfigSvc()
            fetch = getattr(conf, self.dbfetcher)
            fk = fetch(key)
            if isinstance(fk, Exception):
                raise fk
            if type(fk) == types.TupleType:
                self.header, data = fk
            elif hasattr(fk, '__columns__'):
                self.header = fk.__columns__
                data = [list(fk)]
            elif hasattr(fk, 'columns'):
                self.header = fk.columns
                data = fk
            else:
                raise RuntimeError('_LoadData called with unsupported data type', fk.__class__)
        elif type(self.dbfetcher) in [types.ListType, types.TupleType]:
            self.header, data = self.dbfetcher
        else:
            fetch = self.dbfetcher
            self.header, data = fetch(key)
        if self.keyidx is None:
            self.keyidx = self.header.index(self.keycolumn)
        self.__PopulateDataset(data, key, None)

    def Hint(self, key, value):
        if key:
            if key in self.data and idCheckers.IsLocalIdentity(key):
                return
            if len(value) < len(self.header):
                log.LogError('Recordset.Hint is receiving a value that is less than the header length, key=', key, '| classType=', self.rowclass, '| value=', value)
            if len(self.header) == len(value):
                self.data[key] = value
            else:
                self.data[key] = value[:len(self.header)]
        elif hasattr(value, 'columns'):
            self.__PopulateDataset(value, None, list)
        else:
            raise RuntimeError('Hint called with unsupported data type', value.__class__)

    def Prime(self, keys, fuxorcheck = 1):
        if fuxorcheck:
            i = 0
            for each in keys:
                if each not in self.data:
                    i += 1

            if i >= 50:
                flag = [log.LGINFO, log.LGWARN][i >= 100]
                log.general.Log('%s - Prime() called for %s items from %s' % (self.GetFetcherString(), i, log.WhoCalledMe()), flag)
            if boot.role == 'client' and i == 1:
                NUM_SEC = 2
                s = int(blue.os.GetWallclockTime() / (NUM_SEC * const.SEC))
                if s > self.singlePrimeTimestamp + NUM_SEC:
                    self.singlePrimeCount = 0
                self.singlePrimeTimestamp = s
                self.singlePrimeCount += 1
                if self.singlePrimeCount < 100:
                    tick = 10
                    flag = log.LGWARN
                else:
                    tick = 50
                    flag = log.LGERR
                if self.singlePrimeCount >= tick and self.singlePrimeCount % tick == 0:
                    log.general.Log('%s - Prime() called for %s single items. Last caller was %s. Caller might want to consider using Prime()' % (self.GetFetcherString(), self.singlePrimeCount, log.WhoCalledMe()), flag)
        if keys:
            self.waitingKeys.update(keys)
            uthread.Lock(self, 0)
            try:
                self._Prime()
            finally:
                uthread.UnLock(self, 0)

    def _Prime(self):
        if self.dbMultiFetcher is None:
            return
        if not self.waitingKeys:
            return
        keysToGet = self.waitingKeys
        localKeysToGet = set()
        keysIAlreadyHave = set()
        for key in keysToGet:
            if key in self.data:
                keysIAlreadyHave.add(key)
            elif self.clientLocalFetcher is not None and idCheckers.IsLocalIdentity(key):
                localKeysToGet.add(key)

        self.waitingKeys = set()
        keysToGet -= self.knownLuzers
        localKeysToGet -= self.knownLuzers
        keysToGet -= keysIAlreadyHave
        if len(localKeysToGet):
            localFetch = getattr(cfg, self.clientLocalFetcher)
            fk = localFetch(list(keysToGet))
            if isinstance(fk, Exception):
                raise fk
            if type(fk) == types.TupleType:
                self.header, data = fk
            elif hasattr(fk, 'columns'):
                self.header = fk.columns
                data = fk
            else:
                data = []
                cfg.LogWarn('Recordset: ', self.clientLocalFetcher, ' returned an empty record set from local data. Attempting to fetch from server to compensate!')
            if self.keyidx is None:
                self.keyidx = self.header.index(self.keycolumn)
            ix = self.keyidx
            for i in data:
                self.data[i[ix]] = i
                keysToGet.remove(i[ix])

        if len(keysToGet) == 0:
            return
        conf = cfg.GetConfigSvc()
        fetch = getattr(conf, self.dbMultiFetcher)
        fk = fetch(list(keysToGet))
        if isinstance(fk, Exception):
            raise fk
        if type(fk) == types.TupleType:
            self.header, data = fk
        elif hasattr(fk, '__columns__'):
            self.header = fk.__columns__
            data = [list(fk)]
        elif hasattr(fk, 'columns'):
            self.header = fk.columns
            data = fk
        else:
            raise RuntimeError('_Prime called with unsupported data type', fk.__class__)
        if self.keyidx is None:
            self.keyidx = self.header.index(self.keycolumn)
        ix = self.keyidx
        for i in data:
            self.data[i[ix]] = i
            keysToGet.remove(i[ix])

        for luzer in keysToGet:
            self.knownLuzers.add(luzer)
            log.general.Log('Failed to prime ' + strx(luzer), 1, 1)

    def __PopulateDataset(self, data, key = None, factory = None):
        if hasattr(data, 'columns'):
            ix = data.columns.index(self.keycolumn)
        else:
            ix = self.header.index(self.keycolumn)
        gotit = 0
        for i in data:
            if factory is not None:
                i = factory(i)
            if i[ix] not in self.data:
                self.data[i[ix]] = i
            if key and i[ix] == key:
                gotit = 1
            blue.pyos.BeNice()

        if key and not gotit:
            self.knownLuzers.add(key)
            log.LogTraceback()

    def RemoveFromKnowLuzers(self, key):
        self.knownLuzers.discard(key)

    def Get(self, key, flush = 0):
        key = int(key)
        if flush or not self.data.has_key(key):
            if boot.role != 'server':
                self.Prime([key])
            else:
                uthread.Lock(self, key)
                try:
                    if flush or not self.data.has_key(key):
                        self.__LoadData(key)
                finally:
                    uthread.UnLock(self, key)

        if self.data.has_key(key):
            return self.rowclass(self, key)
        raise KeyError('RecordNotFound', key)

    def GetIfExists(self, key):
        if self.data.has_key(key):
            return self.rowclass(self, key)
        else:
            return None

    def xxx__getitem__(self, index):
        if index > len(self.data):
            raise RuntimeError('RecordNotLoaded')
        return self.rowclass(self, self.data.keys()[index])

    def __getitem__(self, key):
        return self.rowclass(self, key)

    def __iter__(self):

        class RecordsetIterator:

            def next(self):
                return self.rowset.rowclass(self.rowset, self.iter.next())

        it = RecordsetIterator()
        it.rowset = self
        it.iter = self.data.iterkeys()
        return it

    def __contains__(self, key):
        return key in self.data

    def GetFetcherString(self):
        if self.clientLocalFetcher is not None:
            if self.dbMultiFetcher is not None:
                fetchers = '(Local: %s - Multi: %s)' % (self.clientLocalFetcher, self.dbMultiFetcher)
            else:
                fetchers = '(Local: %s)' % self.clientLocalFetcher
        else:
            fetchers = '(Multi: %s)' % self.dbMultiFetcher
        return fetchers


class Row(utilRow):
    __guid__ = 'cfg.Row'
    __persistvars__ = ['header', 'line', 'id']

    def __init__(self, recordset = None, key = None):
        if recordset == None:
            self.__dict__['header'] = None
            self.__dict__['line'] = None
            self.__dict__['id'] = None
        else:
            self.__dict__['header'] = recordset.header
            self.__dict__['line'] = recordset.data[key]
            self.__dict__['id'] = key

    def __setattr__(self, name, value):
        if name in ('id', 'header', 'line'):
            self.__dict__[name] = value
        else:
            raise RuntimeError('ReadOnly', name)

    def __setitem__(self, key, value):
        raise RuntimeError('ReadOnly', key)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        try:
            ret = '<Instance of class ' + self.__guid__ + '>\r\n'
            header = self.header
            fields = self.line
            for i in xrange(len(header)):
                ret = ret + '%s:%s%s\r\n' % (header[i], ' ' * (23 - len(header[i])), fields[i])

            return ret
        except:
            sys.exc_clear()
            return '<Instance of Row containing crappy data>'

    def __coerce__(self, object):
        if type(object) == type(0):
            return (self.__dict__['id'], object)

    def __int__(self):
        return self.__dict__['id']
