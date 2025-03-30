#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveLabelVertical.py
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from math import pi

class VerticalLabel(Transform):
    default_rotation = pi * 0.5
    default_wrapWidth = 100
    default_rotationCenter = (0.0, 0.0)

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        labelText = attributes.text
        wrapWidth = attributes.get('wrapWidth', self.default_wrapWidth)
        labelClass = attributes.get('labelClass', EveLabelSmall)
        self.label = labelClass(text=labelText, parent=self, maxLines=2, wrapWidth=wrapWidth)
        self.width = self.label.width
        self.height = self.label.height
        self.rotation = attributes.get('rotation', self.default_rotation)
        self.rotationCenter = attributes.get('rotationCenter', self.default_rotationCenter)

    def SetText(self, text):
        self.label.SetText(text)
