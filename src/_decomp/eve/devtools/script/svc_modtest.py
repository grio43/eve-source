#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_modtest.py
import blue
import dogma.data
import evetypes
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.util import uix
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.parklife import states as state
from carbonui.uicore import uicore
from eveexceptions import UserError
SERVICENAME = 'modtest'
Progress = lambda title, text, current, total: sm.GetService('loading').ProgressWnd(title, text, current, total)

class ModTest(Service):
    __exportedcalls__ = {}
    __notifyevents__ = ['ProcessRestartUI']
    __dependencies__ = []
    __guid__ = 'svc.modtest'
    __servicename__ = SERVICENAME
    __displayname__ = SERVICENAME

    def Run(self, memStream = None):
        self.wnd = None
        self.ammo = None

    def InitGroups(self):
        if getattr(self, 'testgroups', None):
            return
        self.testgroups = {}
        t, a, p = self.GetModuleLists()
        t = t + a
        for x in t:
            gid = evetypes.GetGroupID(x[0])
            if gid not in (const.groupSiegeModule,
             const.groupSuperWeapon,
             const.groupJumpPortalGenerator,
             const.groupMiningLaser):
                self.testgroups[gid] = True
            else:
                self.testgroups[gid] = False

    def Stop(self, memStream = None):
        self.Hide()
        Service.Stop(self, memStream)

    def Show(self):
        if not self.wnd:
            self.wnd = wnd = Window.Open(windowID=SERVICENAME)
            wnd._OnClose = self.Hide
            wnd.SetCaption('Module Test')
            wnd.sr.main = wnd.GetChild('main')
            wnd.SetMinSize((352, 200))
            main = Container(name='main', parent=wnd.sr.main, pos=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            eveLabel.Label(text='Select module groups to test', parent=main, align=uiconst.TOTOP, width=10, left=5, top=5, color=None, state=uiconst.UI_DISABLED)
            wnd.sr.scroll = eveScroll.Scroll(parent=main)
            buttons = [['Test',
              self.Test,
              None,
              81], ['Close',
              self.Hide,
              None,
              81]]
            wnd.sr.main.children.insert(0, ButtonGroup(btns=buttons))
            scrolllist = []
            self.InitGroups()
            for gid in self.testgroups:
                groupName = evetypes.GetGroupNameByGroup(gid)
                scrolllist.append(GetFromClass(CheckboxEntry, {'label': groupName,
                 'checked': self.testgroups[gid],
                 'cfgname': groupName.replace(' ', ''),
                 'retval': gid,
                 'OnChange': self.CheckBoxChange}))

            scrolllist.sort(lambda a, b: cmp(a.label, b.label))
            wnd.sr.scroll.Load(contentList=scrolllist)

    def CheckBoxChange(self, checkbox, node, *args):
        self.testgroups[node.retval] = checkbox.checked

    def Hide(self, *args):
        if self.wnd:
            self.wnd.Close()
            self.wnd = None

    def ProcessRestartUI(self):
        if self.wnd:
            self.Hide()
            self.Show()

    def GetModuleLists(self):
        test = {}
        groups = dict.fromkeys([ groupID for groupID in evetypes.GetGroupIDsByCategory(const.categoryModule) ])
        for parentID in evetypes.GetAllVariationParents():
            for typeID in evetypes.GetVariationChildren(parentID):
                metaGroupID = evetypes.GetMetaGroupID(typeID)
                if metaGroupID == 2:
                    if evetypes.Exists(typeID) and evetypes.GetMarketGroupID(typeID) and evetypes.GetCategoryID(typeID) == const.categoryModule:
                        test[evetypes.GetGroupID(typeID)] = typeID

        for typeID in evetypes.Iterate():
            groupID = evetypes.GetGroupID(typeID)
            if groupID not in test and groupID in groups:
                if evetypes.GetVariationChildren(typeID) is None:
                    if evetypes.GetMarketGroupID(typeID):
                        test[groupID] = typeID

        targeted = []
        activated = []
        passive = []
        for typeID in test.values():
            effects = [ dogma.data.get_effect(row.effectID) for row in dogma.data.get_type_effects(typeID) ]
            effectCategories = [ eff.effectCategory for eff in effects if eff.effectName != 'online' ]
            if const.dgmEffTarget in effectCategories:
                targeted.append((typeID, effects))
            elif const.dgmEffActivation in effectCategories:
                activated.append((typeID, effects))
            else:
                passive.append((typeID, effects))

        return (targeted, activated, passive)

    def GetAmmo(self):
        if getattr(self, 'ammo', None):
            return
        groups = {}
        for groupID in evetypes.GetGroupIDsByCategory(const.categoryCharge):
            groups[groupID] = True

        self.ammo = {}
        godma = sm.GetService('godma')
        for typeID in evetypes.GetTypeIDsByGroups(groups.keys()):
            groupID = evetypes.GetGroupID(typeID)
            if groupID in self.ammo:
                self.ammo[groupID].append(godma.GetType(typeID))
            else:
                self.ammo[groupID] = [godma.GetType(typeID)]

    def Test(self, *args):
        if eve.session.stationid:
            return
        self.Hide()

        def _Click(module):
            module.Click()
            while module.sr.glow.state == uiconst.UI_HIDDEN:
                blue.pyos.synchro.SleepWallclock(1)

            try:
                module.Click()
            except:
                pass

        def _Idle(module):
            return module.sr.glow.state == uiconst.UI_HIDDEN and module.sr.busy.state == uiconst.UI_HIDDEN and module.blinking == False and module.reloadingAmmo is False

        def _WaitForIdle(module, timeout = 60000, reason = None):
            if reason:
                print 'WaitForIdle: %s' % reason
            blue.pyos.synchro.SleepWallclock(100)
            timeout -= 100
            while not _Idle(module) and timeout > 0:
                blue.pyos.synchro.SleepWallclock(100)
                timeout -= 100

        self.GetAmmo()
        t, a, p = self.GetModuleLists()
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if eve.session.role & ROLE_PROGRAMMER:
            if ship.cpuOutput != 13371337:
                w = sm.RemoteSvc('slash')
                w.SlashCmd('/dogma me cpuOutput = 13371337')
                w.SlashCmd('/dogma me powerOutput = 10000000')
                w.SlashCmd('/dogma me hiSlots = 8')
                w.SlashCmd('/dogma me medSlots = 8')
                w.SlashCmd('/dogma me lowSlots = 8')
                w.SlashCmd('/dogma me rigSlots = 8')
                w.SlashCmd('/dogma me upgradeCapacity = 10000')
                w.SlashCmd('/dogma me turretSlotsLeft = 8')
                w.SlashCmd('/dogma me launcherSlotsLeft = 8')
                w.SlashCmd('/dogma me upgradeSlotsLeft = 8')
                w.SlashCmd('/dogma me capacity = 1000000')
                w.SlashCmd('/dogma me capacitorCapacity = 1000000')
        errors = []
        t = filter(lambda x: self.testgroups[x[0].groupID], t + a)
        total = len(t)
        current = 0
        while t:
            sm.RemoteSvc('slash').SlashCmd('/unload me all')
            slotsLeft = {'hiPower': [ x + const.flagHiSlot0 for x in range(int(ship.hiSlots)) ],
             'medPower': [ x + const.flagMedSlot0 for x in range(int(ship.medSlots)) ],
             'loPower': [ x + const.flagLoSlot0 for x in range(int(ship.lowSlots)) ],
             'rigSlot': [ x + const.flagRigSlot0 for x in range(int(ship.rigSlots)) ]}
            for item in t[:]:
                typeID, effects = item
                Progress('Module Test', 'Fitting %d/%d: %s' % (current, total, evetypes.GetName(typeID)), current, total)
                current += 1
                try:
                    slotType = [ eff.effectName for eff in effects if eff.effectName.endswith('Power') or eff.effectName == 'rigSlot' ][0]
                    if slotsLeft[slotType]:
                        sm.RemoteSvc('slash').SlashCmd('/fit me %s' % typeID)
                        t.remove(item)
                        flag = slotsLeft[slotType].pop(0)
                        module = []
                        while not module:
                            blue.pyos.synchro.SleepSim(500)
                            module = [ x for x in sm.GetService('godma').GetItem(eve.session.shipid).modules if x.flagID == flag ]

                        if not eve.session.stationid:
                            sm.RemoteSvc('slash').SlashCmd('/heal me capac=1')
                        if slotsLeft.values() == [[],
                         [],
                         [],
                         []]:
                            break
                except UserError as e:
                    errors.append((typeID, str(e)))

            Progress('Module Test', 'Testing, hold on...', current, total)
            for itemID in sm.GetService('target').GetTargets():
                slimItem = uix.GetBallparkRecord(itemID)
                if slimItem.typeID == 12403:
                    break
            else:
                itemID = sm.RemoteSvc('slash').SlashCmd('/spawn 12403 victim')
                sm.GetService('target').ClearTargets()
                sm.GetService('target').LockTarget(itemID)
                slimItem = uix.GetBallparkRecord(itemID)

            if slimItem:
                sm.GetService('stateSvc').SetState(slimItem.itemID, state.selected, 1)
                sm.GetService('stateSvc').SetState(slimItem.itemID, state.activeTarget, 1)
            if not uicore.layer.shipui:
                return
            for module in uicore.layer.shipui.slotsContainer.modulesByID.itervalues():
                module.SetRepeat(1000)
                attr = sm.GetService('godma').GetType(module.moduleinfo.typeID)
                groups = []
                for x in range(1, 4):
                    if attr.AttributeExists('chargeGroup%d' % x):
                        groups.append(getattr(attr, 'chargeGroup%d' % x))

                if groups:
                    module.SetAutoReload(0)
                    for gid in groups:
                        for ammo in self.ammo[gid]:
                            if ammo.chargeSize == attr.chargeSize and evetypes.GetMarketGroupID(ammo.typeID):
                                print '%s <- %s' % (evetypes.GetName(attr.typeID), evetypes.GetName(ammo.typeID))
                                sm.RemoteSvc('slash').SlashCmd('/create %d' % ammo.typeID)
                                try:
                                    sm.GetService('clientDogmaIM').GetDogmaLocation().LoadAmmoTypeToModule(module.id, ammo.typeID)
                                    _WaitForIdle(module, 2000, reason='pre-activate')
                                    if attr.chargeSize == 4:
                                        blue.pyos.synchro.SleepSim(5000)
                                    else:
                                        blue.pyos.synchro.SleepSim(1000)
                                    _Click(module)
                                    _WaitForIdle(module, reason='post-activate')
                                except UserError as e:
                                    errors.append((module.moduleinfo.typeID, str(e)))

                                sm.RemoteSvc('slash').SlashCmd('/unload me %d' % ammo.typeID)
                                break

                        break

                else:
                    try:
                        _Click(module)
                    except UserError as e:
                        errors.append((module.moduleinfo.typeID, str(e)))

            busy = True
            timeout = 30000
            while busy and timeout > 0:
                blue.pyos.synchro.SleepSim(250)
                timeout -= 250
                for module in uicore.layer.shipui.slotsContainer.modulesByID.itervalues():
                    if not _Idle(module):
                        break
                else:
                    busy = False

        Progress('Module Test', 'Done!', 3, 4)
        blue.pyos.synchro.Sleep(2000)
        Progress('Module Test', 'Done!', 4, 4)
        for typeID, errormsg in errors:
            self.LogError('%d: %s' % (typeID, errormsg))
