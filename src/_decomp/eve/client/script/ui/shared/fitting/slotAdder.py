#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\slotAdder.py
import math
import dogma.data as dogma_data
from carbonui.const import UI_NORMAL
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor, GetBaseShapeSize
import telemetry

class SlotAdder(object):

    def __init__(self, controller, slotClass):
        self.controller = controller
        self.slotClass = slotClass
        scaleFactor = GetScaleFactor()
        self.width = int(round(44.0 * scaleFactor))
        self.height = int(round(54.0 * scaleFactor))
        self.rad = int(239 * scaleFactor)
        self.center = GetBaseShapeSize() / 2

    def AddSlot(self, parent, flagID, slotClass = None):
        left, top, cos, sin = self.GetPositionNumbers(self.angle)
        radCosSin = (self.rad,
         cos,
         sin,
         self.center,
         self.center)
        if slotClass is None:
            slotClass = self.slotClass
        ret = slotClass(name='%s' % flagID, parent=parent, pos=(left,
         top,
         self.width,
         self.height), rotation=-math.radians(self.angle), opacity=0.0, radCosSin=radCosSin, controller=self.controller.GetSlotController(flagID))
        self.angle += self.stepSize
        return ret

    def StartGroup(self, arcStart, arcLength, numSlots):
        self.angle = arcStart
        self.stepSize = arcLength / numSlots

    @telemetry.ZONE_METHOD
    def GetPositionNumbers(self, angle):
        cos = math.cos((angle - 90.0) * math.pi / 180.0)
        sin = math.sin((angle - 90.0) * math.pi / 180.0)
        left = int(round(self.rad * cos + self.center - self.width / 2.0))
        top = int(round(self.rad * sin + self.center - self.height / 2.0))
        return (left,
         top,
         cos,
         sin)


class HardpointAdder(object):
    iconAngle = 313.2
    markerAngle = 310
    iconRad = 276
    markerRad = 278
    iconSize = 16

    def __init__(self, attributeConst, cX, cY, isleftSide = False):
        self.isleftSide = isleftSide
        self.attribute = dogma_data.get_attribute(attributeConst)
        self.cX = cX
        self.cY = cY
        self.slots = []
        self.step = 3.0 / GetScaleFactor()
        if not self.isleftSide:
            self.iconAngle += 1.8
            self.markerAngle += 1.8

    def AddIcon(self, parent, texturePath, tooltipCallback):
        angle = self.iconAngle
        iconRad = int(self.iconRad * GetScaleFactor())
        left, top, cos, sin = self.GetPositionNumbers(angle, iconRad, offset=self.iconSize / 2)
        icon = Sprite(name='%s_Icon' % self.attribute.name, texturePath=texturePath, parent=parent, state=UI_NORMAL, hint=dogma_data.get_attribute_display_name(self.attribute.attributeID), pos=(left,
         top,
         self.iconSize,
         self.iconSize), idx=0)
        icon.LoadTooltipPanel = tooltipCallback

    def AddMarkers(self, parent):
        markerRad = int(self.markerRad * GetScaleFactor())
        angle = self.markerAngle - self.step * 7.5
        for i in xrange(8):
            left, top, cos, sin = self.GetPositionNumbers(angle, markerRad, offset=8)
            icon = MarkerIcon(name='%s_%s_Marker' % (i, self.attribute.name), parent=parent, state=UI_NORMAL, pos=(left,
             top,
             16,
             16), hint=dogma_data.get_attribute_display_name(self.attribute.attributeID), idx=0)
            icon.display = False
            self.slots.insert(0, icon)
            angle += self.step

    def GetPositionNumbers(self, angle, rad, offset):
        if self.isleftSide:
            angle = 180 - angle
        cos = math.cos(angle * math.pi / 180.0)
        sin = math.sin(angle * math.pi / 180.0)
        left = int(round(rad * cos + self.cX - offset))
        top = int(round(rad * sin + self.cY - offset))
        return (left,
         top,
         cos,
         sin)


class MarkerIcon(Sprite):
    slotTaken = 'res:/UI/Texture/classes/Fitting/slotTaken.png'
    slotLeft = 'res:/UI/Texture/classes/Fitting/slotLeft.png'
    default_texturePath = slotLeft
    slotColorNormal = (1.0, 1.0, 1.0, 0.7)
    slotColorRed = (1.0, 0.0, 0.0, 0.7)
    slotColorYellow = (1.0, 1.0, 0.0, 0.7)

    def ModifyLook(self, slotIdx, slotsLeft, slotsFitted, slotsAddition):
        if slotIdx < slotsFitted:
            self.texturePath = self.slotTaken
        else:
            self.texturePath = self.slotLeft
        if slotIdx < slotsLeft + slotsFitted:
            if slotIdx < slotsLeft + slotsFitted + slotsAddition:
                self.SetRGBA(*self.slotColorNormal)
            else:
                self.SetRGBA(*self.slotColorRed)
            self.display = True
        elif slotIdx < slotsLeft + slotsFitted + slotsAddition:
            self.SetRGBA(*self.slotColorYellow)
            self.display = True
        else:
            self.display = False
