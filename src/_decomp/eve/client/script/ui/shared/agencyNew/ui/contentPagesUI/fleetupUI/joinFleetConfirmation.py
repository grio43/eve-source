#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\fleetupUI\joinFleetConfirmation.py
import evefleet
from carbonui import ButtonVariant, uiconst
from carbonui.control.button import Button
from carbonui.control.window import Window
from carbonui.fontconst import EVE_LARGE_FONTSIZE
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.fleet.fleet import GetFleetActivityName
from evelink.client import owner_link
from localization import GetByLabel

def RequestToJoinFleet(fleetID, fleetAd):
    wnd = JoinFleetConfirmationWnd(fleetAd=fleetAd)
    ret = wnd.ShowModal()
    if ret == uiconst.ID_YES:
        fleetSvc = sm.GetService('fleet')
        fleetSvc.ApplyToJoinFleet(fleetID, autoAccept=True)
        fleetSvc.LogFleetJoinAttempts(fleetID, evefleet.JOIN_SOURCE_FLEETUP)


class JoinFleetConfirmationWnd(Window):
    default_width = 400
    default_height = 300
    default_windowID = 'joinFleetConfirmationWnd'

    def ApplyAttributes(self, attributes):
        attributes.useDefaultPos = True
        super(JoinFleetConfirmationWnd, self).ApplyAttributes(attributes)
        self.MakeUnResizeable()
        self.sr.main.padLeft = 25
        self.sr.main.padRight = 25
        fleetAd = attributes.fleetAd
        gridCont = ContainerAutoSize(parent=self.sr.main, align=uiconst.TOTOP)
        grid = LayoutGrid(parent=gridCont, columns=3, padTop=32, cellSpacing=(100, 0), cellPadding=(10, 0))
        headerLabel = Label(fontsize=18, text=GetByLabel('UI/Agency/Fleetup/JoinRequestHeader'), uppercase=True, padBottom=13)
        grid.AddCell(headerLabel, colSpan=grid.columns)
        headerRow = grid.AddRow(cellPadding=(10, 11))
        Label(parent=headerRow, text=GetByLabel('UI/Agency/Fleetup/FleetNameHeader'), uppercase=True, fontsize=EVE_LARGE_FONTSIZE)
        Label(parent=headerRow, text=GetByLabel('UI/Agency/Fleetup/ActivityHeader'), uppercase=True, fontsize=EVE_LARGE_FONTSIZE)
        Label(parent=headerRow, text=GetByLabel('UI/Agency/Fleetup/NumberOfCapsuleers'), uppercase=True, fontsize=EVE_LARGE_FONTSIZE)
        row = grid.AddRow(cellPadding=(10, 9, 10, 9))
        fillFrame = Frame(name='fillFrame', bgParent=row, frameConst=uiconst.FRAME_FILLED_CORNER5, color=eveColor.CRYO_BLUE[:3] + (0.05,))
        Label(parent=row, text=fleetAd.fleetName, color=eveColor.CRYO_BLUE)
        Label(parent=row, text=GetFleetActivityName(fleetAd.activityValue), color=eveColor.CRYO_BLUE)
        if fleetAd.hideInfo:
            membersText = '<color=0x7f888888>%s</color>' % GetByLabel('UI/Generic/Private')
        else:
            membersText = fleetAd.numMembers
        Label(parent=row, text=membersText, color=eveColor.CRYO_BLUE)
        fcName = owner_link(fleetAd.leader.charID)
        approveHint = Label(parent=self.sr.main, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Fleetup/ConfirmationText', charName=fcName), padding=(11, 36, 0, 0), fontsize=EVE_LARGE_FONTSIZE, state=uiconst.UI_NORMAL)
        buttonCont = ContainerAutoSize(parent=self.sr.main, align=uiconst.TOBOTTOM, padBottom=26)
        grid.UpdateAlignment()
        self.width = max(self.width, grid.width + self.sr.main.padLeft + self.sr.main.padRight)
        _, approveHintHeight = Label.MeasureTextSize(approveHint.text, width=grid.width, fontsize=EVE_LARGE_FONTSIZE)
        contentHeight = self.sr.headerParent.height + grid.height + grid.padTop + grid.padBottom + approveHintHeight + approveHint.padTop + self.sr.underlay.padBottom + buttonCont.height + buttonCont.padBottom + 50
        self.height = max(self.height, contentHeight)
        cancelBtn = Button(name='cancelBtn', parent=buttonCont, align=uiconst.CENTERRIGHT, label=GetByLabel('UI/Commands/Cancel'), func=self.CancelClicked, analyticID=evefleet.CONFIRM_REQUEST_TO_JOIN_BTN_ANALYTIC_ID)
        sendRequestBtn = Button(name='sendRequestBtn', parent=buttonCont, align=uiconst.CENTERRIGHT, label=GetByLabel('UI/Agency/Fleetup/SendJoinRequest'), func=self.SendRequestClicked, variant=ButtonVariant.PRIMARY)
        sendRequestBtn.width = cancelBtn.width = max(sendRequestBtn.width, cancelBtn.width) + 16
        sendRequestBtn.left = cancelBtn.left + cancelBtn.width + 10

    def CloseByUser(self, *args):
        self.SetModalResult(uiconst.ID_CLOSE)
        super(JoinFleetConfirmationWnd, self).CloseByUser(*args)

    def SendRequestClicked(self, *args, **kwargs):
        self.SetModalResult(uiconst.ID_YES)

    def CancelClicked(self, *args, **kwargs):
        self.SetModalResult(uiconst.ID_NO)
