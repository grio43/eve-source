#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\targetInBar.py
import _weakref
import math
import random
import blue
import evetypes
import localization
import telemetry
import trinity
import uthread
import utillib
from carbon.common.script.util import commonutils, timerstuff
from carbon.common.script.util.format import FmtDist
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from eve.client.script.parklife import states as state
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetIconColor
from eve.client.script.ui.inflight.bracketsAndTargets.targetOnBracket import ActiveTargetOnBracket
from eve.client.script.ui.inflight.bracketsAndTargets.weaponIcons import FighterAbilityWeapon, Weapon
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIcon
from eve.client.script.ui.util import uix
from eveservices.menu import GetMenuService
from gametime import GetDurationInClient
from spacecomponents.client.messages import MSG_ON_TARGET_BRACKET_ADDED, MSG_ON_TARGET_BRACKET_REMOVED
accuracyThreshold = 0.8
SHIELD = 0
ARMOR = 1
HULL = 2
HOVERTIME = 250

class TargetInBar(ContainerAutoSize):
    __guid__ = 'uicls.TargetInBar'
    __notifyevents__ = ['ProcessShipEffect',
     'OnStateChange',
     'OnJamStart',
     'OnJamEnd',
     'OnSlimItemChange',
     'OnDroneStateChange2',
     'OnDroneControlLost',
     'OnStateSetupChange',
     'OnSetPlayerStanding',
     'OnItemNameChange',
     'OnUIRefresh',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnSuspectsAndCriminalsUpdate',
     'OnDisapprovalUpdate',
     'OnCrimewatchEngagementUpdated']

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.lastDistance = None
        self.sr.updateTimer = None
        self.drones = {}
        self.activeModules = set([])
        self.lastDataUsedForLabel = None
        self.lastTextUsedForLabel = None
        self.lastTextUsedDistance = None
        self.lastTextUsedForShipType = None
        self.itemID = None
        self.weaponsOnTarget = {}
        self.jammingModules = {}
        self.innerHealthBorder = pow(28, 2)
        self.outerHealthBorder = pow(42, 2)
        self._hoverThread = None
        self.fleetTag = None

    def OnUIRefresh(self):
        self.Flush()
        self.init()
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(self.id)
        self.Startup(slimItem)

    def GetTargetDragData(self, *args):
        if settings.user.ui.Get('targetPositionLocked', 0):
            return []
        return [self]

    def Startup(self, slimItem):
        sm.RegisterNotify(self)
        GetShipFighterState().ConnectFighterTargetUpdatedHandler(self._OnFighterTargetUpdate)
        self.ball = _weakref.ref(sm.GetService('michelle').GetBall(slimItem.itemID))
        self.slimItem = _weakref.ref(slimItem)
        self.id = slimItem.itemID
        self.itemID = slimItem.itemID
        self.typeID = slimItem.typeID
        self.updatedamage = slimItem.categoryID not in (const.categoryAsteroid, const.categoryFighter) and slimItem.groupID not in (const.groupHarvestableCloud, const.groupOrbitalTarget)
        self.AddUIObjects(slimItem, self.itemID)
        iconPar = self.sr.iconPar
        barAndImageCont = self.barAndImageCont
        barAndImageCont.isDragObject = True
        barAndImageCont.GetDragData = self.GetTargetDragData
        barAndImageCont.OnMouseDown = self.OnTargetMouseDown
        barAndImageCont.OnClick = self.OnTargetClick
        barAndImageCont.GetMenu = self.GetTargetMenu
        barAndImageCont.OnMouseEnter = self.OnTargetMouseEnter
        barAndImageCont.OnMouseExit = self.OnTargetMouseExit
        self.sr.activeTarget = ActiveTargetOnBracket(parent=iconPar, itemID=self.itemID)
        self.slimForFlag = slimItem
        self.SetStandingIcon()
        if slimItem.categoryID == const.categoryEntity:
            self.SetBracketIcon()
        self.SetFleetTag(sm.GetService('fleet').GetTargetTag(self.itemID))
        self.sr.hilite = Sprite(name='hiliteSprite', parent=iconPar, left=-3, top=-3, width=100, height=100, texturePath='res:/UI/Texture/classes/Target/targetUnderlay.png', color=(1.0, 1.0, 1.0, 0.05))
        self.sr.activeTarget.RotateArrows()
        labelClass = eveLabel.EveLabelSmall
        labelContainer = ContainerAutoSize(parent=self, name='labelContainer', align=uiconst.TOTOP)
        self.labelContainer = labelContainer
        self.sr.label = labelClass(text=' ', parent=labelContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.label2 = labelClass(text=' ', parent=labelContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.shipLabel = labelClass(text=' ', parent=labelContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.distanceLabel = labelClass(text=' ', parent=labelContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, maxLines=1)
        self.SetTargetLabel()
        self.sr.assignedPar = Container(name='assignedPar', align=uiconst.TOTOP, parent=self, height=32)
        self.sr.assigned = Container(name='assigned', align=uiconst.CENTERTOP, parent=self.sr.assignedPar, height=32)
        self.sr.updateTimer = timerstuff.AutoTimer(random.randint(750, 1000), self.UpdateData)
        self.UpdateData()
        selected = sm.GetService('stateSvc').GetExclState(state.selected)
        self.Select(selected == slimItem.itemID)
        hilited = sm.GetService('stateSvc').GetExclState(state.mouseOver)
        self.Hilite(hilited == slimItem.itemID)
        activeTargetID = sm.GetService('target').GetActiveTargetID()
        self.ActiveTarget(activeTargetID == slimItem.itemID)
        drones = sm.GetService('michelle').GetDrones()
        for key in drones:
            droneState = drones[key]
            if droneState.targetID == self.id:
                self.drones[droneState.droneID] = droneState.typeID

        self.UpdateDrones()
        for moduleInfo in sm.GetService('godma').GetStateManager().GetActiveModulesOnTargetID(slimItem.itemID):
            if moduleInfo:
                moduleID = moduleInfo.itemID
                if moduleID and moduleID not in self.activeModules:
                    self.AddWeapon(moduleInfo)

        self._AddActiveFighterAbilities()

    def AddUIDeathObjects(self, discSize):
        self.skullSprite = Sprite(name='skullSprite', parent=self.sr.iconPar, align=uiconst.CENTER, texturePath='res:/UI/Texture/Icons/target_killed_skull.png', width=64, height=64)
        self.skullSprite.display = False
        self.discSprite = Sprite(name='discSprite', parent=self.sr.iconPar, align=uiconst.CENTER, texturePath='res:/UI/Texture/Icons/target_killed.png', width=discSize, height=discSize)
        self.discSprite.display = False
        self.lineSprite = Sprite(name='lineSprite', parent=self.barAndImageCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/Icons/target_killed_line.png', width=100, height=100)
        self.lineSprite.display = False

    def AddUIObjects(self, slimItem, itemID, *args):
        barAndImageCont = Container(parent=self, name='barAndImageCont', align=uiconst.TOTOP, height=100, state=uiconst.UI_NORMAL)
        self.barAndImageCont = barAndImageCont
        self.iconSize = iconSize = 94
        iconPar = Transform(parent=barAndImageCont, name='iconPar', width=iconSize, height=iconSize, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
        iconPar.scalingCenter = (0.5, 0.5)
        self.sr.iconPar = iconPar
        self.AddUIDeathObjects(94)
        maskSize = 50
        iconPadding = (iconSize - maskSize) / 2
        icon = eveIcon.Icon(parent=iconPar, left=iconPadding, top=iconPadding, width=maskSize, height=maskSize, typeID=slimItem.typeID, textureSecondaryPath='res:/UI/Texture/classes/Target/shipMask.png', color=(1.0, 1.0, 1.0, 1.0), blendMode=1, spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED, ignoreSize=True)
        if slimItem.groupID == const.groupOrbitalTarget:
            sm.GetService('photo').GetPortrait(slimItem.ownerID, 64, icon)
        if self.updatedamage:
            self.healthBar = TargetHealthBars(parent=iconPar, itemID=itemID)
        circle = Sprite(name='circle', align=uiconst.CENTER, parent=iconPar, width=iconSize + 2, height=iconSize + 2, texturePath='res:/UI/Texture/classes/Target/outerCircle.png', color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_DISABLED)
        self.circle = circle

    def OnItemNameChange(self, *args):
        uthread.new(self.SetTargetLabel)

    def SetTargetLabel(self):
        self.label = uix.GetSlimItemName(self.slimForFlag)
        if self.slimForFlag.corpID:
            self.label = localization.GetByLabel('UI/Inflight/Target/TargetLabelWithTicker', target=uix.GetSlimItemName(self.slimForFlag), ticker=cfg.corptickernames.Get(self.slimForFlag.corpID).tickerName)
        if self.slimForFlag.corpID and self.slimForFlag.typeID and self.slimForFlag.categoryID == const.categoryShip:
            self.shipLabel = evetypes.GetName(self.slimForFlag.typeID)
        else:
            self.shipLabel = ''
        self.UpdateData()

    def OnSetPlayerStanding(self, *args):
        self.SetStandingIcon()

    def OnStateSetupChange(self, *args):
        self.SetStandingIcon()

    def SetStandingIcon(self):
        stateMgr = sm.GetService('stateSvc')
        flag = stateMgr.CheckStates(self.slimForFlag, 'flag')
        self.standingIcon = AddAndSetFlagIcon(parentCont=self.sr.iconPar, flag=flag, align=uiconst.CENTERBOTTOM, top=8, left=0, showHint=False)

    def SetBracketIcon(self):
        slimItem = self.slimItem()
        if not slimItem:
            return
        bracketData = sm.GetService('bracket').GetBracketDataByTypeID(slimItem.typeID)
        if not bracketData:
            return
        texturePath = bracketData.texturePath
        if not texturePath:
            return
        iconColor = GetIconColor(slimItem)
        if not getattr(self, 'bracketIcon', None) or self.bracketIcon.destroyed:
            self.bracketIcon = Sprite(parent=self.sr.iconPar, align=uiconst.CENTERBOTTOM, pos=(0, 5, 16, 16))
        self.bracketIcon.SetRGBA(*iconColor)
        self.bracketIcon.SetTexturePath(texturePath)

    def OnSuspectsAndCriminalsUpdate(self, criminalizedCharIDs, decriminalizedCharIDs):
        return self._UpdateOnSuspectCriminalAndDisapprovalChanges(criminalizedCharIDs, decriminalizedCharIDs)

    def OnDisapprovalUpdate(self, newCharIDs, removedCharIDs):
        return self._UpdateOnSuspectCriminalAndDisapprovalChanges(newCharIDs, removedCharIDs)

    def _UpdateOnSuspectCriminalAndDisapprovalChanges(self, newCharIDs, removedCharIDs):
        if self.slimForFlag.charID in newCharIDs or self.slimForFlag.charID in removedCharIDs:
            self.SetStandingIcon()

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        if self.slimForFlag.charID == otherCharId:
            self.SetStandingIcon()

    def OnFleetJoin_Local(self, member, *args):
        if session.charid == member.charID or self.slimForFlag.charID == member.charID:
            self.SetStandingIcon()

    def OnFleetLeave_Local(self, member, *args):
        if session.charid == member.charID or self.slimForFlag.charID == member.charID:
            self.SetStandingIcon()

    def SetFleetTag(self, fleetTag):
        if not session.fleetid or fleetTag in (None, ''):
            if self.fleetTag:
                self.fleetTag.Close()
                self.fleetTag = None
            return
        if self.fleetTag is None or self.fleetTag.destroyed:
            self.fleetTag = eveLabel.EveLabelMediumBold(parent=self.sr.iconPar, align=uiconst.CENTERBOTTOM, left=15, top=8, idx=0)
        self.fleetTag.text = fleetTag

    def OnSlimItemChange(self, oldSlim, newSlim):
        uthread.new(self._OnSlimItemChange, oldSlim, newSlim)

    def _OnSlimItemChange(self, oldSlim, newSlim):
        if self.itemID != oldSlim.itemID or self.destroyed:
            return
        self.itemID = newSlim.itemID
        self.slimItem = _weakref.ref(newSlim)
        if oldSlim.corpID != newSlim.corpID or oldSlim.charID != newSlim.charID:
            self.label = uix.GetSlimItemName(newSlim)
            self.UpdateData()

    def OnStateChange(self, itemID, flag, true, *args):
        if not self.destroyed:
            uthread.new(self._OnStateChange, itemID, flag, true)

    def _OnStateChange(self, itemID, flag, true):
        if self.destroyed or self.itemID != itemID:
            return
        if flag == state.mouseOver:
            self.Hilite(true)
        elif flag == state.selected:
            self.Select(true)
        elif flag == state.activeTarget:
            self.ActiveTarget(true)

    def Hilite(self, state):
        if self.sr.hilite:
            self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]

    def Select(self, state):
        pass

    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        if targetBallID != self.id:
            return
        durationInClient = GetDurationInClient(startTime, duration)
        if durationInClient < 0.0:
            return
        moduleInfo = self.GetModuleInfo(moduleID)
        if moduleInfo and moduleID not in self.activeModules:
            self.AddWeapon(moduleInfo)
        self.jammingModules[moduleID] = (sourceBallID,
         moduleID,
         targetBallID,
         startTime,
         duration)
        self.StartTimer(moduleID, durationInClient)

    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not self or self.destroyed:
            return
        if moduleID in self.jammingModules:
            moduleIconCont = self.GetWeapon(moduleID)
            if moduleIconCont:
                if moduleIconCont.icon:
                    moduleIconCont.StopAnimations()
                    moduleIconCont.opacity = 1.0
                    moduleIconCont.icon.SetRGBA(1, 1, 1, 1.0)
                    moduleIconCont.icon.baseAlpha = 0.3
                self.RemoveTimer(moduleID)
            del self.jammingModules[moduleID]

    def StartTimer(self, moduleID, duration, *args):
        moduleIconCont = self.GetWeapon(moduleID)
        if moduleIconCont and moduleIconCont.icon and moduleIconCont.timer:
            moduleIconCont.icon.SetRGBA(1, 1, 1, 1.0)
            moduleIconCont.icon.baseAlpha = 1.0
            moduleIconCont.timer.StartTimer(duration)

    def RemoveTimer(self, moduleID, *args):
        moduleIconCont = self.GetWeapon(moduleID)
        if moduleIconCont and moduleIconCont.icon and moduleIconCont.timer:
            moduleIconCont.icon.SetRGBA(1, 1, 1, moduleIconCont.icon.baseAlpha)

    def _HoverThread(self):
        while True:
            blue.synchro.SleepWallclock(HOVERTIME)
            self.OnTargetMouseHover()

    def KillHoverThread(self, *args):
        if self._hoverThread:
            self._hoverThread.kill()
            self._hoverThread = None

    def OnTargetMouseHover(self, *args):
        if not self.sr.iconPar or self.sr.iconPar.destroyed or not getattr(self, 'healthBar', None):
            self.KillHoverThread()
            return
        if self.healthBar.destroyed:
            self.KillHoverThread()
            return
        l, t, w, h = self.sr.iconPar.GetAbsolute()
        cX = w / 2 + l
        cY = h / 2 + t
        x = uicore.uilib.x - cX
        y = uicore.uilib.y - cY
        if y > 55:
            self.barAndImageCont.SetHint('')
            return
        length2 = pow(x, 2) + pow(y, 2)
        if length2 < self.innerHealthBorder or length2 > self.outerHealthBorder:
            self.barAndImageCont.SetHint('')
            return
        rad = math.atan2(y, x)
        degrees = 180 * rad / math.pi
        if degrees < 0:
            degrees = 360 + degrees
        if degrees > 45 and degrees < 135:
            return
        self.SetHintText()

    def SetHintText(self):
        hintList = []
        percLeft = self.healthBar.GetDamageHint(SHIELD)
        if percLeft is not None:
            percLeft = math.floor(100 * percLeft)
            hintList.append(localization.GetByLabel('UI/Inflight/Target/GaugeShieldRemaining', percentage=percLeft))
        percLeft = self.healthBar.GetDamageHint(ARMOR)
        if percLeft is not None:
            percLeft = math.floor(100 * percLeft)
            hintList.append(localization.GetByLabel('UI/Inflight/Target/GaugeArmorRemaining', percentage=percLeft))
        percLeft = self.healthBar.GetDamageHint(HULL)
        if percLeft is not None:
            percLeft = math.floor(100 * percLeft)
            hintList.append(localization.GetByLabel('UI/Inflight/Target/GaugeStructureRemaining', percentage=percLeft))
        hint = '<br>'.join(hintList)
        self.barAndImageCont.SetHint(hint)

    def GetShipID(self):
        return self.itemID

    def GetIcon(self, icon, typeID, size):
        if not self.destroyed:
            icon.LoadIconByTypeID(typeID)
            icon.SetSize(size, size)

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)
        self.sr.updateTimer = None
        GetShipFighterState().DisconnectFighterTargetUpdatedHandler(self._OnFighterTargetUpdate)

    def _AddActiveFighterAbilities(self):
        abilitiesOnTarget = GetShipFighterState().abilityTargetTracker.GetFighterAbilitiesForTarget(self.itemID)
        for fighterID, abilitySlotID in abilitiesOnTarget:
            self._AddFighterAbility(fighterID, abilitySlotID)

        self.ArrangeWeapons()
        self.SetSizeAutomatically()
        uthread.new(sm.GetService('target').AdjustRowSize)

    def _OnFighterTargetUpdate(self, fighterID, abilitySlotID, targetID):
        if targetID != self.itemID:
            return
        abilitiesOnTarget = GetShipFighterState().abilityTargetTracker.GetFighterAbilitiesForTarget(self.itemID)
        if (fighterID, abilitySlotID) in abilitiesOnTarget:
            if (fighterID, abilitySlotID) not in self.activeModules:
                self._AddFighterAbility(fighterID, abilitySlotID)
        else:
            self._RemoveFighterAbility(fighterID, abilitySlotID)
        self.ArrangeWeapons()
        self.SetSizeAutomatically()
        uthread.new(sm.GetService('target').AdjustRowSize)

    def _AddFighterAbility(self, fighterID, abilitySlotID):
        cont = FighterAbilityWeapon(parent=self.sr.assigned, fighterID=fighterID, abilitySlotID=abilitySlotID)
        self.activeModules.add((fighterID, abilitySlotID))

    def _RemoveFighterAbility(self, fighterID, abilitySlotID):
        iconCont = self.GetWeapon((fighterID, abilitySlotID))
        if iconCont:
            iconCont.Close()
        self.activeModules.discard((fighterID, abilitySlotID))

    def ProcessShipEffect(self, godmaStm, effectState):
        slimItem = self.slimItem()
        if slimItem and effectState.environment[3] == slimItem.itemID:
            if effectState.start:
                if self.GetWeapon(effectState.itemID):
                    return
                moduleInfo = self.GetModuleInfo(effectState.itemID)
                if moduleInfo:
                    self.AddWeapon(moduleInfo)
            else:
                self.RemoveWeapon(effectState.itemID)

    def AddWeapon(self, moduleInfo):
        if self is None or self.destroyed:
            return
        cont = Weapon(parent=self.sr.assigned, moduleInfo=moduleInfo, getJammingInfoFunc=self.GetJammingModuleInfo)
        self.activeModules.add(moduleInfo.itemID)
        self.ArrangeWeapons()
        self.SetSizeAutomatically()
        uthread.new(sm.GetService('target').AdjustRowSize)

    def GetJammingModuleInfo(self, moduleID):
        if moduleID in self.jammingModules:
            sourceBallID, moduleID, targetBallID, startTime, duration = self.jammingModules[moduleID]
            return utillib.KeyVal(startTime=startTime, duration=duration)

    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)

    def RemoveWeapon(self, moduleID):
        iconCont = self.GetWeapon(moduleID)
        if iconCont:
            iconCont.Close()
        self.activeModules.discard(moduleID)
        self.ArrangeWeapons()
        self.SetSizeAutomatically()
        uthread.new(sm.GetService('target').AdjustRowSize)

    def ArrangeWeapons(self):
        if self and not self.destroyed and self.sr.assigned:
            numWeapons = len(self.sr.assigned.children)
            if numWeapons > 2:
                size = 24
            else:
                size = 32
            left = 0
            top = 0
            row = 0
            column = -1
            maxColumns = 4
            for cont in self.sr.assigned.children:
                if isinstance(cont, Frame):
                    continue
                column += 1
                if column >= maxColumns:
                    column = 0
                    row += 1
                cont.width = cont.height = size
                cont.left = column * size
                cont.top = row * size
                cont.state = uiconst.UI_PICKCHILDREN

            if row > 0:
                self.sr.assigned.width = maxColumns * size
            else:
                self.sr.assigned.width = size * (column + 1)
            self.sr.assigned.height = max(32, size * (row + 1))
            self.sr.assignedPar.height = self.sr.assigned.height

    def GetWeapon(self, moduleID):
        if self is None or self.destroyed:
            return
        if self.sr.assigned:
            for cont in self.sr.assigned.children:
                if isinstance(cont, Frame):
                    continue
                if cont.sr.moduleID == moduleID:
                    return cont

    def GetModuleInfo(self, moduleID):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            return
        for module in ship.modules:
            if module.itemID == moduleID:
                return module

    def ResetModuleIcon(self, moduleID, *args):
        if moduleID in self.activeModules:
            weapon = self.GetWeapon(moduleID)
            icon = weapon.icon
            icon.SetAlpha(icon.baseAlpha)

    def OnTargetClick(self, *args):
        sm.GetService('stateSvc').SetState(self.itemID, state.selected, 1)
        sm.GetService('stateSvc').SetState(self.itemID, state.activeTarget, 1)
        GetMenuService().TacticalItemClicked(self.itemID)

    def GetTargetMenu(self):
        m = []
        m += GetMenuService().CelestialMenu(self.itemID)
        return m

    def OnTargetMouseDown(self, *args):
        if getattr(self, 'slimItem', None):
            if GetMenuService().TryExpandActionMenu(self.itemID, self.barAndImageCont):
                return

    def OnBeginMoveTarget(self, *args):
        sm.GetService('target').OnMoveTarget(self)

    def OnTargetMouseEnter(self, *args):
        sm.GetService('stateSvc').SetState(self.id, state.mouseOver, 1)
        if self._hoverThread is None:
            self._hoverThread = uthread.new(self._HoverThread)

    def OnTargetMouseExit(self, *args):
        sm.GetService('stateSvc').SetState(self.itemID, state.mouseOver, 0)
        self.KillHoverThread()

    @telemetry.ZONE_METHOD
    def UpdateData(self):
        ball = self.ball()
        if not ball:
            return
        dist = ball.surfaceDist
        distanceInMeters = int(dist)
        if self.label != self.lastTextUsedForLabel:
            self.SetNameLabels(fullLabel=self.label)
            self.lastTextUsedForLabel = self.label
        if distanceInMeters != self.lastTextUsedDistance:
            self.sr.distanceLabel.text = '<center>' + FmtDist(dist)
            self.FadeText(self.sr.label2)
            self.lastTextUsedDistance = distanceInMeters
        if self.shipLabel != self.lastTextUsedForShipType:
            if self.shipLabel:
                self.sr.shipLabel.display = True
                self.sr.shipLabel.text = '<center>' + self.shipLabel
                self.FadeText(self.sr.shipLabel)
                self.lastTextUsedForShipType = self.shipLabel
            else:
                self.sr.shipLabel.text = ''
                self.sr.shipLabel.display = False

    def SetNameLabels(self, fullLabel, *args):
        hintMarkupStart = ''
        hintMarkupEnd = ''
        localizedHintPos = fullLabel.find('<localized hint')
        if localizedHintPos >= 0:
            strippedLabel = commonutils.StripTags(fullLabel, stripOnly=['localized'])
            hintEndIndex = fullLabel.find('">')
            if hintEndIndex > 0:
                hintMarkupStart = fullLabel[localizedHintPos:hintEndIndex + 2]
                hintMarkupEnd = '</localized>'
        else:
            strippedLabel = fullLabel
        self.sr.label.text = strippedLabel
        indexAtMaxLenght = self.sr.label.GetIndexUnderPos(self.width)
        if indexAtMaxLenght[0] < len(strippedLabel):
            lastBreak = strippedLabel.rfind(' ', 0, indexAtMaxLenght[0])
            if lastBreak != -1:
                self.sr.label.text = strippedLabel[:lastBreak]
            self.sr.label2.text = '<center>' + hintMarkupStart + strippedLabel[lastBreak:].strip() + hintMarkupEnd
            self.FadeText(self.sr.label2)
            self.sr.label2.display = True
        else:
            self.sr.label2.text = ''
            self.sr.label2.display = False
        self.sr.label.text = '<center>' + hintMarkupStart + self.sr.label.text + hintMarkupEnd
        self.lastTextUsedForLabel = self.label

    def FadeText(self, textLabel, *args):
        maxFadeWidth = 10
        fadeEnd = self.width - maxFadeWidth
        textLabel.SetRightAlphaFade(fadeEnd=fadeEnd, maxFadeWidth=maxFadeWidth)

    def ActiveTarget(self, true):
        if self.destroyed:
            return
        targetSvc = sm.GetService('target')
        if true:
            if not targetSvc.disableSpinnyReticule:
                self.sr.activeTarget.state = uiconst.UI_DISABLED
            self.sr.iconPar.opacity = 1.0
            self.circle.opacity = 0.5
        else:
            self.sr.iconPar.width = self.sr.iconPar.height = self.iconSize
            self.sr.activeTarget.state = uiconst.UI_HIDDEN
            self.sr.iconPar.opacity = 0.8
            self.circle.opacity = 0.25

    def OnDroneStateChange2(self, itemID, oldActivityState, activityState):
        michelle = sm.GetService('michelle')
        droneState = michelle.GetDroneState(itemID)
        if activityState in (const.entityCombat,
         const.entityEngage,
         const.entityMining,
         const.entitySalvaging):
            if droneState and droneState.targetID == self.id:
                self.drones[itemID] = droneState.typeID
            elif itemID in self.drones:
                del self.drones[itemID]
        elif itemID in self.drones:
            del self.drones[itemID]
        self.UpdateDrones()

    def OnDroneControlLost(self, droneID):
        if droneID in self.drones:
            del self.drones[droneID]
        self.UpdateDrones()

    def UpdateDrones(self):
        if not self.drones:
            self.RemoveWeapon('drones')
            return
        droneIconCont = self.GetWeapon('drones')
        if not droneIconCont:
            cont = Container(parent=self.sr.assigned, align=uiconst.RELATIVE, width=32, height=32, state=uiconst.UI_HIDDEN)
            icon = Sprite(parent=cont, align=uiconst.TOALL, width=0, height=0, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Icons/56_64_5.png')
            cont.sr.moduleID = 'drones'
            cont.icon = icon
            icon.sr.moduleID = 'drones'
            self.ArrangeWeapons()
        self.UpdateDroneHint()

    def UpdateDroneHint(self):
        dronesByTypeID = {}
        droneIcon = self.GetWeapon('drones')
        if droneIcon is None:
            return
        for droneID, droneTypeID in self.drones.iteritems():
            if droneTypeID not in dronesByTypeID:
                dronesByTypeID[droneTypeID] = 0
            dronesByTypeID[droneTypeID] += 1

        hintLines = []
        for droneTypeID, number in dronesByTypeID.iteritems():
            hintLines.append(localization.GetByLabel('UI/Inflight/Target/DroneHintLine', drone=droneTypeID, count=number))

        droneIcon.icon.hint = localization.GetByLabel('UI/Inflight/Target/DroneHintLabel', droneHintLines='<br>'.join(hintLines))

    def StartDeathAnimation(self):
        self.state = uiconst.UI_DISABLED
        if hasattr(self, 'healthBar'):
            self.healthBar.SetDamage([0.0,
             0.0,
             0.0,
             0.0,
             0.0])
        blue.synchro.SleepSim(random.random() * 200.0)
        sm.GetService('audio').SendUIEvent('target_destroy_play')
        self.discSprite.display = True
        discCurve = ((0.0, (1.0, 0.0, 0.0, 0.0)), (0.1, (1.0, 0.0, 0.0, 0.6)), (2.0, (1.0, 0.0, 0.0, 0.6)))
        uicore.animations.SpColorMorphTo(self.discSprite, curveType=discCurve, duration=0.1)
        self.skullSprite.display = True
        uicore.animations.BlinkIn(self, duration=0.2, loops=6, sleep=True)
        uicore.animations.Tr2DScaleTo(self.sr.iconPar, startScale=(1.0, 1.0), endScale=(1.0, 0.0), sleep=True, duration=0.04, curveType=uiconst.ANIM_LINEAR)
        self.sr.iconPar.display = False


class TargetHealthBars(Container):
    __notifyevents__ = ['OnDamageMessage', 'OnDamageMessages']
    default_name = 'targetHealthBars'
    default_width = 94
    default_height = 94
    default_align = uiconst.CENTER
    allHealthTexture = 'res:/UI/Texture/classes/Target/targetBackground.png'
    allHealthMinusShieldTexture = 'res:/UI/Texture/classes/Target/targetBackgroundNoShield.png'
    shieldTextureLeft = 'res:/UI/Texture/classes/Target/shieldLeft.png'
    shieldTextureRight = 'res:/UI/Texture/classes/Target/shieldRight.png'
    armorTextureLeft = 'res:/UI/Texture/classes/Target/armorLeft.png'
    armorTextureRight = 'res:/UI/Texture/classes/Target/armorRight.png'
    hullTextureLeft = 'res:/UI/Texture/classes/Target/hullLeft.png'
    hullTextureRight = 'res:/UI/Texture/classes/Target/hullRight.png'

    def ApplyAttributes(self, attributes):
        self.damageValuseForTooltip = {}
        Container.ApplyAttributes(self, attributes)
        self.itemID = attributes.itemID
        self.sr.damageTimer = timerstuff.AutoTimer(random.randint(750, 1000), self.UpdateDamage)
        self.width = attributes.get('size', self.default_width)
        self.height = attributes.get('size', self.default_height)
        self.shieldBar = self.AddHealthBar(name='shieldBar', texturePathLeft=self.shieldTextureLeft, texturePathRight=self.shieldTextureRight)
        self.armorBar = self.AddHealthBar(name='armorBar', texturePathLeft=self.armorTextureLeft, texturePathRight=self.armorTextureRight)
        self.hullBar = self.AddHealthBar(name='hullBar', texturePathLeft=self.hullTextureLeft, texturePathRight=self.hullTextureRight)
        self.healthBarBackground = Sprite(name='healthBarBackground', parent=self, width=self.width, height=self.height, texturePath=self.allHealthTexture, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.UpdateDamage()
        sm.RegisterNotify(self)
        bp = sm.GetService('michelle').GetBallpark()
        bp.componentRegistry.SendMessageToItem(self.itemID, MSG_ON_TARGET_BRACKET_ADDED, self)

    def SetGaugeTextureForBar(self, name, texturePath):
        if texturePath is None:
            texturePath = 'res:/UI/Texture/classes/Target/gaugeColor.png'
        bar = getattr(self, name)
        bar.leftBar.SetSecondaryTexturePath(texturePath)
        bar.rightBar.SetSecondaryTexturePath(texturePath)

    def AddHealthBar(self, name, texturePathLeft, texturePathRight, *args):
        cont = Container(name=name, parent=self, width=self.width, height=self.height, align=uiconst.CENTER)
        leftBar = Sprite(name='%s_Left' % name, parent=cont, width=self.width, height=self.height, texturePath=texturePathLeft, textureSecondaryPath='res:/UI/Texture/classes/Target/gaugeColor.png', idx=0, blendMode=1, spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED)
        leftBar.baseRotation = 0
        leftBar.rotationSecondary = leftBar.baseRotation
        rightBar = Sprite(name='%s_Right' % name, parent=cont, width=self.width, height=self.height, texturePath=texturePathRight, textureSecondaryPath='res:/UI/Texture/classes/Target/gaugeColor.png', idx=0, blendMode=1, spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED)
        rightBar.baseRotation = -3 / 4.0 * math.pi
        rightBar.rotationSecondary = rightBar.baseRotation
        cont.leftBar = leftBar
        cont.rightBar = rightBar
        return cont

    def UpdateDamage(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            self.sr.damageTimer = None
            return
        dmg = bp.GetDamageState(self.itemID)
        if dmg is not None:
            self.PrepareHint(dmg)
            self.SetDamage(dmg)

    def PrepareHint(self, state):
        for i, layer in enumerate([SHIELD, ARMOR, HULL]):
            if state[i] is None:
                self.damageValuseForTooltip[layer] = None
            else:
                self.damageValuseForTooltip[layer] = max(0, state[i])

    def SetDamage(self, state, *args):
        visible = 0
        healthBars = [self.shieldBar, self.armorBar, self.hullBar]
        fullAnimationTime = 0.4
        for i, healthBar in enumerate(healthBars):
            if state[i] is None:
                healthBar.display = False
            else:
                healthState = state[i]
                healthState = max(0, healthState)
                lastState = getattr(healthBar, 'lastState', None)
                healthBar.lastState = healthState
                leftBar = healthBar.leftBar
                rightBar = healthBar.rightBar
                if lastState:
                    totalChange = healthState - lastState
                    animationTime = max(0.1, fullAnimationTime * abs(totalChange))
                else:
                    animationTime = None
                if healthState <= 0.5:
                    portionOfBar = (0.5 - healthState) / 0.5
                    rotation = leftBar.baseRotation + portionOfBar * 0.75 * math.pi
                    if lastState and lastState > 0.5:
                        below50Damage = lastState - 0.5
                        below50Percentage = float(below50Damage) / abs(totalChange)
                        if animationTime is None:
                            rightBar.rotationSecondary = 0.0
                            leftBar.rotationSecondary = rotation
                        else:
                            curvePoints = ([0, rightBar.rotationSecondary or 0.0], [below50Percentage or 0.0, 0.0])
                            uicore.animations.MorphScalar(rightBar, 'rotationSecondary', duration=animationTime, curveType=curvePoints)
                            curvePoints = ([0, leftBar.rotationSecondary or 0.0], [below50Percentage or 0.0, leftBar.rotationSecondary or 0.0], [1.0, rotation])
                            uicore.animations.MorphScalar(leftBar, 'rotationSecondary', duration=animationTime, curveType=curvePoints)
                    else:
                        rightBar.rotationSecondary = 0
                        if animationTime is None:
                            leftBar.rotationSecondary = rotation
                        else:
                            uicore.animations.MorphScalar(leftBar, 'rotationSecondary', startVal=leftBar.rotationSecondary or 0.0, endVal=rotation, duration=animationTime, curveType=uiconst.ANIM_LINEAR)
                else:
                    portionOfBar = (1 - healthState) / 0.5
                    rotation = rightBar.baseRotation + portionOfBar * 0.75 * math.pi
                    if lastState and lastState <= 0.5:
                        above50Damage = 0.5 - lastState
                        above50Percentage = float(above50Damage) / abs(totalChange)
                        if animationTime is None:
                            leftBar.rotationSecondary = leftBar.baseRotation - 0.02
                            rightBar.rotationSecondary = rotation
                        else:
                            curvePoints = ([0, leftBar.rotationSecondary], [above50Percentage, leftBar.baseRotation - 0.02])
                            uicore.animations.MorphScalar(leftBar, 'rotationSecondary', duration=animationTime, curveType=curvePoints)
                            curvePoints = ([0, rightBar.rotationSecondary], [above50Percentage, rightBar.rotationSecondary], [1.0, rotation])
                            uicore.animations.MorphScalar(rightBar, 'rotationSecondary', duration=animationTime, curveType=curvePoints)
                    else:
                        if animationTime is None:
                            rightBar.rotationSecondary = rotation
                        else:
                            uicore.animations.MorphScalar(rightBar, 'rotationSecondary', startVal=rightBar.rotationSecondary, endVal=rotation, duration=animationTime, curveType=uiconst.ANIM_LINEAR)
                        leftBar.rotationSecondary = leftBar.baseRotation - 0.02
                healthBar.display = True
                visible += 1

        if visible == 0:
            self.healthBarBackground.display = False
        else:
            if visible == 2:
                self.healthBarBackground.SetTexturePath(self.allHealthMinusShieldTexture)
            else:
                self.healthBarBackground.SetTexturePath(self.allHealthTexture)
            self.healthBarBackground.display = True

    def _OnClose(self, *args):
        self.sr.damageTimer = None
        bp = sm.GetService('michelle').GetBallpark()
        bp.componentRegistry.SendMessageToItem(self.itemID, MSG_ON_TARGET_BRACKET_REMOVED)

    def GetDamageHint(self, whichHealthBar, *args):
        return self.damageValuseForTooltip.get(whichHealthBar, 1.0)

    def OnDamageMessages(self, dmgmsgs):
        for msg in dmgmsgs:
            didBlink = self.OnDamageMessage(*msg[1:])
            if didBlink:
                break

    def OnDamageMessage(self, damageMessagesArgs):
        attackType = damageMessagesArgs.get('attackType', 'me')
        if attackType != 'me':
            return False
        damage = damageMessagesArgs.get('damage', 0)
        if damage == 0:
            return False
        target = damageMessagesArgs.get('target', None)
        if target is None:
            return False
        if isinstance(target, long):
            if target == self.itemID:
                self.DoBlink()
                return True
        if isinstance(target, basestring):
            targetID = damageMessagesArgs.get('target_ID', None)
            if targetID == self.itemID:
                self.DoBlink()
                return True
        return False

    def DoBlink(self, *args):
        uicore.animations.FadeTo(self, startVal=1.3, endVal=1.0, duration=0.75, loops=1, curveType=uiconst.ANIM_OVERSHOT)
