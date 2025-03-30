#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\filterBtn.py
import trinity
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.control.buttonIcon import ButtonIcon
import inventorycommon.const as invConst
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.shared.fittingScreen import BTN_TYPE_ALLIANCE_FITTINGS, BTN_TYPE_COMMUNITY_FITTINGS, BTN_TYPE_CORP_FITTINGS, BTN_TYPE_CURRENT_SHIP, BTN_TYPE_DRONES, BTN_TYPE_FITTING_SKILLS, BTN_TYPE_HISLOT, BTN_TYPE_LOSLOT, BTN_TYPE_MEDSLOT, BTN_TYPE_PERSONAL_FITTINGS, BTN_TYPE_RESOURCES, BTN_TYPE_RIGSLOT, BTN_TYPE_SHIP, BTN_TYPE_SKILLS, FILTER_DEFAULT_COMMUNITY_FITTING, FITTING_FILTER_HW_PREFIX, FITTING_FILTER_SHIP_PREFIX
from globalConfig.getFunctions import AreCommunityFittingsEnabled
from localization import GetByLabel
from carbonui.uicore import uicore
NOT_SELECTED_FRAME_COLOR = (1, 1, 1, 0.1)
SELECTED_FRAME_COLOR = (1, 1, 1, 0.3)

def AddHardwareButtons(parentCont, func, hintFunc = None, buttonSize = 32, prefix = FITTING_FILTER_HW_PREFIX):
    buttonData = ((BTN_TYPE_LOSLOT,
      'res:/UI/Texture/classes/Fitting/filterIconLowSlot.png',
      'UI/Fitting/FittingWindow/FilterLowSlot',
      False),
     (BTN_TYPE_MEDSLOT,
      'res:/UI/Texture/classes/Fitting/filterIconMediumSlot.png',
      'UI/Fitting/FittingWindow/FilterMedSlot',
      False),
     (BTN_TYPE_HISLOT,
      'res:/UI/Texture/classes/Fitting/filterIconHighSlot.png',
      'UI/Fitting/FittingWindow/FilterHiSlot',
      False),
     (BTN_TYPE_RIGSLOT,
      'res:/UI/Texture/classes/Fitting/filterIconRigSlot.png',
      'UI/Fitting/FittingWindow/FilterRigSlot',
      False),
     (BTN_TYPE_DRONES,
      'res:/UI/Texture/classes/Fitting/filterIconDrones.png',
      'UI/Fitting/FittingWindow/FilterDrones',
      False),
     (BTN_TYPE_SHIP,
      'res:/UI/Texture/classes/Fitting/tabFittings.png',
      'UI/Fitting/FittingWindow/FilterCanShipUse',
      True),
     (BTN_TYPE_RESOURCES,
      'res:/UI/Texture/classes/Fitting/filterIconResources.png',
      'UI/Fitting/FittingWindow/FilterResources',
      False),
     (BTN_TYPE_SKILLS,
      'res:/UI/Texture/classes/Fitting/filterIconSkills.png',
      'UI/Fitting/FittingWindow/FilterSkills',
      False))
    return AddFilterButtons(buttonData, prefix, parentCont, func, hintFunc=hintFunc, buttonSize=buttonSize)


def AddFittingFilterButtons(parentCont, func, hintFunc = None, buttonSize = 32):
    buttonData = [(BTN_TYPE_PERSONAL_FITTINGS,
      'res:/UI/Texture/WindowIcons/member.png',
      'UI/Fitting/FittingWindow/FilterPersonalFittings',
      False), (BTN_TYPE_CORP_FITTINGS,
      'res:/UI/Texture/WindowIcons/corporation.png',
      'UI/Fitting/FittingWindow/FilterCorpFittings',
      False)]
    if AreCommunityFittingsEnabled(sm.GetService('machoNet')):
        buttonData += [(BTN_TYPE_COMMUNITY_FITTINGS,
          'res:/UI/Texture/classes/Fitting/tabCommunityFits.png',
          'UI/Fitting/FilterCommunityFittings',
          FILTER_DEFAULT_COMMUNITY_FITTING)]
    if session.allianceid:
        buttonData += [(BTN_TYPE_ALLIANCE_FITTINGS,
          'res:/UI/Texture/classes/Fitting/tabAllianceFits.png',
          'UI/Fitting/FittingWindow/FilterAllianceFittings',
          False)]
    buttonData += [(BTN_TYPE_CURRENT_SHIP,
      'res:/UI/Texture/classes/Fitting/tabFittings.png',
      'UI/Fitting/FittingWindow/FilterCurrentHull',
      False), (BTN_TYPE_FITTING_SKILLS,
      'res:/UI/Texture/classes/Fitting/filterIconSkills.png',
      'UI/Fitting/FittingWindow/FilterSkillsForFitting',
      False)]
    return AddFilterButtons(buttonData, FITTING_FILTER_SHIP_PREFIX, parentCont, func, hintFunc=hintFunc, buttonSize=buttonSize)


def AddFilterButtons(buttonData, settingConfig, parentCont, func, hintFunc, buttonSize):
    btnDict = {}
    for buttonType, texturePath, labelPath, defaultValue in buttonData:
        btnSettingConfig = settingConfig % buttonType
        cont = FilterBtn(parent=parentCont, pos=(0,
         0,
         buttonSize,
         buttonSize), align=uiconst.NOALIGN, texturePath=texturePath, buttonType=buttonType, btnSettingConfig=btnSettingConfig, iconSize=buttonSize, func=func, args=(buttonType,), isChecked=settings.user.ui.Get(btnSettingConfig, defaultValue), hintFunc=hintFunc, hintLabelPath=labelPath)
        btnDict[buttonType] = cont

    return btnDict


def SetSettingForFilterBtns(flagID, btnDict):
    btnTypeToSelect = GetBtnTypeForFlagID(flagID)
    if btnTypeToSelect is None:
        return
    ChangeFilterBtnsStatesSlots(btnDict, btnTypeToSelect)


def ChangeFilterBtnsStatesSlots(btnDict, btnTypeToSelect):
    btnsToChange = (BTN_TYPE_LOSLOT,
     BTN_TYPE_MEDSLOT,
     BTN_TYPE_HISLOT,
     BTN_TYPE_RIGSLOT,
     BTN_TYPE_DRONES)
    return _ChangeFilterBtnsStates(btnDict, btnTypeToSelect, btnsToChange)


def _ChangeFilterBtnsStates(btnDict, btnTypeToSelect, btnsToChange):
    for btnType in btnsToChange:
        btn = btnDict.get(btnType, None)
        if btn is None:
            continue
        if btnTypeToSelect == btnType:
            settings.user.ui.Set(btn.btnSettingConfig, True)
            btn.SetSelected()
        else:
            settings.user.ui.Set(btn.btnSettingConfig, False)
            btn.SetDeselected()


def GetBtnTypeForFlagID(flagID):
    if flagID in invConst.loSlotFlags:
        return BTN_TYPE_LOSLOT
    if flagID in invConst.medSlotFlags:
        return BTN_TYPE_MEDSLOT
    if flagID in invConst.hiSlotFlags:
        return BTN_TYPE_HISLOT
    if flagID in invConst.rigSlotFlags + invConst.subsystemSlotFlags:
        return BTN_TYPE_RIGSLOT


class FilterBtn(ButtonIcon):
    default_colorSelected = (0.5, 0.5, 0.5, 0.1)
    checkmarkTexturePath = 'res:/ui/Texture/classes/Fitting/checkSmall.png'

    def ApplyAttributes(self, attributes):
        attributes.args = (self,) + attributes.args
        ButtonIcon.ApplyAttributes(self, attributes)
        self.loadingWheel = None
        self.hintFunc = attributes.hintFunc
        self.hintLabelPath = attributes.hintLabelPath
        self.checkmark = None
        self.checkmarkFill = None
        self.selectedIcon = None
        self.buttonType = attributes.buttonType
        self.frame = Frame(bgParent=self, color=eveThemeColor.THEME_FOCUS, opacity=0)
        self.hint = self.buttonType
        self.btnSettingConfig = attributes.btnSettingConfig
        if attributes.isChecked:
            self.SetSelected()

    def OnClick(self, *args):
        if not self.enabled:
            return
        if self.isSelected:
            self.SetDeselected()
        else:
            self.SetSelected()
        ButtonIcon.OnClick(self, args)

    def SetSelected(self):
        ButtonIcon.SetSelected(self)
        self.ConstructCheckmark()
        self.ConstructSelectedIcon()
        self.checkmark.display = True
        self.selectedIcon.display = True
        self.frame.color = eveThemeColor.THEME_FOCUS
        self.frame.opacity = 1

    def SetDeselected(self):
        ButtonIcon.SetDeselected(self)
        if self.checkmark:
            self.checkmark.display = False
        if self.selectedIcon:
            self.selectedIcon.display = False
        self.frame.opacity = 0

    def ConstructCheckmark(self):
        if self.checkmark:
            return
        self.checkmark = Container(name='checkmark', parent=self, pos=(1, 1, 12, 12), align=uiconst.BOTTOMRIGHT, idx=0)
        self.checkmarkFill = Fill(bgParent=self.checkmark, color=eveThemeColor.THEME_FOCUSDARK)
        Sprite(parent=self.checkmark, texturePath=self.checkmarkTexturePath, align=uiconst.CENTER, pos=(0, 0, 12, 12), state=uiconst.UI_DISABLED)

    def ConstructSelectedIcon(self):
        if self.selectedIcon:
            return
        self.selectedIcon = Sprite(name='selectedIcon', parent=self, align=uiconst.CENTER, width=self.iconSize, height=self.iconSize, texturePath=self.texturePath, state=uiconst.UI_DISABLED, color=eveThemeColor.THEME_FOCUS)

    def IsChecked(self):
        return bool(self.isSelected)

    def ShowLoading(self):
        if not self.loadingWheel:
            self.loadingWheel = LoadingWheel(name='myLoadingWheel', parent=self, align=uiconst.CENTER, width=self.width * 1.5, height=self.height * 1.5, opacity=0.5)
        self.loadingWheel.display = True

    def HideLoading(self):
        if self.loadingWheel:
            self.loadingWheel.display = False

    def GetHint(self):
        return GetByLabel(self.hintLabelPath)

    def LoadTooltipPanel(self, tootlipPanel, filterBtn):
        if self.hintFunc:
            self.hintFunc(tootlipPanel, filterBtn)

    def OnColorThemeChanged(self):
        super(FilterBtn, self).OnColorThemeChanged()
        if self.selectedIcon:
            self.selectedIcon.color = eveThemeColor.THEME_FOCUS
        if self.checkmarkFill:
            self.checkmarkFill.color = eveThemeColor.THEME_FOCUSDARK
        if self.frame.opacity:
            self.frame.color = eveThemeColor.THEME_FOCUS
        self.UpdateIconState(animate=False)


class DropdownFilter(Combo):
    default_height = 30
    default_iconSize = 30
    default_btnSize = 30
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.initialized = False
        self.default_callback = self.OnChange
        self.chargeController = attributes.chargeController
        Combo.ApplyAttributes(self, attributes)
        self.sr.backgroundFrame.Hide()
        self.sr.selected.Hide()
        self.hardwareList = attributes.hardwareList
        btnSize = attributes.get('btnSize', self.default_btnSize)
        iconSize = attributes.get('iconSize', self.default_iconSize)
        self.height = btnSize
        self.width = btnSize + 20
        self.frame = FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=1.0)
        self.chargeCont = Container(parent=self, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize))
        self.ContructCheckmark()
        self.ConstructChargeIcon(iconSize)
        self.initialized = True
        self.SetSelectedLook(self.GetValue(), False)

    def ContructCheckmark(self):
        self.checkmark = Container(name='checkmark', parent=self.chargeCont, pos=(0, 0, 12, 12), align=uiconst.BOTTOMRIGHT, idx=0)
        colorSelected = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
        Fill(bgParent=self.checkmark, color=colorSelected)
        Sprite(parent=self.checkmark, texturePath='res:/ui/Texture/classes/Fitting/checkSmall.png', align=uiconst.CENTER, pos=(0, 0, 12, 12), state=uiconst.UI_DISABLED)
        self.checkmark.display = False

    def ConstructChargeIcon(self, iconSize):
        self.chargeIcon = GlowSprite(name='chargeIcon', parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(0,
         0,
         iconSize,
         iconSize), iconClass=Icon, iconBlendMode=trinity.TR2_SBM_BLEND)

    def OnMouseEnter(self, *args):
        Combo.OnMouseEnter(self, *args)
        self.UpdateIconState(mousedOver=True)

    def OnMouseExit(self, *args):
        Combo.OnMouseExit(self, *args)
        self.UpdateIconState()

    def OnMouseDown(self, *args):
        Combo.OnMouseDown(self, *args)
        self.UpdateIconState(mousedDown=True)

    def OnMouseUp(self, *args):
        Combo.OnMouseUp(self, *args)
        self.UpdateIconState(mousedOver=True)

    def OnChange(self, cb, key, value):
        self.SetSelectedLook(value)

    def SetSelectedLook(self, typeID, report = True):
        if typeID > 0:
            usedWith = sm.GetService('info').GetUsedWithTypeIDs(typeID)
        else:
            usedWith = set()
        if report:
            self.chargeController.SetSelected(typeID, usedWith)
        if not self.initialized:
            return
        if typeID:
            if typeID > 0:
                self.chargeIcon.LoadIconByTypeID(typeID, None)
            else:
                self.chargeIcon.LoadIcon('res:/ui/texture/icons/14_64_16.png')
            self.checkmark.Show()
            self.frame.SetColorType(uiconst.COLORTYPE_UIHILIGHT)
        else:
            self.chargeIcon.LoadIcon('res:/ui/texture/icons/14_64_16.png')
            self.checkmark.Hide()
            self.frame.SetColorType(uiconst.COLORTYPE_UIBASECONTRAST)

    def GetScrollEntry(self, entryData):
        data = Combo.GetScrollEntry(self, entryData)
        data['typeID'] = entryData.returnValue if entryData.returnValue > 0 else None
        data['getIcon'] = True
        data['showinfo'] = False
        return data

    def GetEntryWidth(self, data):
        width = self.GetTextWidth(data['label'])
        return width + 30

    def GetEntryClass(self):
        from eve.client.script.ui.control.entries.item import Item
        return Item

    def UpdateIconState(self, mousedDown = False, mousedOver = False, animate = True):
        glowAmount = ButtonIcon.OPACITY_IDLE
        if mousedDown:
            if uicore.uilib.leftbtn:
                glowAmount = ButtonIcon.GLOWAMOUNT_MOUSECLICK
        elif mousedOver:
            glowAmount = ButtonIcon.GLOWAMOUNT_MOUSEHOVER
        if animate:
            uicore.animations.MorphScalar(self.chargeIcon, 'glowAmount', self.chargeIcon.glowAmount, glowAmount, duration=0.2)
        else:
            self.chargeIcon.glowAmount = glowAmount
