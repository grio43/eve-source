#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\typeEntry.py
import evelink.client
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from localization import GetByLabel

class TypeEntry(ContainerAutoSize):
    default_name = 'TypeEntry'
    default_align = uiconst.NOALIGN
    default_state = uiconst.UI_NORMAL
    default_height = 32

    def ApplyAttributes(self, attributes):
        super(TypeEntry, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.ConstructLayout()

    def ConstructLayout(self):
        typeIcon = TypeIcon(parent=self, align=uiconst.CENTERLEFT, typeID=self.typeID, height=32, width=32)
        sm.GetService('photo').GetIconByType(typeIcon, self.typeID)
        EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, text=evelink.type_link(self.typeID), state=uiconst.UI_NORMAL, left=37, autoFadeSides=15)

    def AnimEnter(self, offsetIdx):
        timeOffset = 0.05 * offsetIdx
        duration = 0.3
        animations.Tr2DScaleTo(self, (0.9, 0.9), (1.0, 1.0), duration=duration, timeOffset=timeOffset)
        animations.FadeIn(self, duration=2 * duration, timeOffset=timeOffset)


class TypeIcon(Sprite):
    default_name = 'TypeIcon'
    isDragObject = True
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(TypeIcon, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        animations.FadeTo(self, self.opacity, 1.5, duration=0.3)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, 1.0, duration=0.3)

    def GetHint(self):
        if self.hint:
            return self.hint
        if not self.typeID:
            return
        return evetypes.GetName(self.typeID)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        sm.GetService('info').ShowInfo(self.typeID)
