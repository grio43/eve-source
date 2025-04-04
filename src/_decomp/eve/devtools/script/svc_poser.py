#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_poser.py
import os
from math import sqrt
import evetypes
import blue
import triui
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING, ROLE_WORLDMOD
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from controltowerresources.data import get_control_tower_resources
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.util import utilWindows
from eve.client.script.util import eveMisc
from eve.common.script.sys import idCheckers
from eveexceptions import UserError
Slash = lambda x: sm.RemoteSvc('slash').SlashCmd(x)
Progress = lambda title, text, current, total: sm.GetService('loading').ProgressWnd(title, text, current, total)
PURPOSE_ONLINE = 1
PURPOSE_POWER = 2
PURPOSE_CPU = 3
PURPOSE_REINFORCED = 4
ORIENTATION = 1

class Structure():
    __guid__ = 'poser.Structure'

    def __init__(self, starbase, typeID, options = None):
        self.starbase = starbase
        self.typeID = typeID
        self.itemID = None
        self.quantity = 1
        self.name = evetypes.GetName(typeID)
        self.options = options or {}
        self.godma = sm.GetService('godma')
        self.attr = self.godma.GetType(typeID)
        groupID = evetypes.GetGroupID(typeID)
        self.isControlTower = groupID == const.groupControlTower
        self.isWeapon = self.attr.AttributeExists('chargeGroup1')
        self.isRenameable = groupID in (const.groupMobileLaboratory, const.groupAssemblyArray)

    def Create(self):
        if not self.itemID:
            self.itemID = Slash('/createitem %s' % self.typeID)
        else:
            raise RuntimeError('Instance of poser.Structure already bound to an item')

    def Position(self, x, y, z):
        self.x = self.x_ + x
        self.y = self.y_ + y
        self.z = self.z_ + z
        Slash('/tr %s %s %s %s' % (self.itemID,
         self.x,
         self.y,
         self.z))

    def Anchor(self):
        try:
            Slash('/pos anchor %s' % self.itemID)
        except:
            raise

        if 'name' in self.options and self.isRenameable:
            cfg.evelocations.Prime([self.itemID])
            sm.GetService('invCache').GetInventoryMgr().SetLabel(self.itemID, self.options['name'])
            sm.ScatterEvent('OnItemNameChange', self.itemID)

    def Online(self):
        if 'offline' not in self.options or self.isControlTower:
            Slash('/pos online %s' % self.itemID)

    def Arm(self):
        a = self.attr
        ammo = sm.GetService(SERVICENAME).GetAmmo()
        if a.AttributeExists('damageMultiplier'):
            for ammoType in ammo[a.chargeGroup1]:
                if ammoType.chargeSize == a.chargeSize:
                    break

        else:
            for ammoType in ammo[a.chargeGroup1]:
                break

        units = int(a.capacity / ammoType.volume)
        itemID = Slash('/createitem %s %s' % (ammoType.typeID, units))
        inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
        inv.Add(itemID, eve.session.shipid, qty=units)

    def GetCapacity(self):
        if self.isControlTower:
            ctinv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
            try:
                row = ctinv.capacityByFlag[const.flagNone]
                capacity = row.capacity
                used = row.used
            except:
                capacity = sm.GetService('godma').GetType(self.typeID).capacity
                used = 0.0

            return (capacity, used)
        raise RuntimeError('this only works on towers')

    def Requirements(self):
        if self.isControlTower:
            return (self.attr.cpuOutput, self.attr.powerOutput)
        else:
            return (self.attr.cpu, self.attr.power)

    def Distance(self, this):
        dx = this.x - self.x
        dy = this.y - self.y
        dz = this.z - self.z
        return sqrt(dx * dx + dy * dy + dz * dz) - this.radius

    def MoveTo(self):
        self.starbase.MoveTo(self)

    def Approach(self):
        Slash('/tr me %s' % self.itemID)

    def Hug(self):
        Slash('/tr me pos=%s,%s,%s' % (self.x + 700, self.y, self.z + 700))


class Starbase():
    __guid__ = 'poser.Starbase'

    def MoveTo(self, structure):
        structure.Approach()
        distance = 1501
        i = 600
        ball = self.bp.GetBall(structure.itemID)
        while distance > 1500:
            if not i:
                raise RuntimeError, 'Shit happened'
            i -= 1
            blue.pyos.synchro.SleepSim(100)
            distance = structure.Distance(self.ship) - ball.radius

    def Step(self, s = None, a = 0, title = 'Poser - Starbase Assembly<br>Stage %d of %d'):
        bp = self.bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        ship = self.ship = bp.GetBall(eve.session.shipid)
        if not ship:
            return
        if s is None:
            Progress(self.title, self.info, 1, 1)
            return
        if type(s) == type(0):
            self.maxsteps = s
            self.maxamount = a
            self.step = 0
            self.title_ = title
            return
        self.step += 1
        if self.maxsteps:
            self.title = self.title_ % (self.step, self.maxsteps)
        else:
            self.title = self.title_
        self.info = s
        self.done = 0
        self.Update()

    def Update(self, maxamount = 0):
        if not maxamount:
            maxamount = self.maxamount
        Progress(self.title, self.info, self.done * 1000, maxamount * 1000 + 1)
        self.done += 1

    def ImportFromEnvironment(self):
        bp = self.bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        ship = self.ship = bp.GetBall(eve.session.shipid)
        if not ship:
            return
        ct = None
        structs = []
        self.Step(0, 16, 'Poser - Starbase Scan')
        self.Step('Scanning Area...')
        i = 1
        for ballID in bp.balls.iterkeys():
            blue.pyos.BeNice()
            i += 1
            self.Update(i & 15)
            if ballID:
                ball = bp.GetBall(ballID)
                item = bp.GetInvItem(ballID)
                if ball and item and item.categoryID == const.categoryStarbase:
                    if item.groupID == const.groupControlTower:
                        ct = ballID
                    else:
                        structs.append(ballID)

        if not ct:
            info = 'No control tower found.'
            raise UserError('CustomInfo', {'info': info})
        structs.insert(0, ct)
        self.structures = []
        ownerID = bp.GetInvItem(ct).ownerID
        for ballID in structs:
            item = bp.GetInvItem(ballID)
            if item.ownerID == ownerID:
                options = {}
                ball = bp.GetBall(ballID)
                if not sm.GetService('pwn').GetStructureState(item)[0] == 'online':
                    options['offline'] = True
                s = Structure(self, item.typeID, options)
                s.x = ball.x
                s.y = ball.y
                s.z = ball.z
                s.itemID = ballID
                if s.isRenameable:
                    cfg.evelocations.Prime([ballID])
                    name = cfg.evelocations.Get(ballID).name
                    if name != evetypes.GetName(item.typeID):
                        options['name'] = name
                self.structures.append(s)
                if s.isControlTower:
                    self.controltower = ct = s
                s.x_ = int(s.x + 0.5) - int(ct.x + 0.5)
                s.y_ = int(s.y + 0.5) - int(ct.y + 0.5)
                s.z_ = int(s.z + 0.5) - int(ct.z + 0.5)

        self.Assemble = self.NoAssemble
        return self

    def ImportFromFile(self, filename):
        fh = open(filename, 'r')
        stuff = fh.read().replace('\r', '').split('\n')
        fh.close()
        self.structures = []
        self.controltower = None
        notFound = {}
        amount = len(stuff)
        for i in xrange(amount):
            line = stuff[i]
            if line.strip() != '':
                coords, name = line.split('=', 1)
                coords = coords.strip()
                name = name.strip()
                optionsDict = {}
                if name.find(':') > -1:
                    name, options = name.split(':', 1)
                    name = name.strip()
                    for option in options.split(':'):
                        if '=' in option:
                            k, v = option.split('=', 1)
                            v = v.strip()
                        else:
                            k, v = option, True
                        optionsDict[k.strip().lower()] = v

                x, y, z = coords.split()
                if name.isdigit():
                    typeID = name
                else:
                    typeID = sm.GetService('poser').FindTypeID(name)
                typeID = int(typeID)
                if not typeID:
                    notFound[name] = True
                else:
                    s = Structure(self, typeID, optionsDict)
                    s.x_ = float(x)
                    s.y_ = float(y)
                    s.z_ = float(z)
                    self.structures.append(s)
                    if s.isControlTower:
                        self.controltower = s
                    blue.pyos.BeNice()

        Progress('Poser - Loading', 'Done!', 1, 1)
        if notFound:
            sm.GetService('gameui').MessageBox('The following structures were not found:<br><font color="#FF0000">%s</font><br><br>It is possible these types have been deleted or had their name changed. Edit the .pos file and try again' % '<br>'.join(notFound.keys()), 'Unknown Structures', buttons=uiconst.OK, icon=triui.WARNING)
            raise UserError('IgnoreToTop')
        return self

    def ExportAsTriText(self):
        lines = []
        for s in self.structures:
            options = ''
            for k, v in s.options.iteritems():
                if v == True:
                    options += ':' + k
                else:
                    options += ':%s=%s' % (k, v)

            line = '% 6d % 6d % 6d = %s' % (s.x_,
             s.y_,
             s.z_,
             s.typeID)
            lines.append(line)

        return '<br>'.join(lines)

    def ExportAsFile(self, filename):
        crud = self.ExportAsTriText().replace('<br>', '\r\n')
        fh = open(filename, 'wb')
        fh.write(crud)
        fh.close()

    def NoAssemble(self):
        raise RuntimeError, 'Cannot Assemble from a live configuration'

    def Assemble(self, stepSelection = {}):
        bp = self.bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        amount = len(self.structures)
        self.Step(8, amount)
        self.Step('Creating structures...')
        x, y, z = self.ship.x, self.ship.y, self.ship.z
        for s in self.structures:
            self.Update()
            s.Create()

        self.Step('Launching structures...')
        sm.RemoteSvc('slash').SlashCmd('/tr me offset=32000,0,0')
        eveMisc.LaunchFromShip(self.structures, session.corpid)
        blue.pyos.synchro.SleepSim(2000)
        self.Step('Positioning structures...')
        for s in self.structures:
            self.Update()
            s.Position(x, y, z)

        if stepSelection.get('TowerAnchor', True):
            self.controltower.Anchor()
        if stepSelection.get('TowerFuel', True):
            self.Fuel(1, [PURPOSE_ONLINE])
        if stepSelection.get('TowerOnline', True):
            self.controltower.Online()
        if stepSelection.get('StructAnchor', True):
            self.Anchor()
        if stepSelection.get('StructFuel', True):
            self.Fuel()
        if stepSelection.get('StructOnline', True):
            self.Online()
        if stepSelection.get('ArmWeapons', True):
            self.Arm()
        self.Assemble = self.NoAssemble
        Progress('Poser - Complete', 'All done!', 1, 1)

    def GetLoad(self):
        cpu = 0
        power = 0
        for s in self.structures:
            if not s.isControlTower:
                if 'offline' not in s.options:
                    c, p = s.Requirements()
                    cpu += c
                    power += p

        ccpu, cpower = self.controltower.Requirements()
        if ccpu:
            fcpu = float(min(cpu, ccpu))
            cpu = fcpu / ccpu
        else:
            cpu = 0
        if cpower:
            fpower = float(min(power, cpower))
            power = fpower / cpower
        else:
            power = 0
        return (cpu, power)

    def GetFuelInfo(self, filter = ()):
        fcpu, fpower = self.GetLoad()
        secStatus = sm.GetService('map').securityInfo[eve.session.solarsystemid]
        factionID = sm.GetService('map').GetItem(eve.session.solarsystemid).factionID
        fuel = {PURPOSE_ONLINE: [],
         PURPOSE_POWER: [],
         PURPOSE_CPU: [],
         PURPOSE_REINFORCED: [],
         'all': [],
         'filter': []}
        volumePerCycle = {PURPOSE_ONLINE: 0.0,
         PURPOSE_POWER: 0.0,
         PURPOSE_CPU: 0.0,
         PURPOSE_REINFORCED: 0.0,
         'all': 0.0,
         'filter': 0.0}

        def _add(r, x, v):
            fuel[r.purpose].append(x)
            volumePerCycle[r.purpose] += v
            fuel['all'].append(x)
            volumePerCycle['all'] += v
            if r.purpose in filter:
                fuel['filter'].append(x)
                volumePerCycle['filter'] += v

        resources = get_control_tower_resources(self.controltower.typeID)
        for resource in resources:
            info = sm.GetService('godma').GetType(resource.resourceTypeID)
            volume = info.volume
            if info.groupID == const.groupLease:
                if secStatus >= resource.minSecurityLevel:
                    if factionID == resource.factionID:
                        _add(resource, (resource.resourceTypeID, 1), volume)
                continue
            if resource.purpose == PURPOSE_CPU:
                factor = fcpu
            elif resource.purpose == PURPOSE_POWER:
                factor = fpower
            else:
                factor = 1.0
            qty = int(factor * resource.quantity + 0.5)
            _add(resource, (resource.resourceTypeID, qty), volume * qty)

        return (volumePerCycle, fuel)

    def Fuel(self, desiredCycles = 2147483647, what = (PURPOSE_ONLINE, PURPOSE_POWER, PURPOSE_CPU)):
        self.Step('Fueling Control Tower...')
        ct = self.controltower
        v, fuel = self.GetFuelInfo(filter=what)
        if v['filter'] > 0.0:
            ct.MoveTo()
            capacity, used = ct.GetCapacity()
            ctinv = sm.GetService('invCache').GetInventoryFromId(ct.itemID)
            free = capacity - used
            cycles = min(int(free / v['filter']), desiredCycles)
            for typeID, qty in fuel['filter']:
                if qty:
                    self.Update(len(fuel['filter']))
                    itemID = Slash('/createitem %s %s' % (typeID, qty * cycles))
                    ctinv.Add(itemID, eve.session.shipid)

        self.Step()

    def Anchor(self):
        self.Step('Anchoring Structures...')
        for s in self.structures:
            self.Update()
            if not s.isControlTower:
                s.Anchor()

        blue.pyos.synchro.SleepWallclock(1000)
        self.Step()

    def Online(self):
        self.Step('Onlining Structures...')
        for s in self.structures:
            self.Update()
            if not s.isControlTower:
                s.Online()

        self.Step()

    def Arm(self):
        self.Step('Arming Weapon Batteries...')
        for s in self.structures:
            self.Update()
            if s.isWeapon:
                s.MoveTo()
                s.Arm()

        self.Step()


class FuelWindow(Window):
    __guid__ = 'form.FuelWindow'
    default_windowID = 'FuelWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('Fuel Starbase')
        self.SetMinSize([350, 250], 1)
        self.MakeUnResizeable()
        y = const.defaultPadding + 10
        self.cycles_online = SingleLineEditText(name='cycles_online', parent=self.sr.main, setvalue=0, ints=(0, 99999), left=90, width=100, top=y)
        self.cycles_cpupow = SingleLineEditText(name='cycles_cpupow', parent=self.sr.main, setvalue=0, ints=(0, 99999), left=90, width=100, top=y + 40)
        self.cycles_reinf = SingleLineEditText(name='cycles_reinf', parent=self.sr.main, setvalue=0, ints=(0, 99999), left=90, width=100, top=y + 80)
        eveLabel.Label(text='Add number of cycles fuel for...', parent=self.sr.main, width=400, left=const.defaultPadding, top=y - 12, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        y += 4
        eveLabel.Label(text='Online:', parent=self.sr.main, width=100, left=2 * const.defaultPadding, top=y, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        eveLabel.Label(text='CPU/Power:', parent=self.sr.main, width=100, left=2 * const.defaultPadding, top=y + 40, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        eveLabel.Label(text='Reinforced:', parent=self.sr.main, width=100, left=2 * const.defaultPadding, top=y + 80, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        Button(parent=self.sr.main, label='Auto', pos=(204,
         y + 5,
         0,
         0), func=self.Auto)
        y += 4
        Line(parent=self.sr.main, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.5), left=194, top=y, width=4, height=1)
        Line(parent=self.sr.main, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.5), left=194, top=y + 40, width=4, height=1)
        Line(parent=self.sr.main, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.5), left=198, top=y, width=1, height=41)
        Line(parent=self.sr.main, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.5), left=199, top=y + 20, width=4, height=1)
        buttons = [['Fuel',
          self.Fuel,
          None,
          81], ['Cancel',
          self.Cancel,
          None,
          81]]
        self.sr.main.children.insert(0, ButtonGroup(btns=buttons))

    def Cancel(self, *args):
        self.Close()

    def _prep(self):
        try:
            s = self.starbase
        except AttributeError:
            s = self.starbase = Starbase().ImportFromEnvironment()
            s.controltower.MoveTo()
            capacity, used = s.controltower.GetCapacity()
            self.free = capacity - used
            self.vol, self.fuel = s.GetFuelInfo(filter=(PURPOSE_ONLINE, PURPOSE_CPU, PURPOSE_POWER))

    def Auto(self, *args):
        self._prep()
        free = self.free - self.cycles_reinf.GetValue() * self.vol[PURPOSE_REINFORCED]
        cycles = max(int(self.free / self.vol['filter']), 0)
        self.cycles_online.SetValue(cycles)
        self.cycles_cpupow.SetValue(cycles)

    def Fuel(self, *args):
        o = self.cycles_online.GetValue()
        c = self.cycles_cpupow.GetValue()
        r = self.cycles_reinf.GetValue()
        self._prep()
        self.state = uiconst.UI_HIDDEN
        x = 0
        self.starbase.controltower.MoveTo()
        ctinv = sm.GetService('invCache').GetInventoryFromId(self.starbase.controltower.itemID)
        for cycles, purpose in [(o, PURPOSE_ONLINE),
         (c, PURPOSE_CPU),
         (c, PURPOSE_POWER),
         (r, PURPOSE_REINFORCED)]:
            if cycles:
                Progress('Adding Fuel...', 'Hold on!', x, 4)
                for fuel in self.fuel[purpose]:
                    if fuel[1]:
                        itemID = Slash('/createitem %s %s' % (fuel[0], cycles * fuel[1]))
                        if fuel[0] != const.typeStrontiumClathrates:
                            ctinv.Add(itemID, eve.session.shipid, flag=const.flagNone)
                        else:
                            ctinv.Add(itemID, eve.session.shipid, flag=const.flagSecondaryStorage)

            x += 1

        Progress('Adding Fuel...', 'Done!', 1, 1)
        self.Close()


class AssembleWindow(Window):
    __guid__ = 'form.AssembleWindow'
    default_windowID = 'AssembleWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        fileList = attributes.fileList
        self.selected = fileList[0][0] + '.pos'
        self.SetCaption('Assemble Starbase')
        self.MakeUnResizeable()
        self.SetMinSize([256, 256], 1)
        guts = Container(parent=self.sr.main, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), align=uiconst.TOALL)
        Combo(label='Select POS file', parent=guts, options=fileList, name='fileselect', select=0, align=uiconst.TOTOP, pos=(0, 20, 0, 0), width=200, callback=self.OnComboChange)
        scroll = eveScroll.Scroll(parent=guts, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        scrolllist = []
        for cfgname, var, label, group in [['posTowerAnchor',
          'TowerAnchor',
          'Anchor Control Tower',
          None],
         ['posTowerFuel',
          'TowerFuel',
          'Fuel Control Tower (for onlining)',
          None],
         ['posTowerOnline',
          'TowerOnline',
          'Online Control Tower',
          None],
         ['posStructAnchor',
          'StructAnchor',
          'Anchor All Structures',
          None],
         ['posStructFuel',
          'StructFuel',
          'Fuel Control Tower (for structures)',
          None],
         ['posStructOnline',
          'StructOnline',
          'Online All Structures',
          None],
         ['posArmWeapons',
          'ArmWeapons',
          'Arm Weapon Batteries',
          None]]:
            le = GetFromClass(CheckboxEntry, {'label': label,
             'checked': True,
             'cfgname': cfgname,
             'retval': var,
             'group': group,
             'OnChange': self.CheckBoxChange})
            scrolllist.append(le)
            setattr(self, var, True)
            setattr(self, var + 'LE', le)

        scroll.Load(contentList=scrolllist)
        buttons = [['Execute',
          self.Execute,
          None,
          81], ['Cancel',
          self.Cancel,
          None,
          81]]
        self.sr.main.children.insert(0, ButtonGroup(btns=buttons))

    def Cancel(self, *args):
        self.Close()

    def Execute(self, *args):
        INSIDERDIR = sm.GetService('insider').GetInsiderDir()
        TARGET = os.path.join(INSIDERDIR, self.selected)
        Starbase().ImportFromFile(TARGET).Assemble(stepSelection=self.__dict__)
        AssembleWindow.CloseIfOpen()

    def Set(self, state, list):
        for x in list:
            le = getattr(self, x + 'LE')
            p = le.panel
            if p:
                p.sr.checkbox.SetChecked(state)
            le.checked = state

    def CheckBoxChange(self, checkbox, node, *args):
        name = node.retval
        setattr(self, name, checkbox.checked)
        if name == 'TowerAnchor':
            if not checkbox.checked:
                self.Set(False, ['TowerFuel',
                 'TowerOnline',
                 'StructAnchor',
                 'StructFuel',
                 'StructOnline',
                 'ArmWeapons'])
        elif name == 'TowerFuel':
            if checkbox.checked:
                self.Set(True, ['TowerAnchor'])
            else:
                self.Set(False, ['TowerOnline',
                 'StructAnchor',
                 'StructFuel',
                 'StructOnline',
                 'ArmWeapons'])
        elif name == 'TowerOnline':
            if checkbox.checked:
                self.Set(True, ['TowerAnchor', 'TowerFuel'])
            else:
                self.Set(False, ['StructAnchor',
                 'StructFuel',
                 'StructOnline',
                 'ArmWeapons'])
        elif name == 'StructAnchor':
            if checkbox.checked:
                self.Set(True, ['TowerAnchor', 'TowerFuel', 'TowerOnline'])
            else:
                self.Set(False, ['StructFuel', 'StructOnline', 'ArmWeapons'])
        elif name == 'StructFuel':
            if checkbox.checked:
                self.Set(True, ['TowerAnchor',
                 'TowerFuel',
                 'TowerOnline',
                 'StructAnchor'])
            else:
                self.Set(False, ['StructOnline', 'ArmWeapons'])
        elif name == 'StructOnline':
            if checkbox.checked:
                self.Set(True, ['TowerAnchor',
                 'TowerFuel',
                 'TowerOnline',
                 'StructAnchor',
                 'StructFuel'])
            else:
                self.Set(False, ['ArmWeapons'])
        elif name == 'ArmWeapons':
            if checkbox.checked:
                self.Set(True, ['TowerAnchor',
                 'TowerFuel',
                 'TowerOnline',
                 'StructAnchor',
                 'StructFuel',
                 'StructOnline'])

    def OnComboChange(self, combo, header, value, *args):
        self.selected = header + '.pos'


SERVICENAME = 'poser'

class PoserService(Service):
    __module__ = __name__
    __doc__ = 'Ultimate starbase setup tool'
    __exportedcalls__ = {'Show': []}
    __notifyevents__ = ['ProcessRestartUI']
    __dependencies__ = []
    __guid__ = 'svc.poser'
    __servicename__ = SERVICENAME
    __displayname__ = SERVICENAME.capitalize()

    def Run(self, *args):
        self.wnd = None
        self.state = SERVICE_START_PENDING
        godma = sm.GetService('godma')
        self.structureTypeID = {}
        self.ammo = {}
        for typeID in evetypes.Iterate():
            categoryID = evetypes.GetCategoryID(typeID)
            if categoryID == const.categoryStarbase:
                self.structureTypeID[evetypes.GetName(typeID).lower().replace(' ', '')] = typeID
            elif categoryID == const.categoryCharge:
                groupID = evetypes.GetGroupID(typeID)
                if self.ammo.has_key(groupID):
                    self.ammo[groupID].append(godma.GetType(typeID))
                else:
                    self.ammo[groupID] = [godma.GetType(typeID)]

        blue.pyos.BeNice()
        self.state = SERVICE_RUNNING

    def RoleCheck(self, *roleSets):
        for roleNames in roleSets:
            flags = 0
            for roleName in roleNames:
                flags += globals()[roleName]

            if eve.session.role & flags == flags:
                return True

        summary = []
        for roleNames in roleSets:
            summary.append('<br>- '.join(roleNames))

        sm.GetService('gameui').MessageBox(title='Missing Roles', text='You require the following role(s) to use this function:<br>-  %s' % '<br><br>Or the following role(s):<br>- '.join(summary), buttons=uiconst.OK, icon=uiconst.INFO)

    def FindTypeID(self, name):
        return self.structureTypeID.get(name.lower().replace(' ', ''), None)

    def GetAmmo(self):
        return self.ammo

    def Show(self):
        if self.wnd and not self.wnd.destroyed:
            self.wnd.Maximize()
            return

        def MakeButton1(where, x, y, map, size, function, label, hint = None):
            return ButtonIcon(name=label, parent=where, align=uiconst.TOPLEFT, pos=(x,
             y,
             size,
             size), texturePath=map, iconSize=size, hint=hint, func=function, args=())

        self.wnd = wnd = Window.Open(windowID=SERVICENAME)
        wnd._OnClose = self.Hide
        wnd.sr.main = wnd.GetChild('main')
        wnd.SetCaption('Poser')
        x = const.defaultPadding
        y = const.defaultPadding
        size = 32
        labelwidth = 128
        for icon, label, func in [['res:/UI/Texture/Icons/41_64_2.png', 'Assemble Starbase', self.Assemble],
         ['res:/UI/Texture/Icons/57_64_14.png', 'Store Starbase', self.Store],
         ['res:/UI/Texture/Icons/24_64_5.png', 'Fuel Tower - Cycles', self.Fuel],
         ['res:/UI/Texture/Icons/24_64_5.png', 'Fuel Tower - Full', lambda : sm.GetService('slash').SlashCmd('/pos fuel')],
         ['res:/UI/Texture/Icons/56_64_2.png', 'Nuke Structures', lambda : sm.GetService('gridutils').NukeStructures()],
         ['res:/UI/Texture/Icons/58_64_2.png', 'Anchor All', lambda : sm.GetService('slash').SlashCmd('/pos anchor all')],
         ['res:/UI/Texture/Icons/58_64_15.png', 'Unanchor All', lambda : sm.GetService('slash').SlashCmd('/pos unanchor all')],
         ['res:/UI/Texture/Icons/41_64_10.png', 'Online All', lambda : sm.GetService('slash').SlashCmd('/pos online all')],
         ['res:/UI/Texture/Icons/41_64_11.png', 'Offline All', lambda : sm.GetService('slash').SlashCmd('/pos offline all')],
         ['res:/UI/Texture/Icons/23_64_3.png', 'Reinforce', lambda : sm.GetService('slash').SlashCmd('/pos reinforce all')],
         ['res:/UI/Texture/Icons/56_64_10.png', 'Interrupt', lambda : sm.GetService('slash').SlashCmd('/pos interrupt all')]]:
            MakeButton1(wnd.sr.main, x, y, icon, size, func, label, label)
            if ORIENTATION == 0:
                eveLabel.Label(text=label, parent=wnd.sr.main, width=200, left=x + size + 6, top=y + size / 2 - 6, color=None, state=uiconst.UI_DISABLED)
                y += size
            else:
                x += size

        if ORIENTATION == 0:
            width = 40 + const.defaultPadding + size - 1 + labelwidth + const.defaultPadding
            height = 60 + const.defaultPadding + y + const.defaultPadding
        else:
            width = 20 + const.defaultPadding + x - 1 + const.defaultPadding
            height = 60 + const.defaultPadding + size + const.defaultPadding
        wnd.SetMinSize([width, height])
        wnd.SetFixedWidth(width)
        wnd.SetFixedHeight(height)
        wnd.MakeUnResizeable()
        wnd.Maximize(1)

    def Hide(self, *args):
        if self.wnd:
            self.wnd.Close()
            self.wnd = None

    def ProcessRestartUI(self):
        if self.wnd:
            self.Hide()
            self.Show()

    def Assemble(self, *args):
        INSIDERDIR = sm.GetService('insider').GetInsiderDir()
        if idCheckers.IsNPC(eve.session.corpid):
            info = "You can't be in an NPC corporation and expect to use POS's"
            raise UserError('CustomInfo', {'info': info})
            return
        if not self.RoleCheck(['ROLE_WORLDMOD']):
            return
        fileList = []
        if os.path.exists(INSIDERDIR) == False:
            os.mkdir(INSIDERDIR)
        else:
            files = os.listdir(INSIDERDIR)
            for fileName in files:
                if fileName[-4:] == '.pos':
                    fileList.append((fileName[:-4], fileName))

        if not fileList:
            info = "No '.pos' file found. POSer files must be located in:<br>'%s...'" % INSIDERDIR
            raise UserError('CustomInfo', {'info': info})
            return
        wnd = AssembleWindow.Open(fileList=fileList)
        wnd.ShowModal()

    def Store(self, *args):
        insiderDir = sm.GetService('insider').GetInsiderDir()
        s = Starbase()
        s.ImportFromEnvironment()
        filename = utilWindows.NamePopup(caption='Store Starbase', label='Enter filename:', setvalue='', maxLength=32)
        if not filename:
            return
        filename = os.path.join(insiderDir, filename)
        if not filename:
            return
        if filename[:4].lower() != '.pos':
            filename += '.pos'
        s.ExportAsFile(filename)

    def Fuel(self, *args):
        wnd = FuelWindow.Open()
        wnd.ShowModal()
