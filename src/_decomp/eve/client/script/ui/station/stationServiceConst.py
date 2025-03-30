#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\stationServiceConst.py
from eve.common.lib import appConst
from eve.common.script.util.insuranceConst import INSURANCE_ICON
from eveexceptions import UserError
from localization import GetByLabel
from utillib import KeyVal
import structures
serviceIDAlwaysPresent = -1
serviceData = (KeyVal(name='charcustomization', command='OpenCharacterCustomization', label=GetByLabel('UI/Station/CharacterRecustomization'), iconID='res:/UI/Texture/WindowIcons/charcustomization.png', serviceID=serviceIDAlwaysPresent, stationServiceIDs=(serviceIDAlwaysPresent,), disableButtonIfNotAvailable=False),
 KeyVal(name='medical', command='OpenMedical', label=GetByLabel('UI/Medical/Medical'), iconID='res:/ui/Texture/WindowIcons/cloneBay.png', serviceID=structures.SERVICE_MEDICAL, stationServiceIDs=(appConst.stationServiceCloning,
  appConst.stationServiceSurgery,
  appConst.stationServiceDNATherapy,
  appConst.stationServiceJumpCloneFacility), disableButtonIfNotAvailable=False),
 KeyVal(name='repairshop', command='OpenRepairshop', label=GetByLabel('UI/Station/Repairshop'), iconID='res:/ui/Texture/WindowIcons/repairshop.png', serviceID=structures.SERVICE_REPAIR, stationServiceIDs=(appConst.stationServiceRepairFacilities,), disableButtonIfNotAvailable=True),
 KeyVal(name='reprocessingPlant', command='OpenReprocessingPlant', label=GetByLabel('UI/Station/ReprocessingPlant'), iconID='res:/UI/Texture/WindowIcons/Reprocess.png', serviceID=structures.SERVICE_REPROCESSING, stationServiceIDs=(appConst.stationServiceReprocessingPlant,), disableButtonIfNotAvailable=True),
 KeyVal(name='market', command='OpenMarket', label=GetByLabel('UI/Station/Market'), iconID='res:/ui/Texture/WindowIcons/market.png', serviceID=structures.SERVICE_MARKET, stationServiceIDs=(appConst.stationServiceMarket,), disableButtonIfNotAvailable=False),
 KeyVal(name='fitting', command='OpenFitting', label=GetByLabel('UI/Station/Fitting'), iconID='res:/ui/Texture/WindowIcons/fitting.png', serviceID=structures.SERVICE_FITTING, stationServiceIDs=(appConst.stationServiceFitting,), disableButtonIfNotAvailable=False),
 KeyVal(name='industry', command='OpenIndustry', label=GetByLabel('UI/Industry/Industry'), iconID='res:/UI/Texture/WindowIcons/Industry.png', serviceID=structures.SERVICE_INDUSTRY, stationServiceIDs=(appConst.stationServiceFactory, appConst.stationServiceLaboratory), disableButtonIfNotAvailable=False),
 KeyVal(name='navyoffices', command='OpenRelevantFWWindow', label=GetByLabel('UI/Station/MilitiaOffice'), iconID='res:/ui/Texture/WindowIcons/factionalwarfare.png', serviceID=structures.SERVICE_FACTION_WARFARE, stationServiceIDs=(appConst.stationServiceNavyOffices,), disableButtonIfNotAvailable=False),
 KeyVal(name='insurance', command='OpenInsurance', label=GetByLabel('UI/Station/Insurance'), iconID=INSURANCE_ICON, serviceID=structures.SERVICE_INSURANCE, stationServiceIDs=(appConst.stationServiceInsurance,), disableButtonIfNotAvailable=True),
 KeyVal(name='lpstore', command='OpenLpstore', label=GetByLabel('UI/Station/LPStore'), iconID='res:/ui/Texture/WindowIcons/lpstore.png', serviceID=structures.SERVICE_LOYALTY_STORE, stationServiceIDs=(appConst.stationServiceLoyaltyPointStore,), disableButtonIfNotAvailable=True),
 KeyVal(name='securityoffice', command='OpenSecurityOffice', label=GetByLabel('UI/Station/SecurityOffice'), iconID='res:/UI/Texture/WindowIcons/concord.png', serviceID=structures.SERVICE_SECURITY_OFFICE, stationServiceIDs=(appConst.stationServiceSecurityOffice,), disableButtonIfNotAvailable=True),
 KeyVal(name='moonmining', command='', label=GetByLabel('UI/Moonmining/MoonDrillService'), iconID='res:/UI/Texture/WindowIcons/moonDrill.png', serviceID=structures.SERVICE_MOONMINING, stationServiceIDs=(), disableButtonIfNotAvailable=False),
 KeyVal(name='jumpbridge', command='', label=GetByLabel('UI/Structures/ServiceJumpBridge'), iconID='res:/UI/Texture/WindowIcons/navigation.png', serviceID=structures.SERVICE_JUMP_BRIDGE, stationServiceIDs=(), disableButtonIfNotAvailable=False),
 KeyVal(name='cynobeacon', command='', label=GetByLabel('UI/Structures/ServiceJumpBeacon'), iconID='res:/UI/Texture/WindowIcons/navigation.png', serviceID=structures.SERVICE_CYNO_BEACON, stationServiceIDs=(), disableButtonIfNotAvailable=False),
 KeyVal(name='cynojammer', command='', label=GetByLabel('UI/Structures/ServiceCynoJammer'), iconID='res:/UI/Texture/classes/InfluenceBar/effectCyno.png', serviceID=structures.SERVICE_CYNO_JAMMER, stationServiceIDs=(), disableButtonIfNotAvailable=False),
 KeyVal(name='automoonmining', command='', label=GetByLabel('UI/Moonmining/AutoMoonDrillService'), iconID='res:/UI/Texture/WindowIcons/moonDrill.png', serviceID=structures.SERVICE_AUTOMOONMINING, stationServiceIDs=(), disableButtonIfNotAvailable=False))
serviceDataByNameID = {data.name:data for data in serviceData}
serviceDataByServiceID = {data.serviceID:data for data in serviceData}
UPWELL_STANDARD_SERVICES = {name:serviceDataByNameID.get(name) for name in ['charcustomization',
 'fitting',
 'insurance',
 'repairshop']}

class NewbieShipError(UserError):
    pass
