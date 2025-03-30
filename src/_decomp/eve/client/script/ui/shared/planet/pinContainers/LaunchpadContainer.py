#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\LaunchpadContainer.py
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import Label
import localization
from .StorageFacilityContainer import StorageFacilityContainer
from .. import planetCommon

class LaunchpadContainer(StorageFacilityContainer):
    default_name = 'LaunchpadContainer'
    panelIDs = [planetCommon.PANEL_LAUNCH] + StorageFacilityContainer.panelIDs

    def PanelLaunch(self):
        bp = sm.GetService('michelle').GetBallpark()
        text = None
        if bp is not None and not self.pin.IsInEditMode():
            customsOfficeIDs = sm.GetService('planetInfo').GetFunctionalCustomOfficeOrbitalsForPlanet(sm.GetService('planetUI').planetID)
            if len(customsOfficeIDs) > 0:
                try:
                    customsOfficeID = None
                    for ID in customsOfficeIDs:
                        customsOfficeID = ID
                        break

                    sm.GetService('planetUI').OpenPlanetCustomsOfficeImportWindow(customsOfficeID, self.pin.id)
                    self.CloseByUser()
                    return
                except UserError as e:
                    if e.msg == 'ShipCloaked':
                        text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadWhileCloaked')
                    else:
                        message = cfg.GetMessage(e.msg)
                        text = message.text

        if text is None:
            if self.pin.IsInEditMode():
                text = localization.GetByLabel('UI/PI/Common/CustomsOfficeNotBuilt')
            else:
                solarSystemID = sm.GetService('planetUI').GetCurrentPlanet().solarSystemID
                if solarSystemID == session.locationid and session.structureid is None:
                    text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadNotThere')
                else:
                    text = localization.GetByLabel('UI/PI/Common/CannotAccessLaunchpadLocation')
        return Label(parent=self.actionCont, text=text, align=uiconst.TOTOP)
