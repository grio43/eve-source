#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\characterOverviewPanel\characterOverviewElements.py
import eveformat.client
import homestation.client
import threadutils
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.shared.info.infoConst import TAB_WARHISTORY
from eve.client.script.ui.shared.neocom.corporation.war.atWarTooltip import LoadAtWarTooltipPanelFindWars
from eve.common.lib import appConst
from eve.common.lib import appConst as const
from localization import GetByLabel
from menu import MenuList
from eve.client.script.ui.const.eveIconConst import RACE_ICONS
CHAR_INFO_ELEMENT_HEIGHT = 25
CHAR_INFO_TOOLTIP_ICON_PATH = 'res:/UI/Texture/Icons/generic/more_info_16.png'
CHAR_INFO_TOOLTIP_WIDTH = 16

class EmpireIcon(GlowSprite):
    default_state = uiconst.UI_NORMAL
    default_iconOpacity = 1.0

    def ApplyAttributes(self, attributes):
        if 'texturePath' not in attributes and 'empireID' in attributes:
            attributes['texturePath'] = RACE_ICONS[attributes['empireID']]
        super(EmpireIcon, self).ApplyAttributes(attributes)

    def OnMouseHover(self, *args):
        super(EmpireIcon, self).OnMouseHover(*args)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnClick(self, *args):
        super(EmpireIcon, self).OnClick(*args)
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        factionID = const.factionByRace[session.raceID]
        sm.GetService('info').ShowInfo(const.typeFaction, itemID=factionID)


class CharacterInfoElement(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        leftCont = ContainerAutoSize(parent=self, name='leftCont', align=uiconst.TOLEFT, height=CHAR_INFO_ELEMENT_HEIGHT, padRight=10, padTop=1)
        centerCont = ContainerAutoSize(parent=self, name='rightCont', align=uiconst.TOLEFT, height=CHAR_INFO_ELEMENT_HEIGHT, padRight=10)
        rightCont = ContainerAutoSize(parent=self, name='rightCont', align=uiconst.TOLEFT, height=CHAR_INFO_ELEMENT_HEIGHT)
        self.titleLabel = EveLabelLarge(parent=leftCont, name='titleLabel', align=uiconst.CENTERLEFT, text=attributes.titleText, opacity=1, color=TextColor.SECONDARY)
        self.valueLabel = EveLabelLarge(parent=centerCont, name='valueLabel', align=uiconst.CENTERLEFT, text=attributes.valueText, opacity=1)
        if attributes.tooltip is not None:
            self.tooltipIcon = ButtonIcon(parent=rightCont, name='tooltipButton', texturePath=CHAR_INFO_TOOLTIP_ICON_PATH, align=uiconst.CENTERLEFT, width=CHAR_INFO_TOOLTIP_WIDTH, height=CHAR_INFO_TOOLTIP_WIDTH, state=uiconst.UI_NORMAL, hint=attributes.tooltip)


class CharacterInfoSecurityStatus(CharacterInfoElement):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        CharacterInfoElement.ApplyAttributes(self, attributes)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.OpenSecurityStatus()


class CharacterInfoHomeStation(CharacterInfoElement):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        CharacterInfoElement.ApplyAttributes(self, attributes)
        homestation.Service.instance().on_home_station_changed.connect(self._UpdateHomeStationText)
        self._UpdateHomeStationText()

    @property
    def home_station(self):
        return homestation.Service.instance().get_home_station()

    @threadutils.threaded
    def _UpdateHomeStationText(self):
        text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/UnknownSystem')
        if self.home_station and self.home_station.solar_system_id:
            text = eveformat.solar_system_with_security(self.home_station.solar_system_id)
        self.valueLabel.SetText(text)
        self.tooltipIcon.hint = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CloneLocationHint', locationId=self.home_station.id)

    def GetMenu(self):
        if self.home_station:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(self.home_station.id, self.home_station.type_id)
        return MenuList()

    def OnClick(self, *args):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        CharacterSheetWindow.OpenHomeStation()


class IconButtonCont(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOLEFT
    default_width = 45

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.func = attributes.func

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        uicore.animations.FadeTo(self, self.opacity, 1.5, duration=0.15)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self, self.opacity, 1.0, duration=0.3)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.func()


class AtWarIconAndLabel(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    texturePath = 'res:/UI/Texture/classes/war/atWar_64.png'
    iconSize = 52

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        iconCont = Container(parent=self, align=uiconst.TOTOP, height=self.iconSize)
        self.icon = GlowSprite(parent=iconCont, state=uiconst.UI_DISABLED, align=uiconst.CENTER, texturePath=self.texturePath, width=52, height=52)
        labelCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP)
        self.label = EveLabelMedium(parent=labelCont, align=uiconst.CENTER, text=self.GetText())

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.icon.OnMouseEnter()
        uicore.animations.FadeTo(self, self.opacity, 1.3, duration=0.15)

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()
        uicore.animations.FadeTo(self, self.opacity, 1.0, duration=0.3)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        typeID = appConst.typeAlliance if session.allianceid else appConst.typeCorporation
        itemID = session.allianceid or session.corpid
        sm.GetService('info').ShowInfo(typeID, itemID, selectTabType=TAB_WARHISTORY)

    def GetText(self):
        return '<color=0xff99251f>%s</color>' % GetByLabel('UI/Corporations/Wars/AtWar')

    def GetHint(self):
        return ''

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadAtWarTooltipPanelFindWars(tooltipPanel)
