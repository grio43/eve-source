#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\weaponIcons.py
import fighters
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight.moduleEffectTimer import ModuleEffectTimer
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronManagementCont import SquadronNumber
from fighters import GetAbilityIDForSlot
from localization import GetByLabel
import blue
from carbonui.uicore import uicore

class FighterAbilityWeapon(Container):
    default_width = 32
    default_height = 32
    default_align = uiconst.RELATIVE
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        fighterID = attributes.fighterID
        abilitySlotID = attributes.abilitySlotID
        fighterState = GetShipFighterState()
        fighter = fighterState.GetFighterInSpaceByID(fighterID)
        fighterTypeID = fighter.typeID
        abilityID = GetAbilityIDForSlot(fighterTypeID, abilitySlotID)
        abilityInfo = fighters.AbilityStorage()[abilityID]
        abilityIconID = abilityInfo.iconID
        self.icon = Icon(parent=self, align=uiconst.TOALL, width=0, height=0, state=uiconst.UI_NORMAL, icon=abilityIconID)
        self.sr.moduleID = (fighterID, abilitySlotID)
        self.sr.fighterID = fighterID
        self.sr.abilitySlotID = abilitySlotID
        self.icon.sr.fighterID = fighterID
        self.icon.sr.abilitySlotID = abilitySlotID
        self.icon.OnClick = self.ClickWeapon
        squadronNumber = SquadronNumber(parent=self, top=-2, left=-4, idx=0)
        squadronNumber.SetColor()
        squadronNumber.SetText(fighter.tubeFlagID)

    def ClickWeapon(self):
        fighterID, abilitySlotID = self.sr.moduleID
        sm.GetService('fighters').DeactivateAbilitySlots([fighterID], abilitySlotID)


class Weapon(Container):
    default_width = 32
    default_height = 32
    default_align = uiconst.RELATIVE
    default_state = uiconst.UI_HIDDEN
    timerRightCounterTexturePath = 'res:/UI/Texture/classes/Target/ecmCounterRight.png'
    timerLeftCounterTexturePath = 'res:/UI/Texture/classes/Target/ecmCounterLeft.png'
    timerCounterGaugeTexturePath = 'res:/UI/Texture/classes/Target/ecmCounterGauge.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        moduleInfo = attributes.moduleInfo
        self.getJammingInfoFunc = attributes.getJammingInfoFunc
        icon = Icon(parent=self, align=uiconst.TOALL, width=0, height=0, state=uiconst.UI_NORMAL, typeID=moduleInfo.typeID)
        self.sr.moduleID = moduleInfo.itemID
        self.icon = icon
        icon.sr.moduleID = moduleInfo.itemID
        icon.OnClick = self.ClickWeapon
        icon.OnMouseEnter = self.OnMouseEnterWeapon
        icon.OnMouseExit = self.OnMouseExitWeapon
        icon.OnMouseHover = self.OnMouseHoverWeapon
        if moduleInfo.groupID == const.groupElectronicCounterMeasures:
            icon.baseAlpha = 0.3
        else:
            icon.baseAlpha = 1.0
        icon.SetAlpha(icon.baseAlpha)
        self.timer = ModuleEffectTimer(parent=self, blink=True, timerRightCounterTexturePath=self.timerRightCounterTexturePath, timerLeftCounterTexturePath=self.timerLeftCounterTexturePath, timerCounterGaugeTexturePath=self.timerCounterGaugeTexturePath)

    def ClickWeapon(self):
        module = GetModuleFromID(self.sr.moduleID)
        if module:
            module.Click()

    def OnMouseEnterWeapon(self):
        moduleID = self.sr.moduleID
        module = GetModuleFromID(moduleID)
        if module is not None:
            module.InitHilite()
            module.sr.hilite.display = True
        sm.GetService('bracket').ShowHairlinesForModule(moduleID, reverse=True)

    def OnMouseExitWeapon(self):
        moduleID = self.sr.moduleID
        module = GetModuleFromID(moduleID)
        if module is not None:
            module.RemoveHilite()
        sm.GetService('bracket').StopShowingModuleRange(moduleID)

    def OnMouseHoverWeapon(self):
        if not self.getJammingInfoFunc:
            return
        jammingInfo = self.getJammingInfoFunc(self.sr.moduleID)
        if jammingInfo is None:
            self.SetIconHint('')
            return
        now = blue.os.GetSimTime()
        timeSinceStart = now - jammingInfo.startTime
        timeLeft = jammingInfo.duration - timeSinceStart / 10000
        hintText = GetByLabel('UI/Inflight/Target/ECMTimeLeft', secondsLeft=timeLeft / 1000)
        self.SetIconHint(hintText)

    def SetIconHint(self, hintText):
        self.icon.hint = hintText


def GetModuleFromID(moduleID):
    if not uicore.layer.shipui:
        return
    module = uicore.layer.shipui.GetModule(moduleID)
    return module
