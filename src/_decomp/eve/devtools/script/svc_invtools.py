#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_invtools.py
import random
import types
import time
import blue
import evetypes
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD, SERVICE_RUNNING, SERVICE_START_PENDING, SERVICE_STOP_PENDING, SERVICE_STOPPED
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from carbonui.control.window import Window
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg
MAX_VOLUME = 1000000000
Progress = lambda title, text, current, total: sm.GetService('loading').ProgressWnd(title, text, current, total)

class InvTools(Service):
    __module__ = __name__
    __exportedcalls__ = {}
    __notifyevents__ = []
    __dependencies__ = []
    __servicename__ = 'invtools'
    __displayname__ = 'invtools'
    __guid__ = 'svc.invtools'

    def __init__(self):
        Service.__init__(self)
        self.inv = sm.GetService('invCache').GetInventory

    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        Service.Run(self, memStream)
        self.wnd = None
        self.state = SERVICE_RUNNING

    def Stop(self, memStream = None):
        self.state = SERVICE_STOP_PENDING
        Service.Stop(self, memStream)
        self.state = SERVICE_STOPPED

    def Startup(self, *args):
        pass

    def GetShip(self, *args):
        if not hasattr(eve.session, 'shipid'):
            return
        return self.inv(eve.session.shipid)

    def GetSelf(self, *args):
        if not hasattr(eve.session, 'charid'):
            return
        return self.inv(eve.session.charid)

    def GetSpecial(self, loc = None, *args):
        if loc is None:
            return
        return self.inv(loc)

    def IsValid(self, typeID, onlyPublished, onlyUnpublished, volume):
        if evetypes.GetVolume(typeID) > volume:
            return False
        if onlyPublished and not evetypes.IsPublished(typeID):
            return False
        if onlyUnpublished and evetypes.IsPublished(typeID):
            return False
        if evetypes.IsDynamicType(typeID):
            return False
        return True

    def SpawnRandom(self, loc = None, flag = None, minQty = None, maxQty = None, iterations = None, categories = True, groups = False, want = None, onlyPublished = True, onlyUnpublished = False, useMultiMove = True, volume = None, *args):
        if loc is None:
            return
        if loc == eveCfg.GetActiveShip() and sm.GetService('clientDogmaIM').GetDogmaLocation().GetItem(loc).groupID == const.groupCapsule:
            eve.Message('CustomNotify', {'notify': 'You cannot spawn items into capsule.'})
            return
        if minQty is None:
            minQty = 1
        if maxQty is None:
            maxQty = 10
        if iterations is None:
            iterations = 10
        if minQty > maxQty:
            eve.Message('CustomNotify', {'notify': 'Min stack size is greater than max stack size.'})
            return
        if minQty > iterations:
            eve.Message('CustomNotify', {'notify': 'Min stack size is greater than number of items.'})
            return
        if want is None:
            categories = True
            want = [const.categoryCharge,
             const.categoryCommodity,
             const.categoryModule,
             const.categoryStructureModule]
        if type(want) is types.IntType:
            want = [want]
        if type(want) is not types.ListType:
            return
        selectedTypesAndQty = []
        mustMove = []
        possibleTypes = []
        if categories:
            for typeID in evetypes.GetTypeIDsByCategories(want):
                if self.IsValid(typeID, onlyPublished, onlyUnpublished, volume):
                    possibleTypes.append(typeID)

        else:
            for typeID in evetypes.GetTypeIDsByGroups(want):
                if self.IsValid(typeID, onlyPublished, onlyUnpublished, volume):
                    possibleTypes.append(typeID)

        if len(possibleTypes) == 0:
            return
        for i in xrange(1, iterations + 1):
            selectedTypesAndQty.append((random.choice(possibleTypes), random.choice(xrange(minQty, maxQty + 1))))

        title = 'Spawning...'
        idx = int()
        qty = len(selectedTypesAndQty)
        Progress(title, 'Processing', 0, qty)
        for t, q in selectedTypesAndQty:
            idx += 1
            msg = 'Processing %d of %d' % (idx, qty)
            Progress(title, msg, idx, qty)
            if q == 0:
                q = 1
            try:
                if eve.session.role & ROLE_WORLDMOD:
                    itemID = sm.RemoteSvc('slash').SlashCmd('/createitem %d %d' % (t, q))
                elif eve.session.role & ROLE_GML:
                    itemID = sm.RemoteSvc('slash').SlashCmd('/load me %d %d' % (t, q))[0]
                else:
                    return
                mustMove.append(itemID)
            except Exception:
                self.LogException('Failed to spawn item with typeID %s' % t)

        Progress(title, 'Complete', 1, 1)
        if session.stationid is not None and loc != const.containerHangar:
            self.MoveItems(items=mustMove, source=session.locationid, destination=loc, flag=flag, multi=useMultiMove, suppress=True)

    def GetFlags(self, *args):
        flagList = []
        for key in const.__dict__:
            if key.lower().startswith('flag'):
                flagList.append(key)

        flagList.sort()
        return flagList

    def GetItemFromContainer(self, itemID = None, container = None, *args):
        if itemID is None:
            return
        if container is None:
            return
        inv = [ item for item in self.inv(container).List() ]
        for item in inv:
            if item.itemID == itemID:
                return item

    def MoveItems(self, items = None, source = None, destination = None, flag = None, multi = True, suppress = False, **kwargs):
        if None in (items, source, destination):
            return
        if not suppress:
            destinationCargo = {}
            postDestinationCargo = {}
            sourceCargo = {}
            postSourceCargo = {}
            cargoDict = {}
            for rec in self.inv(destination).List():
                destinationCargo[rec.itemID] = rec.stacksize

            for rec in self.inv(source).List():
                sourceCargo[rec.itemID] = rec.stacksize

            for each in items:
                cargoDict[each] = self.GetItemFromContainer(each, source).stacksize

        title = 'Moving...'
        Progress(title, 'Telling Scotty the docking manager what to do...', 0, 1)
        if multi:
            if flag is not None:
                self.inv(destination).MultiAdd(items, source, flag=flag, **kwargs)
            else:
                self.inv(destination).MultiAdd(items, source, **kwargs)
        else:
            idx = int()
            all = len(items)
            for itemID in items:
                idx += 1
                msg = 'Processing %d of %d' % (idx, all)
                Progress(title, msg, idx, all)
                self.inv(destination).Add(itemID, source, **kwargs)

        Progress(title, "All done, don't forget to pay the man!", 1, 1)
        if not suppress:
            blue.pyos.synchro.SleepWallclock(5000)
            for rec in self.inv(destination).List():
                postDestinationCargo[rec.itemID] = rec.stacksize

            for rec in self.inv(source).List():
                postSourceCargo[rec.itemID] = rec.stacksize

            for k in cargoDict.iterkeys():
                if k in postDestinationCargo:
                    qtyCargo = cargoDict[k]
                    qtyDest = postDestinationCargo[k]
                    if qtyCargo == qtyDest:
                        pass
                    else:
                        print k, ' is in destination and qty is different!'
                else:
                    print '\t%s is not in destination', k
                    print '\tsrc inv rec', self.GetItemFromContainer(k, source)
                    print '\tdest inv rec:', self.GetItemFromContainer(k, destination)

            postSourceCopy = postSourceCargo.copy()
            postSourceCopy.update(cargoDict)
            print '\tsrc ok?\t', ['No', 'Yes'][postSourceCopy == sourceCargo]
            destinationCopy = destinationCargo.copy()
            destinationCopy.update(cargoDict)
            print '\tdest ok?\t', ['No', 'Yes'][destinationCopy == postDestinationCargo]

    def InvMoveLoop(self, loop = None, noSpawn = True, *args):
        if loop is None:
            loop = 10
        _loop = loop
        if not noSpawn:
            self.SpawnRandom(eve.session.shipid, iterations=10)
        items = self.GetShip().ListCargo()
        if len(items) == 0:
            return
        itemIDs = [ rec.itemID for rec in items ]
        moveCommands = [(eve.session.shipid,
          const.containerHangar,
          const.flagHangar,
          False),
         (const.containerHangar,
          eve.session.shipid,
          const.flagCargo,
          False),
         (eve.session.shipid,
          const.containerHangar,
          const.flagHangar,
          True),
         (const.containerHangar,
          eve.session.shipid,
          const.flagCargo,
          True)]
        lookup = {eveCfg.GetActiveShip(): 'Ship',
         const.containerHangar: 'Hangar Floor',
         const.flagCargo: 'Cargo Bay',
         const.flagCorpSAG1: 'Corp Hangar, Division 1',
         const.flagCorpSAG2: 'Corp Hangar, Division 2',
         const.flagCorpSAG3: 'Corp Hangar, Division 3',
         const.flagCorpSAG4: 'Corp Hangar, Division 4',
         const.flagCorpSAG5: 'Corp Hangar, Division 5',
         const.flagCorpSAG6: 'Corp Hangar, Division 6',
         const.flagCorpSAG7: 'Corp Hangar, Division 7',
         const.flagCorpGoalDeliveries: 'Corp Hangar, Goal Deliveries'}
        usecase = {True: 'multimove',
         False: 'single move'}
        office = sm.StartService('officeManager').GetCorpOfficeAtLocation()
        if office is not None:
            office = office.officeID
            moveCommands.extend([(eve.session.shipid,
              office,
              const.flagCorpSAG1,
              False),
             (office,
              office,
              const.flagCorpSAG2,
              False),
             (office,
              office,
              const.flagCorpSAG3,
              False),
             (office,
              office,
              const.flagCorpSAG4,
              False),
             (office,
              office,
              const.flagCorpSAG5,
              False),
             (office,
              office,
              const.flagCorpSAG6,
              False),
             (office,
              office,
              const.flagCorpSAG7,
              False),
             (office,
              office,
              const.flagCorpGoalDeliveries,
              False),
             (office,
              eve.session.shipid,
              const.flagCargo,
              False),
             (eve.session.shipid,
              office,
              const.flagCorpSAG1,
              True),
             (office,
              office,
              const.flagCorpSAG2,
              True),
             (office,
              office,
              const.flagCorpSAG3,
              True),
             (office,
              office,
              const.flagCorpSAG4,
              True),
             (office,
              office,
              const.flagCorpSAG5,
              True),
             (office,
              office,
              const.flagCorpSAG6,
              True),
             (office,
              office,
              const.flagCorpSAG7,
              True),
             (office,
              office,
              const.flagCorpGoalDeliveries,
              True),
             (office,
              eve.session.shipid,
              const.flagCargo,
              True)])
            lookup[office] = 'Office'
        start = time.time()
        while loop:
            for src, dest, f, m in moveCommands:
                if f is not None:
                    print "Moving from %s to %s's %s using %s:" % (lookup[src],
                     lookup[dest],
                     lookup[f],
                     usecase[m])
                else:
                    print 'Moving from %s to %s using %s:' % (lookup[src], lookup[dest], usecase[m])
                t = time.time()
                self.MoveItems(itemIDs, src, dest, f, m)
                duration = time.time() - t
                print 'Move took %d:%.2d to move %s items\n' % (duration / 60, duration % 60, len(items))

            loop -= 1

        finish = time.time() - start
        print 'Move test complete, total time: %d:%.2d for %s iteration(s)' % (finish / 60, finish % 60, _loop)
        print '%s items were moved %s times' % (len(items), len(moveCommands) * _loop)


class InvToolsWnd(Window):
    __guid__ = 'form.invTools'
    __notifyevents__ = ['OnSessionChanged']
    RANDOM_COMBO = ('Random', 'random')
    PUBLISHED_LIST = ['<color=0xffff0000>Not Published<color=0xffffffff>', '<color=0xff00ff00>Published<color=0xffffffff>']
    default_windowID = 'InvTools'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('Inventory Tools')
        self.MakeUnResizeable()
        self.cats = None
        self.grps = None
        self.locs = None
        self.DoSetup()
        self.Begin()

    def OnSessionChanged(self, isRemote, session, change):
        self.location.entries = self.locs = self.GetLocations()
        self.location.SetValue('ship')

    def DoSetup(self):
        self.cats = [ ('%s [%s]' % (evetypes.GetCategoryNameByCategory(categoryID), self.PUBLISHED_LIST[evetypes.IsCategoryPublishedByCategory(categoryID)]), categoryID) for categoryID in evetypes.IterateCategories() if categoryID is not 0 ]
        self.cats.sort()
        self.cats.insert(0, self.RANDOM_COMBO)
        self.grps = [self.RANDOM_COMBO]
        self.default = {'categoryID': 'random',
         'groupID': 'random',
         'published': 1,
         'multimove': 1,
         'minQty': 1,
         'maxQty': 10,
         'number': 10,
         'volume': MAX_VOLUME,
         'location': 'ship'}
        self.config = self.default.copy()
        self.locs = self.GetLocations()
        self.spawnlocation = (eveCfg.GetActiveShip(), const.flagCargo)
        self.prepCorpHangar = False

    def Begin(self):
        margin = const.defaultPadding
        self.main = main = Container(name='main', parent=self.sr.main, padding=margin)
        Frame(parent=main, color=(1.0, 1.0, 1.0, 0.2))
        uix.GetContainerHeader('Random Item Spawn', main, bothlines=0)
        COMBOPADDING = 120
        self.categories = Combo(parent=main, options=self.cats, select=self.config['categoryID'], name='category', align=uiconst.TOTOP, callback=self.DoCategoryChange, padding=(COMBOPADDING,
         margin,
         margin,
         0))
        txt = eveLabel.Label(text='Category', parent=self.categories, align=uiconst.CENTERLEFT, left=-COMBOPADDING + margin, fontsize=10)
        self.groups = Combo(parent=main, options=self.grps, select=self.config['groupID'], name='group', align=uiconst.TOTOP, callback=self.DoGroupChange, padding=(COMBOPADDING,
         margin,
         margin,
         0))
        txt = eveLabel.Label(text='Group', parent=self.groups, align=uiconst.CENTERLEFT, left=-COMBOPADDING + margin, fontsize=10)
        self.pub = RadioButton(text='use only published items', parent=main, settingsKey='pub', retval=0, checked=bool(self.config['published'] == 1), groupname='published', align=uiconst.TOTOP, callback=self.DoPublishChange, padding=(margin,
         0,
         margin,
         0))
        Line(parent=main, align=uiconst.TOTOP)
        self.unpub = RadioButton(text='use only unpublished items', parent=main, settingsKey='unpub', retval=0, checked=bool(self.config['published'] == 0), groupname='published', align=uiconst.TOTOP, callback=self.DoPublishChange, padding=(margin,
         0,
         margin,
         0))
        self.all = RadioButton(text='use all items', parent=main, settingsKey='all', retval=0, checked=bool(self.config['published'] == -1), groupname='published', align=uiconst.TOTOP, callback=self.DoPublishChange, padding=(margin,
         0,
         margin,
         0))
        Line(parent=main, align=uiconst.TOTOP)
        self.multimove = Checkbox(text='use multimove', parent=main, settingsKey='multimove', checked=self.config['multimove'], groupname=None, align=uiconst.TOTOP, callback=self.DoMoveChange, padding=(margin,
         0,
         margin,
         0))
        Line(parent=main, align=uiconst.TOTOP)
        for checkbox in [self.pub,
         self.unpub,
         self.all,
         self.multimove]:
            checkbox.hint = 'Changing this is <color=0xffff0000>not advised<color=0xffffffff>.<br>Proceed with caution!'

        INPUTPADDING = 140
        self.min = SingleLineEditInteger(name='minQty', setvalue=str(self.config['minQty']), minValue=1, maxValue=100, parent=main, align=uiconst.TOTOP, padding=(INPUTPADDING,
         margin,
         margin,
         0))
        txt = eveLabel.Label(text='Minimum stack size', parent=self.min, align=uiconst.CENTERLEFT, left=-INPUTPADDING + margin, fontsize=10)
        self.max = SingleLineEditInteger(name='maxQty', setvalue=str(self.config['maxQty']), minValue=1, maxValue=100, parent=main, align=uiconst.TOTOP, padding=(INPUTPADDING,
         margin,
         margin,
         0))
        txt = eveLabel.Label(text='Maximum stack size', parent=self.max, align=uiconst.CENTERLEFT, left=-INPUTPADDING + margin, fontsize=10)
        self.number = SingleLineEditInteger(name='number', setvalue=str(self.config['number']), minValue=1, maxValue=1000, parent=main, align=uiconst.TOTOP, padding=(INPUTPADDING,
         margin,
         margin,
         0))
        txt = eveLabel.Label(text='Number of Items', parent=self.number, align=uiconst.CENTERLEFT, left=-INPUTPADDING + margin, fontsize=10)
        self.volume = SingleLineEditFloat(name='volume', setvalue=str(self.config['volume']), maxValue=MAX_VOLUME, parent=main, align=uiconst.TOTOP, padding=(INPUTPADDING,
         margin,
         margin,
         0))
        txt = eveLabel.Label(text='Maximum item volume', parent=self.volume, align=uiconst.CENTERLEFT, left=-INPUTPADDING + margin, fontsize=10)
        self.location = Combo(parent=main, options=self.locs, select=self.config['location'], name='location', align=uiconst.TOTOP, callback=self.DoLocationChange, padding=(COMBOPADDING,
         margin,
         margin,
         0))
        txt = eveLabel.Label(text='Location', parent=self.location, align=uiconst.CENTERLEFT, left=-COMBOPADDING + margin, fontsize=10)
        buttons = [['Spawn',
          self.DoFormSubmit,
          None,
          81]]
        btns = ButtonGroup(btns=buttons, line=1, parent=main, padTop=margin)
        btn = btns.GetChild('Spawn_Btn')
        if eve.session.role & ROLE_WORLDMOD:
            btn.hint = 'Spawn using /createitem...'
        elif eve.session.role & ROLE_GML:
            btn.hint = 'Spawn using /load...'
        else:
            btn.hint = 'No <b>WORLDMOD</b> or <b>GML</b> role present.'
        content_height = sum((each.height + each.padTop + each.padBottom + each.top for each in main.children)) + 16
        _, window_height = self.GetWindowSizeForContentSize(height=content_height)
        self.height = window_height

    def DoCategoryChange(self, combo, text, value):
        self.config['categoryID'] = value
        if value == 'random':
            self.grps = [self.RANDOM_COMBO]
        else:
            self.grps = [ ('%s [%s]' % (evetypes.GetGroupNameByGroup(groupID), self.PUBLISHED_LIST[evetypes.IsGroupPublishedByGroup(groupID)]), groupID) for groupID in evetypes.IterateGroups() if evetypes.GetCategoryIDByGroup(groupID) == value ]
            self.grps.sort()
            self.grps.insert(0, self.RANDOM_COMBO)
        self.groups.SetValue('random')
        self.config['groupID'] = 'random'
        self.groups.entries = self.grps

    def DoGroupChange(self, combo, text, value):
        self.config['groupID'] = value

    def DoLocationChange(self, combo, text, value):
        self.prepCorpHangar = False
        self.config['location'] = value
        if value == 'ship':
            self.spawnlocation = (eveCfg.GetActiveShip(), const.flagCargo)
        elif value == 'hangar':
            self.spawnlocation = const.containerHangar

    def DoPublishChange(self, cb):
        lookup = {'pub': 1,
         'unpub': 0,
         'all': -1}
        self.config['published'] = lookup[cb.name]

    def DoMoveChange(self, cb):
        self.config['multimove'] = cb.GetValue()

    def DoFormSubmit(self, *args):
        for formField in [self.min,
         self.max,
         self.number,
         self.volume]:
            configFieldName = formField.name
            self.config[configFieldName] = formField.GetValue()

        loc = self.spawnlocation
        if isinstance(loc, types.TupleType):
            loc, flag = loc
        else:
            flag = None
        if self.config['categoryID'] == 'random':
            ids = set([ evetypes.GetCategoryIDByGroup(groupID) for groupID in evetypes.IterateGroups() ])
            want = list(ids)
            categories = True
            groups = False
        elif self.config['groupID'] == 'random':
            ids = evetypes.GetGroupIDsByCategory(self.config['categoryID'])
            want = list(ids)
            categories = False
            groups = True
        else:
            want = [self.config['groupID']]
            categories = False
            groups = True
        publishedFlags = {0: (False, True),
         1: (True, False),
         -1: (False, False)}
        onlyPublished, onlyUnpublished = publishedFlags[self.config['published']]
        if self.prepCorpHangar is True:
            sm.GetService('window').OpenCorpHangar(None, None, 1)
        sm.StartService('invtools').SpawnRandom(loc=loc, flag=flag, minQty=self.config['minQty'], maxQty=self.config['maxQty'], iterations=self.config['number'], categories=categories, groups=groups, want=want, onlyPublished=onlyPublished, onlyUnpublished=onlyUnpublished, useMultiMove=self.config['multimove'], volume=self.config['volume'])

    def GetLocations(self):
        ret = [('Current Ship', 'ship')]
        if eve.session.stationid or eve.session.structureid:
            ret.append(('Hangar Floor', 'hangar'))
        return ret
