#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\containersByPinType.py
from eve.client.script.ui.shared.planet.pinContainers.CommandCenterContainer import CommandCenterContainer
from eve.client.script.ui.shared.planet.pinContainers.LaunchpadContainer import LaunchpadContainer
from eve.client.script.ui.shared.planet.pinContainers.LinkContainer import LinkContainer
from eve.client.script.ui.shared.planet.pinContainers.ProcessorContainer import ProcessorContainer
from eve.client.script.ui.shared.planet.pinContainers.StorageFacilityContainer import StorageFacilityContainer
from eve.client.script.ui.shared.planet.pinContainers.ecuContainer import ECUContainer
from eve.client.script.ui.shared.planet.pinContainers.obsoletePinContainer import ObsoletePinContainer
from eve.common.lib import appConst
containerClsByPinType = {appConst.groupCommandPins: CommandCenterContainer,
 appConst.groupExtractorPins: ObsoletePinContainer,
 appConst.groupExtractionControlUnitPins: ECUContainer,
 appConst.groupProcessPins: ProcessorContainer,
 appConst.groupSpaceportPins: LaunchpadContainer,
 appConst.groupStoragePins: StorageFacilityContainer,
 appConst.groupPlanetaryLinks: LinkContainer}
