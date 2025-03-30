#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\traits.py
import eveicon
import evetypes
import infobubbles
import localization
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.commonutils import StripTags
from carbonui import fontconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from dogma import units
from eve.client.script.ui.control.eveLabel import Label
from carbonui.uicore import uicore
ROLE_BONUS_TYPE = -1
MISC_BONUS_TYPE = -2
COLOR_CAPTION = (0.298, 0.549, 0.69, 1.0)
COLOR_TEXT_HILITE = (0.765, 0.914, 1.0, 1.0)
COLOR_TEXT = (0.5, 0.5, 0.5, 1.0)
COLOR_TEXT_HILITE_HEX = Color.RGBtoHex(*COLOR_TEXT_HILITE)
TAB_MARGIN = 3

def HasTraits(typeID):
    return infobubbles.has_traits(typeID)


class TraitsContainer(ContainerAutoSize):
    default_name = 'TraitsContainer'
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(TraitsContainer, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        displayTraitAttributeIcons = attributes.get('traitAttributeIcons', False)
        padLeft = self.GetLeftPad()
        if displayTraitAttributeIcons and self.typeID in cfg.infoBubbleTypeElements:
            self.AddCaption(localization.GetByLabel('UI/InfoWindow/ShipCharacteristics'))
            self.AddAttributeIcons(cfg.infoBubbleTypeElements[self.typeID], padLeft)
        if not infobubbles.has_traits(self.typeID):
            return
        bonusLabels = []
        for skillTypeID, bonuses in infobubbles.iter_ship_skill_bonuses(self.typeID):
            self.AddCaption(localization.GetByLabel('UI/ShipTree/SkillNameCaption', skillName=evetypes.GetName(skillTypeID)))
            bonusLabels += self.AddBonusLabel(bonuses, padLeft)

        role_bonus = infobubbles.get_role_bonus(self.typeID)
        if role_bonus:
            self.AddCaption(localization.GetByLabel('UI/ShipTree/RoleBonus'))
            bonusLabels += self.AddBonusLabel(role_bonus, padLeft)
        misc_bonus = infobubbles.get_misc_bonus(self.typeID)
        if misc_bonus:
            self.AddCaption(text=localization.GetByLabel('UI/ShipTree/MiscBonus'))
            bonusLabels += self.AddBonusLabel(misc_bonus, padLeft)
        self.AdjustBonusLabels(bonusLabels)

    def AdjustBonusLabels(self, bonusLabels):
        defaultPadding = self.GetLeftPad()
        maxWidth = defaultPadding
        for b in bonusLabels:
            parts = b.text.split('<t>')
            if parts:
                col0Text = StripTags(parts[0], ignoredTags=['b'])
                w, h = Label.MeasureTextSize(col0Text)
                maxWidth = max(maxWidth, w + TAB_MARGIN)

        if maxWidth > defaultPadding:
            for b in bonusLabels:
                b.tabs = (maxWidth,)

    def AddCaption(self, text):
        Label(parent=self, text=text, align=uiconst.TOTOP, padTop=8 if self.children else 0, bold=True, color=COLOR_CAPTION)

    def AddBonusLabel(self, bonuses, padLeft):
        bonusLines = []
        for bonus in sorted(bonuses, key=lambda x: x['importance']):
            b = self._FormatBonusLine(bonus, padLeft)
            bonusLines.append(b)

        return bonusLines

    def AddAttributeIcons(self, data, padLeft):
        rowCont = Container(parent=self, align=uiconst.TOTOP, padTop=3)
        labelCont = Container(parent=rowCont, align=uiconst.TOPLEFT, height=TraitAttributeIcon.default_height, width=0)
        text = localization.GetByLabel('UI/InfoWindow/TraitWithoutNumber', color=Color.RGBtoHex(*COLOR_TEXT_HILITE), bonusText='')
        Label(parent=labelCont, text=text, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, color=COLOR_TEXT, tabs=(padLeft,), tabMargin=3)
        iconCont = FlowContainer(parent=rowCont, align=uiconst.TOTOP, padLeft=3, contentSpacing=(1, 1), autoHeight=True)
        old_OnSizeChange_NoBlock = iconCont._OnSizeChange_NoBlock

        def OnSizeChange_NoBlock_Hook(newWidth, newHeight):
            old_OnSizeChange_NoBlock(newWidth, newHeight)
            rowCont.height = newHeight

        iconCont._OnSizeChange_NoBlock = OnSizeChange_NoBlock_Hook
        attributeIDs = [ x[1] for x in sorted(data.items(), key=lambda data: int(data[0])) ]
        for attributeID in attributeIDs:
            TraitAttributeIcon(parent=iconCont, align=uiconst.NOALIGN, attributeID=attributeID)

    def GetLeftPad(self):
        return 40 * fontconst.fontSizeFactor

    def _FormatBonusLine(self, data, padLeft):
        text = self._GetBonusText(data)
        label = Label(parent=self, text=text, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=3, color=COLOR_TEXT, tabs=(padLeft,), tabMargin=TAB_MARGIN)
        return label

    def _GetBonusText(self, data):
        if 'bonus' in data:
            bonus = float(data['bonus'])
            value = round(bonus, 1)
            if int(bonus) == bonus:
                value = int(bonus)
            text = localization.GetByLabel('UI/InfoWindow/TraitWithNumber', color=COLOR_TEXT_HILITE_HEX, value=value, unit=units.get_display_name(int(data['unitID'])), bonusText=localization.GetByMessageID(int(data['nameID'])))
        else:
            text = localization.GetByLabel('UI/InfoWindow/TraitWithoutNumber', color=COLOR_TEXT_HILITE_HEX, bonusText=localization.GetByMessageID(int(data['nameID'])))
        return text


class TraitAttributeIcon(Container):
    default_name = 'TraitAttributeIcon'
    default_width = 30
    default_height = 30
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(TraitAttributeIcon, self).ApplyAttributes(attributes)
        self._iconOpacity = attributes.get('iconOpacity', TextColor.SECONDARY.opacity)
        self._iconHoverOpacity = attributes.get('iconHoverOpacity', TextColor.NORMAL.opacity)
        self.attributeID = attributes.attributeID
        iconID = cfg.infoBubbleElements[self.attributeID]['icon']
        self.icon = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=eveicon.get(iconID, default=iconID), opacity=self._iconOpacity)

    def GetHint(self):
        nameID = cfg.infoBubbleElements[self.attributeID]['nameID']
        descriptionID = cfg.infoBubbleElements[self.attributeID]['descriptionID']
        return '<b>' + localization.GetByMessageID(nameID) + '</b><br>' + localization.GetByMessageID(descriptionID)

    def OnMouseEnter(self):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        uicore.animations.FadeTo(self.icon, self.icon.opacity, self._iconHoverOpacity, duration=0.2)

    def OnMouseExit(self):
        uicore.animations.FadeTo(self.icon, self.icon.opacity, self._iconOpacity, duration=0.2)
