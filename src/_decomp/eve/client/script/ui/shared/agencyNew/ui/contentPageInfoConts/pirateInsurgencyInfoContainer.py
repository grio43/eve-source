#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\pirateInsurgencyInfoContainer.py
from carbonui import TextBody
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import OwnerIcon, LogoIcon
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.jobInfoContainer import JobContentPageInfoContainer
from jobboard.client import get_pirate_insurgency_job
from localization import GetByLabel
import carbonui.const as uiconst

class PirateInsurgencyInfoContainer(JobContentPageInfoContainer):
    default_name = 'PirateInsurgencyInfoContainer'
    default_headerText = GetByLabel('UI/Agency/PirateIncursions/ActivitiesInSystem')
    __notifyevents__ = ['OnClientEvent_DestinationSet']

    def __init__(self, *args, **kwargs):
        super(PirateInsurgencyInfoContainer, self).__init__(*args, **kwargs)
        sm.RegisterNotify(self)

    def Close(self):
        sm.UnregisterNotify(self)
        super(PirateInsurgencyInfoContainer, self).Close()

    def GetEntryContentPieces(self):
        return self.contentPiece.contentPieces

    def ConstructLayout(self):
        self.ConstructFobContainer()
        self.ConstructSystemExtraInfoContainer()
        self.ConstructScroll()

    def ConstructSystemExtraInfoContainer(self):
        iconSize = 64
        cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, height=iconSize, padBottom=10, alignMode=uiconst.CENTERLEFT)
        iconCont = Container(name='iconCont', parent=cont, align=uiconst.CENTERLEFT, width=iconSize + 8, pos=(6,
         0,
         iconSize,
         iconSize))
        self.ownerIcon = OwnerIcon(parent=iconCont, align=uiconst.TOALL)
        normalLeft = iconSize + 14
        self.textCont = ContainerAutoSize(parent=cont, align=uiconst.CENTERLEFT, width=250, left=normalLeft)
        self.textCont.normalLeft = normalLeft
        self.pirateText = TextBody(parent=self.textCont, align=uiconst.TOTOP)
        self.corruptionLabel = TextBody(parent=self.textCont, align=uiconst.TOTOP)
        self.suppressionLabel = TextBody(parent=self.textCont, align=uiconst.TOTOP)

    def ConstructFobContainer(self):
        self.fobContainer = Container(name='fobContainer', parent=self, align=uiconst.TOPRIGHT, pos=(0, 0, 52, 103))
        self.fobOwnerIcon = Sprite(name='fobOwnerIcon', parent=self.fobContainer, align=uiconst.CENTERTOP, pos=(0, 16, 32, 32))
        self.pirateText = TextBody(parent=self.fobContainer, align=uiconst.CENTERTOP, top=56, text=GetByLabel('UI/PirateInsurgencies/FOB'))
        self.fobBG = Sprite(name='fobBG', parent=self.fobContainer, align=uiconst.CENTERTOP, pos=(0, 0, 52, 103), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/agency/pirateIncursions/fobFlag.png', color=sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT))

    def _UpdateContentPiece(self, contentPiece):
        super(PirateInsurgencyInfoContainer, self)._UpdateContentPiece(contentPiece)
        ownerID = self.contentPiece.GetOwnerID()
        if ownerID:
            self.ownerIcon.SetOwnerID(ownerID)
            self.ownerIcon.Show()
            self.textCont.left = self.textCont.normalLeft
        else:
            self.ownerIcon.Hide()
            self.textCont.left = 0
        self.pirateText.text = self.contentPiece.GetPirateText()
        self.corruptionLabel.text = self.contentPiece.GetCorruptionStageText()
        self.suppressionLabel.text = self.contentPiece.GetSuppressionStageText()
        fobOwnerID = self.contentPiece.GetFobOwnerInSystem()
        if fobOwnerID:
            self.fobContainer.Show()
            self.fobOwnerIcon.texturePath = LogoIcon.GetFactionIconTexturePath(fobOwnerID)
            self.fobOwnerIcon.GetMenu = lambda *args: sm.GetService('menu').GetMenuForOwner(fobOwnerID)
            typeID = cfg.eveowners.Get(fobOwnerID).typeID
            self.fobOwnerIcon.OnClick = lambda *args: sm.GetService('info').ShowInfo(typeID, fobOwnerID)
        else:
            self.fobContainer.Hide()

    def _GetJob(self, instanceID):
        return get_pirate_insurgency_job(instanceID)

    def OnClientEvent_DestinationSet(self, *args, **kwargs):
        self.OnScrollEntryClicked(self.clickedEntry)
