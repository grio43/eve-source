#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\shared\paymentselector.py
import logging
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
logger = logging.getLogger(__name__)
RADIO_FILL = 'res:/UI/Texture/classes/RadioButton/fill.png'
RADIO_FRAME = 'res:/UI/Texture/classes/RadioButton/frame.png'
RADIO_GLOW = 'res:/UI/Texture/classes/RadioButton/innerGlow.png'
RADIO_SELECTED = 'res:/UI/Texture/classes/RadioButton/selected.png'
BACKGROUND_COLOR_INACTIVE = (0.1, 0.1, 0.1, 1.0)
BACKGROUND_COLOR_ACTIVE = (0.2, 0.2, 0.2, 1.0)

class RadioButtonComponent(Container):
    default_name = 'RadioButtonComponent'
    default_fillColor = (1.0, 1.0, 1.0, 0.9)

    def ApplyAttributes(self, attributes):
        super(RadioButtonComponent, self).ApplyAttributes(attributes)
        fillColor = attributes.get('fillColor', self.default_fillColor)
        self.radioFill = Sprite(parent=self, texturePath=RADIO_FILL, width=8, height=8, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, color=fillColor)
        Sprite(parent=self, texturePath=RADIO_FRAME, width=12, height=12, align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=(0.3, 0.3, 0.3, 0.8))

    def OnSelect(self):
        self.radioFill.Show()

    def OnDeselect(self):
        self.radioFill.Hide()


class PaymentSelectionBox(Container):

    def ApplyAttributes(self, attributes):
        super(PaymentSelectionBox, self).ApplyAttributes(attributes)
        self.selectionValue = attributes.selectionValue
        self.contents = attributes.contents
        self.contents.SetParent(self)
        radioBoxContainer = Container(name='radioBoxContainer', parent=self, align=uiconst.TOLEFT_NOPUSH, width=24, padLeft=12)
        self.radioBox = RadioButtonComponent(parent=radioBoxContainer, align=uiconst.CENTER, width=24, height=12)
        self.selectedBackground = Sprite(name='selectedBackground', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/Vgs/currencySelectorActive.png', opacity=0.0, state=uiconst.UI_DISABLED)
        self.deselectedBackground = Sprite(name='deselectedBackground', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/Vgs/currencySelectorInactive.png', opacity=1.0, state=uiconst.UI_DISABLED)

    def OnClick(self, *args):
        super(PaymentSelectionBox, self).OnClick(*args)
        self.parent.Select(self)

    def OnSelect(self):
        self.deselectedBackground.opacity = 0.0
        self.selectedBackground.opacity = 1.0
        self.radioBox.OnSelect()

    def OnDeSelect(self):
        self.deselectedBackground.opacity = 1.0
        self.selectedBackground.opacity = 0.0
        self.radioBox.OnDeselect()


class PaymentSelector(Container):

    def ApplyAttributes(self, attributes):
        super(PaymentSelector, self).ApplyAttributes(attributes)
        defaultValue = attributes.defaultValue
        self.onSelect = attributes.onSelect
        self.selected = defaultValue
        self.selectedBox = None
        self.selectionBoxes = {}
        numButtons = len(attributes.optionsDict)
        for k, v in attributes.optionsDict.iteritems():
            box = PaymentSelectionBox(parent=self, align=uiconst.TOLEFT_PROP, selectionValue=k, contents=v, padLeft=10, state=uiconst.UI_NORMAL)
            box.width = 1.0 / numButtons
            self.selectionBoxes[k] = box

        if self.selectionBoxes:
            self._SetDefaultSelected(defaultValue)

    def _SetDefaultSelected(self, defaultValue):
        if defaultValue:
            for box in self.selectionBoxes.values():
                if box.selectionValue == defaultValue:
                    self.Select(box)

        else:
            self.Select(self.selectionBoxes.values()[0])

    def Select(self, selectionBox):
        if selectionBox == self.selectedBox:
            return
        if self.selectedBox is not None:
            self.selectedBox.OnDeSelect()
        self.selectedBox = selectionBox
        self.selected = selectionBox.selectionValue
        selectionBox.OnSelect()
        if self.onSelect:
            self.onSelect(selectionBox.selectionValue)

    def SelectValue(self, value):
        try:
            self.Select(self.selectionBoxes[value])
        except KeyError:
            logger.warn('Value %s does not exist' % str(value))

    def GetSelectedValue(self):
        return self.selected
