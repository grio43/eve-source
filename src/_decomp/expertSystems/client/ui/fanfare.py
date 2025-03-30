#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\fanfare.py
import eveformat
import evelink.client
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelLarge, Label
from carbonui.control.window import Window
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeButton
from expertSystems.client.const import Color
from expertSystems.client.service import ExpertSystemService
from expertSystems.data import get_expert_system
from localization import GetByLabel
from localization.formatters import FormatGenericList
SELECTED_ICON_SIZE = 128
DEFAULT_TOPCONT_XPOS = 333
ICON_TRANSFORM_WIDTH = SELECTED_ICON_SIZE
ICON_CONT_CENTER_ALLIGNMENT = 205
FIRST_ICON_SCALE = (0.5, 0.5)
SECOND_ICON_SCALE = (0.25, 0.25)
ICON_X_SPACES = [-135,
 -87,
 0,
 87,
 135]
ICON_SCALES = [0.25,
 0.5,
 1.0,
 0.5,
 0.25]

class ExpertSystemFanfareWindow(Window):
    __guid__ = 'fanfare.expertSystem'
    __notifyevents__ = ['OnCharacterSessionChanged']
    default_windowID = 'ExpertSystemFanfareWindow'
    default_width = 540
    default_fixedWidth = 540
    default_height = 680
    default_fixedHeight = 680
    default_isCollapseable = False
    default_isMinimizable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(ExpertSystemFanfareWindow, self).ApplyAttributes(attributes)
        Fill(parent=self.sr.headerParent, color=Color.base, opacity=0.85, padding=(2, 2, 2, 0))
        PlaySound('expert_system_play')
        expertSystemTypeID = attributes.get('expertSystemTypeID', attributes)
        self.redeemedExpertSystemIDs = [expertSystemTypeID]
        self.mainCont = Container(parent=self.sr.main, align=uiconst.TOALL, bgTexturePath='res:/UI/Texture/classes/ExpertSystems/fanfareBG.png')
        self.iconIndexDisplacement = 2
        self.selectedExpertSystemIdx = 0
        self.ConstructLayout()

    def Close(self, *args, **kwargs):
        PlaySound('expert_system_stop')
        super(ExpertSystemFanfareWindow, self).Close(*args, **kwargs)

    def ConstructLayout(self):
        myExpertSystems = ExpertSystemService.instance().GetMyExpertSystems()
        self.redeemedExpertSystemsData = []
        for expertSystemTypeID in self.redeemedExpertSystemIDs:
            expiryDate = None
            for id, (inDate, exDate) in myExpertSystems.iteritems():
                if id == expertSystemTypeID:
                    expiryDate = exDate

            data = {'expiryDate': expiryDate,
             'expertSystem': get_expert_system(expertSystemTypeID),
             'name': evetypes.GetName(expertSystemTypeID)}
            self.redeemedExpertSystemsData.append(data)

        self.topButtonCont = Container(align=uiconst.TOPLEFT_PROP, height=0.4, width=self.width, parent=self.mainCont)
        self.topCont = Container(align=uiconst.TOTOP_PROP, height=0.4, parent=self.mainCont)
        self.bottomCont = Container(parent=self.mainCont, align=uiconst.TOTOP_PROP, height=0.6)
        self.ConstructIcons()
        self._ConstructBottom()

    def ConstructIcons(self):
        self.topButtonCont.height = self.topCont.height
        selectedExpertSystemID = self.redeemedExpertSystemIDs[self.selectedExpertSystemIdx]
        self.iconTransforms = []
        for i, esID in enumerate(self.redeemedExpertSystemIDs):
            scale = FIRST_ICON_SCALE
            if abs(i - self.selectedExpertSystemIdx) > 1:
                scale = SECOND_ICON_SCALE
            transform = _ESTransform(parent=self.topCont, align=uiconst.CENTER, left=ICON_X_SPACES[i + self.iconIndexDisplacement], width=ICON_TRANSFORM_WIDTH, expertSystemTypeID=esID, selected=esID == selectedExpertSystemID, top=50, scale=scale, index=i)
            icon = ItemIcon(parent=transform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=SELECTED_ICON_SIZE, height=SELECTED_ICON_SIZE)
            icon.SetTypeID(esID)
            if esID == selectedExpertSystemID:
                transform.scale = (1.0, 1.0)
            self.iconTransforms.append(transform)

        if len(self.redeemedExpertSystemIDs) > 1:
            ButtonIcon(name='leftButton', parent=self.topButtonCont, align=uiconst.CENTERLEFT, texturePath='res:/ui/texture/classes/ExpertSystems/fanfareLeftArrow.png', iconSize=22, top=60, func=self._ScrollLeft)
            ButtonIcon(name='rightButton', parent=self.topButtonCont, align=uiconst.CENTERRIGHT, texturePath='res:/ui/texture/classes/ExpertSystems/fanfareRightArrow.png', iconSize=22, top=60, func=self._ScrollRight)

    def _ConstructBottom(self):
        selectedExpertSystem = self.redeemedExpertSystemsData[self.selectedExpertSystemIdx]
        expiryDate = selectedExpertSystem['expiryDate']
        newExpertSystemName = selectedExpertSystem['name']
        newExpertSystem = selectedExpertSystem['expertSystem']
        titleCont = ContainerAutoSize(parent=self.bottomCont, align=uiconst.TOTOP)
        Label(parent=titleCont, text=GetByLabel('UI/ExpertSystem/FanFare/ExpertSystemRedeemed'), align=uiconst.CENTER, opacity=1.0, top=8, color=Color.base, uppercase=True, fontsize=15, bold=True)
        expertSystemNameCont = ContainerAutoSize(parent=self.bottomCont, align=uiconst.TOTOP)
        Label(parent=expertSystemNameCont, text=eveformat.center(newExpertSystemName), align=uiconst.CENTERLEFT, left=15, opacity=1.0, color=Color.base, top=5, fontsize=36, bold=True, uppercase=True, width=500, autoFitToText=True)
        if session.charid:
            UpgradeButton(parent=self.bottomCont, align=uiconst.CENTERBOTTOM, top=75, width=250, height=41, onClick=self._OnCTAButtonClicked, text=GetByLabel('UI/ExpertSystem/FanFare/CTAButtonText'), labelColor=Color.base, fillColor=Color.base, stretchTexturePath='res:/UI/Texture/classes/ExpertSystems/fanfareBtnBG.png', stretchTextureColor=Color.base)
        infoCont = ContainerAutoSize(name='infoCont', parent=self.bottomCont, align=uiconst.TOBOTTOM, clipChildren=True, top=85, bgColor=(0, 0, 0, 0.4), padding=(50, 0, 50, 50))
        associatedShipTypes = []
        for shipTypeID in newExpertSystem.associated_type_ids:
            text = evetypes.GetName(shipTypeID)
            if session.charid:
                text = evelink.type_link(shipTypeID)
            associatedShipTypes.append(text)

        if newExpertSystem.associated_type_ids:
            text = None
            if len(associatedShipTypes) > 3:
                genericList = FormatGenericList(associatedShipTypes[:3])
                text = GetByLabel('UI/ExpertSystem/FanFare/HelpsYouFlyPlusMore', ships=genericList, notListed=len(associatedShipTypes) - 3)
            else:
                genericList = FormatGenericList(associatedShipTypes)
                text = GetByLabel('UI/ExpertSystem/FanFare/HelpsYouFly', ships=genericList)
            BenefitRow(parent=infoCont, text=text, align=uiconst.TOTOP, padTop=20, padLeft=20, labelState=uiconst.UI_NORMAL)
        BenefitRow(parent=infoCont, text=GetByLabel('UI/ExpertSystem/FanFare/WillSurvivePodDeath'), align=uiconst.TOTOP, padTop=20, padLeft=20)
        BenefitRow(text=GetByLabel('UI/ExpertSystem/FanFare/WillExpireOn', expiryDate=FmtDate(expiryDate)), parent=infoCont, align=uiconst.TOTOP, padTop=20, padLeft=20, padBottom=20)

    @classmethod
    def ShowFanfare(cls, expertSystemTypeID):
        cls.Open(expertSystemTypeID=expertSystemTypeID)

    def OnCharacterSessionChanged(self, *args):
        self.mainCont.Flush()
        self.ConstructLayout()

    def _OnCTAButtonClicked(self, *args):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.OpenExpertSystems()
        self.CloseByUser()

    def _ScrollRight(self):
        self.selectedExpertSystemIdx = (self.selectedExpertSystemIdx + 1) % len(self.redeemedExpertSystemIDs)
        minDisplacement = 3 - len(self.redeemedExpertSystemIDs)
        if self.iconIndexDisplacement == minDisplacement:
            self.iconIndexDisplacement = 2
        else:
            self.iconIndexDisplacement = self.iconIndexDisplacement - 1
        self._Scroll()

    def _ScrollLeft(self):
        self.selectedExpertSystemIdx = (self.selectedExpertSystemIdx - 1) % len(self.redeemedExpertSystemIDs)
        minDisplacement = 3 - len(self.redeemedExpertSystemIDs)
        if self.iconIndexDisplacement == 2:
            self.iconIndexDisplacement = minDisplacement
        else:
            self.iconIndexDisplacement = self.iconIndexDisplacement + 1
        self._Scroll()

    def _Scroll(self):
        selectedESID = self.redeemedExpertSystemIDs[self.selectedExpertSystemIdx]
        for icon in self.iconTransforms:
            newX = ICON_X_SPACES[icon.index + self.iconIndexDisplacement]
            uicore.animations.MorphScalar(icon, 'left', startVal=icon.left, endVal=newX, duration=0.75)
            if icon.expertSystemTypeID == selectedESID and not icon.selected:
                icon.selected = True
                uicore.animations.Tr2DScaleTo(icon, startScale=icon.scale, endScale=(1.0, 1.0), duration=0.75)
            elif icon.expertSystemTypeID != selectedESID:
                icon.selected = False
                scale = FIRST_ICON_SCALE
                if abs(icon.index - self.selectedExpertSystemIdx) > 1:
                    scale = SECOND_ICON_SCALE
                uicore.animations.Tr2DScaleTo(icon, startScale=icon.scale, endScale=scale, duration=0.75)

        self.bottomCont.Flush()
        self._ConstructBottom()

    def AddAnotherExpertSystemToFanfare(self, expertSystemTypeID):
        self.redeemedExpertSystemIDs.append(expertSystemTypeID)
        self.mainCont.Flush()
        self.ConstructLayout()

    def _Reload(self):
        self.mainCont.Flush()
        self.ConstructLayout()


class _ESTransform(Transform):
    default_scalingCenter = (0.5, 0.5)

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.expertSystemTypeID = attributes.expertSystemTypeID
        self.selected = attributes.selected
        self.index = attributes.index


class BenefitRow(Container):
    default_height = 20

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.text = attributes.get('text', None)
        self.labelState = attributes.get('labelState', uiconst.UI_DISABLED)
        Sprite(texturePath='res:/UI/Texture/Classes/MissionTracker/tracker_check.png', parent=self, align=uiconst.TOLEFT, color=Color.base, pos=(0, 0, 20, 20), state=uiconst.UI_DISABLED)
        EveLabelLarge(parent=self, align=uiconst.TOLEFT, text=self.text, padLeft=20, state=self.labelState)


class OpenCharSheetInfoLink(GlowSprite):
    default_state = uiconst.UI_NORMAL
    default_width = 16
    default_height = 16
    default_texturePath = 'res:/ui/Texture/Icons/38_16_208.png'

    def OnMouseEnter(self, *args):
        GlowSprite.OnMouseEnter(self, *args)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnClick(self):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.OpenExpertSystems()
