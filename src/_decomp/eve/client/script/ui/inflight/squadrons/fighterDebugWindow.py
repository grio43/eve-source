#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\squadrons\fighterDebugWindow.py
from carbonui import uicore, uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.control.window import Window
from fighters import ABILITY_SLOT_0, ABILITY_SLOT_1, ABILITY_SLOT_2
from spacecomponents.client.components.behavior import EnableDebugging
from carbonui.uicore import uicore
import geo2

class FighterDebugWindow(Window):
    default_windowID = 'FighterDebugWindow'
    default_width = 250
    default_height = 360
    default_caption = 'Fighter debugger'
    default_icon = '41_13'
    currentFighterID = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.Layout()
        self.SetMinSize([350, 500], refresh=True)

    def Layout(self):
        fighter_cont = Container(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        EveLabelSmall(text='Fighter ID', parent=ContainerAutoSize(parent=fighter_cont, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, padRight=8)
        self.fighterIDBox = SingleLineEditText(name='fighterID', parent=fighter_cont, align=uiconst.TOLEFT, OnChange=self.OnFighterIDBoxChange, padRight=8)
        self.fighterIDBox.SetText(self._GetFighterID())
        Button(parent=fighter_cont, name='DebugFighter', label='DBG', func=self.OnDebugFighterButton, align=uiconst.TOLEFT)
        target_cont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        EveLabelSmall(text='Target ID', parent=ContainerAutoSize(parent=target_cont, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, padRight=8)
        self.targetIDBox = SingleLineEditText(parent=target_cont, name='targetID', align=uiconst.TOLEFT)
        self.targetIDBox.SetText(session.shipid)
        orbit_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        Button(parent=orbit_container, name='OrbitTarget', label='Orbit Target', func=self.OnOrbitTargetButton, align=uiconst.TOLEFT, padRight=8)
        Button(name='OrbitMe', parent=orbit_container, label='Orbit Me', func=self.OnOrbitMeButton, align=uiconst.TOLEFT)
        Button(name='StopMovement', label='Stop movement', func=self.OnMoveStopButton, parent=ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, padBottom=8), align=uiconst.TOPLEFT)
        xyz_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        EveLabelSmall(text='x,y,z', parent=ContainerAutoSize(parent=xyz_container, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, padRight=8)
        self.gotoPosBox = SingleLineEditText(name='gotoPos', parent=xyz_container, align=uiconst.TOLEFT)
        ButtonIcon(name='pickXYZ', parent=xyz_container, align=uiconst.TOLEFT, width=16, iconSize=16, texturePath='res:/UI/Texture/Icons/38_16_150.png', hint='Pick random position near target', func=self.OnPickXYZ)
        point_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        Button(parent=point_container, name='GotoPoint', label='Goto this point', func=self.OnGotoPointButton, align=uiconst.TOLEFT, padRight=8)
        Button(parent=point_container, name='ToggleMoveMode', label='Toggle Movement', func=self.OnToggleMoveButton, align=uiconst.TOLEFT)
        EveLabelSmall(text='Ability 0', parent=self.content, align=uiconst.TOTOP, padBottom=8)
        ability0_btns_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        Button(parent=ability0_btns_container, name='ActivateAbilityOnTarget', label='Activate (target)', func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_0,), align=uiconst.TOLEFT, padRight=8)
        Button(parent=ability0_btns_container, name='ActivateAbilityOnSelf', label='Activate (self)', func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_0,), align=uiconst.TOLEFT, padRight=8)
        Button(parent=ability0_btns_container, name='DeactivateAbility', label='Deactivate', func=self.OnDeactivateAbility, args=(ABILITY_SLOT_0,), align=uiconst.TOLEFT)
        EveLabelSmall(text='Ability 1', align=uiconst.TOTOP, parent=self.content, padBottom=8)
        ability1_btns_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        Button(parent=ability1_btns_container, name='ActivateAbilityOnTarget', label='Activate (target)', func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_1,), align=uiconst.TOLEFT, padRight=8)
        Button(parent=ability1_btns_container, name='ActivateAbilityOnSelf', label='Activate (self)', func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_1,), align=uiconst.TOLEFT, padRight=8)
        Button(parent=ability1_btns_container, name='DeactivateAbility', label='Deactivate', func=self.OnDeactivateAbility, args=(ABILITY_SLOT_1,), align=uiconst.TOLEFT)
        EveLabelSmall(text='Ability 2', align=uiconst.TOTOP, parent=self.content, padBottom=8)
        ability2_btns_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padBottom=8)
        Button(parent=ability2_btns_container, name='ActivateAbilityOnTarget', label='Activate (target)', func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_2,), align=uiconst.TOLEFT, padRight=8)
        Button(parent=ability2_btns_container, name='ActivateAbilityOnSelf', label='Activate (self)', func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_2,), align=uiconst.TOLEFT, padRight=8)
        Button(parent=ability2_btns_container, name='DeactivateAbility', label='Deactivate', func=self.OnDeactivateAbility, args=(ABILITY_SLOT_2,), align=uiconst.TOLEFT)

    def _GetFighterID(self):
        return self.currentFighterID

    def _GetTargetID(self):
        try:
            return int(self.targetIDBox.text.strip())
        except ValueError:
            return None

    def OnFighterIDBoxChange(self, *args):
        try:
            self.currentFighterID = int(self.fighterIDBox.text.strip())
        except ValueError:
            pass

    def OnDebugFighterButton(self, *args):
        self._OnDebugFighterButton(*args)

    def _OnDebugFighterButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            EnableDebugging(fighterID)

    def OnPickXYZ(self, *args):
        self._OnPickXYZ(*args)

    def _OnPickXYZ(self, *args):
        michelle = sm.GetService('michelle')
        targetID = self._GetTargetID() or session.shipid
        ball = michelle.GetBall(targetID)
        if ball:
            import random
            shipPos = geo2.VectorD(ball.x, ball.y, ball.z)
            offsetRange = ball.radius + 2000
            offset = geo2.Vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
            targetPos = geo2.Vec3AddD(shipPos, geo2.Vec3Scale(geo2.Vec3Normalize(offset), offsetRange))
            self.gotoPosBox.SetText('%.0f, %.0f, %0.f' % (targetPos[0], targetPos[1], targetPos[2]))

    def OnGotoPointButton(self, *args):
        self._OnGotoPointButton(*args)

    def _OnGotoPointButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            point = geo2.VectorD([ float(v.strip()) for v in self.gotoPosBox.text.strip().split(',') ])
            sm.GetService('fighters').CmdGotoPoint([fighterID], list(point))

    def OnToggleMoveButton(self, *args):
        self._OnOnToggleMoveButton(*args)

    def _OnOnToggleMoveButton(self, *args):
        uicore.layer.inflight.positionalControl.StartMoveCommand()

    def OnOrbitTargetButton(self, *args):
        self._OnOrbitTargetButton(*args)

    def _OnOrbitTargetButton(self, *args):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').CmdMovementOrbit([fighterID], targetID, 5000)

    def OnOrbitMeButton(self, *args):
        self._OnOrbitMeButton(*args)

    def _OnOrbitMeButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementOrbit([fighterID], session.shipid, 5000)

    def OnMoveStopButton(self, *args):
        self._OnMoveStopButton(*args)

    def _OnMoveStopButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementStop([fighterID])

    def OnActivateAbilityOnTarget(self, abilitySlotID):
        self._OnActivateAbilityOnTarget(abilitySlotID)

    def _OnActivateAbilityOnTarget(self, abilitySlotID):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').ActivateAbilitySlotsOnTarget([fighterID], abilitySlotID, targetID)

    def OnActivateAbilityOnSelf(self, abilitySlotID):
        self._OnActivateAbilityOnSelf(abilitySlotID)

    def _OnActivateAbilityOnSelf(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').ActivateAbilitySlotsOnSelf([fighterID], abilitySlotID)

    def OnDeactivateAbility(self, abilitySlotID):
        self._OnDeactivateAbility(abilitySlotID)

    def _OnDeactivateAbility(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').DeactivateAbilitySlots([fighterID], abilitySlotID)
