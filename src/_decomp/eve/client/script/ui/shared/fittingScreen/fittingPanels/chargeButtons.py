#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\chargeButtons.py
import evetypes
import inventorycommon
import signals
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.shared.fittingScreen import CHARGE_FILTER_ALL_CHARGES
from signals.signalUtil import ChangeSignalConnect
from utillib import KeyVal
from eveservices.menu import GetMenuService

class ModuleChargeRadioButton(ButtonIcon):
    isDragObject = True
    default_iconClass = Icon
    default_iconBlendMode = trinity.TR2_SBM_BLEND
    default_iconSize = 32
    checkmarkTexturePath = 'res:/ui/Texture/classes/Fitting/checkSmall.png'

    def ApplyAttributes(self, attributes):
        self.moduleTypeID = attributes.typeID
        self.usedWithChargesIDs = attributes.usedWithChargesIDs
        attributes.texturePath = inventorycommon.typeHelpers.GetIconFile(self.moduleTypeID) if self.moduleTypeID else ''
        ButtonIcon.ApplyAttributes(self, attributes)
        self.isSelected = attributes.isSelected
        self.controller = attributes.controller
        self.checkmark = None
        self.ChangeSignalConnection()
        self.colorSelected = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
        self.hint = attributes.moduleName
        self.frame = FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.75)
        sm.GetService('photo').GetIconByType(self.icon, self.moduleTypeID)
        if self.isSelected:
            self.SetSelected()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_selected_changed, self.OnSelectedChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def GetModuleType(self):
        return self.moduleTypeID

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.moduleTypeID, includeMarketDetails=True)

    def OnClick(self, *args):
        if self.isSelected:
            self.SetDeselected()
        else:
            self.SetSelected()
        self.controller.OnBtnClicked(self.moduleTypeID, self.usedWithChargesIDs)

    def SetSelected(self):
        self.isSelected = True
        self.ConstructCheckmark()
        self.checkmark.display = True
        self.frame.SetColorType(uiconst.COLORTYPE_UIHILIGHT)

    def SetDeselected(self):
        self.isSelected = False
        if self.checkmark:
            self.checkmark.display = False
        self.frame.SetColorType(uiconst.COLORTYPE_UIBASECONTRAST)

    def OnSelectedChanged(self, moduleTypeID):
        if moduleTypeID == self.moduleTypeID:
            self.SetSelected()
        else:
            self.SetDeselected()

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        self.controller = None
        Container.Close(self)

    def ConstructCheckmark(self):
        if self.checkmark:
            return
        self.checkmark = Container(name='checkmark', parent=self, pos=(0, 0, 12, 12), align=uiconst.BOTTOMRIGHT, idx=0)
        Fill(bgParent=self.checkmark, color=self.colorSelected)
        Sprite(parent=self.checkmark, texturePath=self.checkmarkTexturePath, align=uiconst.CENTER, pos=(0, 0, 12, 12), state=uiconst.UI_DISABLED)

    def GetDragData(self):
        keyVal = KeyVal(__guid__='listentry.GenericMarketItem', typeID=self.moduleTypeID, label=evetypes.GetName(self.moduleTypeID))
        return [keyVal]

    def SetModuleTypeID(self, typeID, usedWithChargesIDs):
        self.moduleTypeID = typeID
        self.usedWithChargesIDs = usedWithChargesIDs
        self.UpdateModuleIcon()

    def UpdateModuleIcon(self):
        texturePath = inventorycommon.typeHelpers.GetIconFile(self.moduleTypeID) if self.moduleTypeID else ''
        self.SetTexturePath(texturePath)


class ModuleChargeController(object):

    def __init__(self, settingName, isToggle = True):
        self.settingName = settingName
        self.isToggle = isToggle
        self.moduleTypeSelected = settings.char.ui.Get(self.settingName, None)
        if self.moduleTypeSelected:
            self.isActive = True
            if self.moduleTypeSelected == CHARGE_FILTER_ALL_CHARGES:
                self.selectedUsedWith = set()
            else:
                self.selectedUsedWith = sm.GetService('info').GetUsedWithTypeIDs(self.moduleTypeSelected)
        else:
            self.isActive = False
            self.selectedUsedWith = set()
        self.on_selected_changed = signals.Signal(signalName='on_selected_changed')

    def OnBtnClicked(self, moduleTypeID, usedWith):
        return self.SetSelected(moduleTypeID, usedWith)

    def SetSelected(self, moduleTypeID, usedWith):
        if self.isToggle and self.moduleTypeSelected == moduleTypeID:
            self.moduleTypeSelected = None
            self.selectedUsedWith = set()
        else:
            self.moduleTypeSelected = moduleTypeID
            self.selectedUsedWith = usedWith
        self.isActive = bool(moduleTypeID)
        settings.char.ui.Set(self.settingName, self.moduleTypeSelected)
        self.on_selected_changed(self.moduleTypeSelected)

    def GetSelectModuleTypeID(self):
        return self.moduleTypeSelected

    def GetUsedWithForSelectedModule(self):
        return self.selectedUsedWith

    def IsFilterActive(self):
        return self.isActive > 0

    def ResetSelected(self):
        self.moduleTypeSelected = None
        self.selectedUsedWith = set()
        self.SetActiveState(False)

    def SetActiveState(self, isActive):
        self.isActive = isActive

    def ClearSignals(self):
        self.on_selected_changed.clear()
