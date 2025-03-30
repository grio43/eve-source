#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\selectedInfoCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import Label, EveCaptionSmall, EveHeaderSmall
from eve.common.lib import appConst
from localization import GetByLabel

class SelectedInfoCont(ContainerAutoSize):
    default_name = 'SelectedInfoCont'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.shouldShow = True
        setActiveCallback = attributes.setActiveCallback
        self.ownerIcon = OwnerIcon(parent=self, align=uiconst.TOPLEFT, pos=(0, -6, 60, 60))
        self.labelCont = ContainerAutoSize(parent=self, pos=(72, 12, 0, 30), align=uiconst.TOPLEFT)
        self.regionLabel = LocationLabel(parent=self.labelCont, align=uiconst.TOLEFT, caption=GetByLabel('UI/Common/LocationTypes/Region'), setActiveCallback=setActiveCallback)
        self.constLabel = LocationLabel(parent=self.labelCont, align=uiconst.TOLEFT, caption=GetByLabel('UI/Common/LocationTypes/Constellation'), padLeft=14, setActiveCallback=setActiveCallback)
        self.systemLabel = LocationLabel(parent=self.labelCont, align=uiconst.TOLEFT, caption=GetByLabel('UI/Common/LocationTypes/SolarSystem'), padLeft=14, setActiveCallback=setActiveCallback)
        self.Update()

    def Update(self, solarSystemID = None, constID = None, regionID = None):
        self.UpdateFactionLogoIcon(constID, regionID, solarSystemID)
        self.systemLabel.Update(solarSystemID)
        self.constLabel.Update(constID)
        self.regionLabel.Update(regionID)
        self.UpdateDisplayState()

    def UpdateDisplayState(self):
        if not self.shouldShow:
            self.Hide()
            return
        if self.systemLabel.GetLocationID() or self.constLabel.GetLocationID() or self.regionLabel.GetLocationID():
            self.Show()
        else:
            self.Hide()

    def SetShouldShow(self, value):
        self.shouldShow = value

    def UpdateFactionLogoIcon(self, constID, regionID, solarSystemID):
        factionSvc = sm.GetService('faction')
        if solarSystemID:
            factionID = factionSvc.GetFactionOfSolarSystem(solarSystemID)
            factionIDs = [factionID]
        elif constID:
            factionIDs = factionSvc.GetFactionsOfConstellation(constID)
        elif regionID:
            factionIDs = factionSvc.GetFactionsOfRegion(regionID)
        else:
            factionIDs = []
        factionID = factionIDs[0] if factionIDs else None
        if factionID:
            self.ownerIcon.SetOwnerID(factionID)
            self.ownerIcon.Show()
        else:
            self.ownerIcon.Hide()


class LocationLabel(ContainerAutoSize):
    default_name = 'LocationLabel'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        caption = attributes.caption
        self.setActiveCallback = attributes.setActiveCallback
        self.locationID = None
        EveHeaderSmall(parent=self, align=uiconst.TOPLEFT, text=caption, state=uiconst.UI_DISABLED, opacity=0.5)
        self.label = Label(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=12)

    def Update(self, locationID):
        self.locationID = locationID
        if locationID:
            text = self.GetLocationName()
            self.Enable()
        else:
            text = "<color='0x33ffffff'>-</color>"
            self.Disable()
        self.label.SetText(text)

    def GetLocationID(self):
        return self.locationID

    def GetLocationName(self):
        if self.locationID:
            return cfg.evelocations.Get(self.locationID).locationName
        return ''

    def OnClick(self, *args):
        self.setActiveCallback(self.locationID)

    def OnMouseEnter(self, *args):
        animations.FadeTo(self, self.opacity, 1.5, duration=0.3)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, 1.0, duration=0.3)
