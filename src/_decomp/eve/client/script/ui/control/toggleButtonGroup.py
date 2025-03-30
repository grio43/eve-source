#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\toggleButtonGroup.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst, Density
from carbonui.primitives.container import Container
from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButton

class ToggleButtonGroup(Container):
    default_align = uiconst.TOPLEFT
    default_height = 32
    default_selectSound = uiconst.SOUND_BUTTON_CLICK
    default_btnClass = ToggleButtonGroupButton
    default_isOptional = False
    _button_size_dirty = False

    def __init__(self, autoHeight = None, btnClass = None, callback = None, density = Density.NORMAL, height = None, isOptional = None, selectSound = None, **kwargs):
        if btnClass is None:
            btnClass = self.default_btnClass
        if isOptional is None:
            isOptional = self.default_isOptional
        if selectSound is None:
            selectSound = self.default_selectSound
        if autoHeight is None:
            autoHeight = btnClass.AUTO_HEIGHT_ENABLED_BY_DEFAULT
        if height is None:
            height = self.default_height
        self._auto_height = autoHeight
        self._button_class = btnClass
        self._callback = callback
        self._density = density
        self._on_select_sound = selectSound
        self._optional = isOptional
        self._set_height = height
        self._buttons_by_id = {}
        self.buttons = []
        super(ToggleButtonGroup, self).__init__(height=height, **kwargs)

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        if self._density != value:
            self._density = value
            for button in self.buttons:
                button.density = self._density

    @property
    def buttonsByID(self):
        return dict(self._buttons_by_id)

    def AddButton(self, btnID, label = '', panel = None, iconPath = None, iconSize = None, hint = None, isDisabled = False, colorSelected = None, btnClass = None, getMenu = None, **kw):
        if btnClass is None:
            btnClass = self._button_class
        btn = btnClass(name=('Button_%s' % btnID), parent=self, controller=self, btnID=btnID, panel=panel, label=label, iconPath=iconPath, iconSize=iconSize, hint=hint, isDisabled=isDisabled, colorSelected=colorSelected, density=self._density, **kw)
        self.buttons.append(btn)
        self._buttons_by_id[btnID] = btn
        self._button_size_dirty = True
        if getMenu:
            btn.GetMenu = lambda *args, **kwargs: getMenu(btnID)
        for button in self.buttons:
            button.OnButtonAdded()

        return btn

    def GetPanel(self, btnID):
        return self._buttons_by_id[btnID].panel

    def ClearButtons(self):
        for btn in self.buttons:
            btn.Close()

        self.buttons = []
        self._buttons_by_id = {}

    def UpdateAlignment(self, *args, **kwargs):
        if self._button_size_dirty:
            self._UpdateButtonWidth()
            self._button_size_dirty = False
        if self._auto_height:
            minHeight = 0
            for button in self.buttons:
                try:
                    height = button.GetAutoHeight()
                except AttributeError:
                    pass
                else:
                    if height is not None:
                        minHeight = max(minHeight, height)

            self.height = minHeight
        return super(ToggleButtonGroup, self).UpdateAlignment(*args, **kwargs)

    def _UpdateButtonWidth(self):
        numButtons = len(self.buttons)
        for i, button in enumerate(self.buttons):
            isLast = i == numButtons - 1
            button.align = uiconst.TOALL if isLast else uiconst.TOLEFT_PROP
            button.width = 0 if isLast else 1.0 / numButtons

    def DeselectAll(self):
        oldBtnID = self.GetValue()
        for btn in self.buttons:
            btn.SetDeselected()
            if btn.panel:
                btn.panel.Hide()

        if self._callback is not None:
            self._callback(None, oldBtnID)

    def GetSelected(self):
        for btn in self.buttons:
            if btn.IsSelected():
                return btn.btnID

    def GetValue(self):
        return self.GetSelected()

    def SelectByID(self, btnID, animate = False):
        for btn in self.buttons:
            if btn.btnID == btnID:
                self.Select(btn, animate)

    def SetSelectedByID(self, btnID, animate = True):
        for btn in self.buttons:
            if btn.btnID == btnID:
                self.SetSelected(btn.btnID, animate=animate)

    def SelectFirst(self):
        for btn in self.buttons:
            if not btn.isDisabled:
                self.Select(btn)
                return

    def SetSelected(self, btnID, animate = True):
        self._DeselectCurrentlySelected(animate)
        if btnID is not None:
            self._SelectNewButton(animate, btnID)

    def _SelectNewButton(self, animate, btnID):
        btn = self.GetButton(btnID)
        btn.SetSelected(animate=animate)
        if btn.panel:
            btn.panel.Show()

    def GetButton(self, btnID):
        return self._buttons_by_id[btnID]

    def _DeselectCurrentlySelected(self, animate):
        btnID = self.GetSelected()
        if btnID is None:
            return
        btn = self.GetButton(btnID)
        if btn:
            btn.SetDeselected(animate=animate)
            panel = btn.panel
            if panel:
                panel.Hide()

    def Select(self, selectedBtn, animate = True, playSound = False, *args):
        if selectedBtn.isDisabled:
            return
        if playSound:
            PlaySound(self._on_select_sound)
        oldBtnID = self.GetSelected()
        self.SetSelected(selectedBtn.btnID, animate=animate)
        if self._callback is not None:
            self._callback(selectedBtn.btnID, oldBtnID)

    def EnableButton(self, btnID):
        for button in self.buttons:
            if button.btnID == btnID:
                button.label.opacity = 1
                button.isDisabled = False

    def DisableButton(self, btnID):
        for button in self.buttons:
            if button.btnID == btnID:
                button.label.opacity = 0.4
                button.isDisabled = True

    def IsOptional(self):
        return self._optional

    def Flush(self):
        self.ClearButtons()
