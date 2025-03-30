#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crimewatch\duelInviteWindow.py
import blue
import evelink.client
import localization
import uthread
import utillib
from carbonui import ButtonVariant, uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.crimewatch.crimewatchConst import Colors
from eve.client.script.ui.shared.stateFlag import FlagIconWithState
from eve.common.lib import appConst as const
DUEL_WND_WIDTH = 420

class DuelInviteWindow(Window):
    default_iconNum = 'res:/UI/Texture/WindowIcons/limitedengagement.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.charID = attributes.charID
        self.corpID = attributes.corpID
        self.allianceID = attributes.allianceID
        self.info = cfg.eveowners.Get(self.charID)
        self.result = set()
        self._buttons = []
        self.SetCaption(localization.GetByLabel('UI/Crimewatch/Duel/InvitationWindowCaption'))
        self.SetMinSize([DUEL_WND_WIDTH, 222])
        self.MakeUnResizeable()
        self.MakeUnKillable()
        self.ConstructLayout()

    def ConstructLayout(self):

        def on_main_cont_resized(main_cont):
            _, height = self.GetWindowSizeForContentSize(height=main_cont.height)
            self.SetFixedHeight(height)

        main_cont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, alignMode=uiconst.TOTOP, callback=lambda : on_main_cont_resized(main_cont))
        invitorCont = ContainerAutoSize(name='invitorCont', parent=main_cont, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, alignMode=uiconst.TOTOP, minHeight=64)
        self.lefSide = Container(name='lefSide', parent=invitorCont, align=uiconst.TOLEFT, width=64)
        self.rightSide = Container(name='rightSide', parent=invitorCont, align=uiconst.TORIGHT, width=64)
        challangerCont = ContainerAutoSize(name='challangerCont', parent=invitorCont, align=uiconst.TOTOP, padding=(8, 0, 8, 0))
        grid = LayoutGrid(name='grid', parent=challangerCont, columns=2, cellSpacing=(8, 8))
        challangerImgCont = Container(name='challangerImgCont', parent=self.lefSide, align=uiconst.TOPLEFT, pos=(0, 0, 64, 64))
        eveIcon.GetOwnerLogo(parent=challangerImgCont, ownerID=self.charID, size=64, noServerCall=True)
        icon = challangerImgCont.children[0]
        icon.isDragObject = True
        icon.GetDragData = self.CharGetDragData
        icon.OnClick = self.CharOnClick
        stateFlag = FlagIconWithState(parent=challangerImgCont, align=uiconst.BOTTOMRIGHT)
        slimItem = sm.GetService('crimewatchSvc').GetSlimItemDataForCharID(self.charID)
        if slimItem is not None:
            stateSvc = sm.GetService('stateSvc')
            flagCode = stateSvc.CheckFilteredFlagState(slimItem)
            flagInfo = stateSvc.GetStatePropsColorAndBlink(flagCode)
            stateFlag.ModifyIcon(flagInfo=flagInfo)
        charNameLabel = eveLabel.EveLabelMedium(name='charNameLabel', parent=grid, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, text=localization.GetByLabel('UI/Common/Name'))
        charName = eveLabel.EveLabelMedium(name='charName', text=evelink.client.character_link(self.charID), parent=grid, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        corpNameLabel = eveLabel.EveLabelMedium(name='corpNameLabel', parent=grid, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, text=localization.GetByLabel('UI/Common/Corporation'))
        corpName = eveLabel.EveLabelMedium(name='corpName', text=evelink.client.corporation_link(self.corpID), parent=grid, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        labels = [charNameLabel, corpNameLabel]
        valueLabels = [charName, corpName]
        if self.allianceID is not None:
            allianceNameLabel = eveLabel.EveLabelMedium(name='allianceNameLabel', parent=grid, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, text=localization.GetByLabel('UI/Common/Alliance'))
            allianceName = eveLabel.EveLabelMedium(name='allianceName', parent=grid, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=evelink.client.alliance_link(self.allianceID))
            labels.append(allianceNameLabel)
            valueLabels.append(allianceName)
        timeCont = Container(name='timeCont', parent=self.rightSide, align=uiconst.TOPRIGHT, width=64, height=64)
        Sprite(name='logo', parent=timeCont, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Crimewatch/Crimewatch_LimitedEngagement_64.png', opacity=0.3)
        self.time = eveLabel.Label(name='counter', parent=timeCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, text='30', fontsize=32, bold=False, color=Colors.Engagement.GetRGBA())
        eveLabel.EveLabelMedium(parent=main_cont, align=uiconst.TOTOP, top=8, text=localization.GetByLabel('UI/Crimewatch/Duel/DuelDecleration'))
        bottom_grid = LayoutGrid(parent=ContainerAutoSize(parent=main_cont, align=uiconst.TOTOP, top=16), columns=3, cellSpacing=(8, 0))
        Button(parent=bottom_grid, align=uiconst.CENTERLEFT, label=localization.GetByLabel('UI/Crimewatch/Duel/Accept'), variant=ButtonVariant.PRIMARY, func=self.AcceptDuel)
        Button(parent=bottom_grid, align=uiconst.CENTERLEFT, label=localization.GetByLabel('UI/Crimewatch/Duel/Decline'), func=self.DeclineDuel)
        self.blockOption = Checkbox(parent=bottom_grid, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/Crimewatch/Duel/BlockCommunications'))

    def StartTimeout(self, expiryTime):
        self.expiryThread = uthread.new(self._DoTimeout, expiryTime)

    def _DoTimeout(self, expiryTime):
        timeout = expiryTime - blue.os.GetWallclockTimeNow()
        while timeout > 0:
            blue.pyos.synchro.SleepWallclock(100)
            timeout = expiryTime - blue.os.GetWallclockTimeNow()
            self.time.text = str(max(0, int(timeout / float(const.SEC))))

        if not self or self.destroyed:
            return
        self.SetModalResult(uiconst.OK)
        self.time.SetTextColor(Color.RED)
        for btn in self._buttons:
            btn.Disable()

        blue.pyos.synchro.SleepWallclock(2000)
        self.Close()

    def CharGetDragData(self, *args):
        if self and not self.destroyed:
            fakeNode = utillib.KeyVal()
            fakeNode.charID = self.charID
            fakeNode.typeID = self.info.typeID
            fakeNode.info = self.info
            fakeNode.itemID = self.charID
            fakeNode.__guid__ = 'listentry.User'
            return [fakeNode]
        else:
            return []

    def CharOnClick(self, *args):
        sm.GetService('info').ShowInfo(typeID=self.info.typeID, itemID=self.charID)

    def AcceptDuel(self, *args):
        if uicore.Message('AskConfirmDuel', None, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        self.result = {'accept'}
        if self.blockOption.checked:
            self.result.add('block')
        self.SetModalResult(uiconst.OK)

    def DeclineDuel(self, *args):
        self.result = {'decline'}
        if self.blockOption.checked:
            self.result.add('block')
        self.SetModalResult(uiconst.OK)
