#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\fuelConts.py
import math
import appConst
import carbonui
import eveicon
import evetypes
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from localization import GetByLabel
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE
from sovereignty.client.sovHub.hubUtil import GetIconTexturePathForReagent

class BaseFuelCont(Container):
    default_height = 120
    default_width = 120
    default_align = carbonui.Align.TOPLEFT
    tooltipLabelPath = ''
    texturePath = ''
    reagentTypeID = None

    def ApplyAttributes(self, attributes):
        self.hubController = attributes.hubController
        super(BaseFuelCont, self).ApplyAttributes(attributes)
        self.ConstructUI()
        if hasattr(self.hubController, 'on_online_state_changed'):
            self.hubController.on_online_state_changed.connect(self.OnOnlineStateChanged)
        if hasattr(self.hubController, 'on_upgrades_changed'):
            self.hubController.on_upgrades_changed.connect(self.OnUpgradesChanged)

    def ConstructUI(self):
        self.timeLabel = carbonui.TextHeadline(parent=self, text='', align=carbonui.Align.CENTER, pickState=carbonui.PickState.ON)
        self.timeLabel.hint = GetByLabel(self.tooltipLabelPath)
        self.amountLabel = carbonui.TextBody(parent=self, text='', align=carbonui.Align.CENTER, top=20, color=carbonui.TextColor.SECONDARY)
        self.perHourLabel = carbonui.TextBody(parent=self, text='', align=carbonui.Align.CENTER, top=35, color=carbonui.TextColor.SECONDARY)
        icon = Sprite(parent=self, align=carbonui.Align.CENTER, pos=(0, -24, 16, 16), texturePath=self.texturePath)
        icon.GetMenu = lambda *args: GetMenuService().GetMenuFromItemIDTypeID(None, self.reagentTypeID)
        self.gaugeCircular = GaugeCircular(parent=self, showMarker=False, radius=55, lineWidth=3.0, startAngle=math.pi / 2, align=carbonui.Align.CENTER, colorStart=eveColor.CRYO_BLUE, colorEnd=eveColor.CRYO_BLUE, glow=True, glowBrightness=0.3)

    def OnOnlineStateChanged(self, typeID):
        self.LoadUI()

    def OnUpgradesChanged(self):
        self.LoadUI()

    def LoadUI(self):
        numHoursLeftProgress = self.hubController.GetTimeLeftProgressForTypeID(self.reagentTypeID)
        numHoursLeftText = self.hubController.GetTimeLeftTextForTypeID(self.reagentTypeID)
        if numHoursLeftProgress is None:
            self.timeLabel.text = numHoursLeftText
            self.gaugeCircular.SetValue(0)
        else:
            self.timeLabel.text = numHoursLeftText
            self.gaugeCircular.SetValue(min(1.0, numHoursLeftProgress))
        fuelInfo = self.hubController.GetReagentForTypeID(self.reagentTypeID)
        if fuelInfo == DATA_NOT_AVAILABLE:
            self.amountLabel.text = GetByLabel('UI/Sovereignty/HubPage/NotAvailable', color=eveColor.GUNMETAL_HEX)
        elif fuelInfo:
            self.amountLabel.text = fuelInfo.amount_now
        else:
            self.amountLabel.text = 0
        perHour = self.hubController.GetReagentConsumptionForTypeID(self.reagentTypeID)
        if perHour == DATA_NOT_AVAILABLE:
            self.perHourLabel.text = GetByLabel('UI/Sovereignty/HubPage/NotAvailable', color=eveColor.GUNMETAL_HEX)
        else:
            self.perHourLabel.text = GetByLabel('UI/Sovereignty/AmountPerHour', value=perHour)

    def Close(self):
        with ExceptionEater('Closing BaseFuelCont'):
            if hasattr(self.hubController, 'on_online_state_changed'):
                self.hubController.on_online_state_changed.disconnect(self.OnOnlineStateChanged)
            if hasattr(self.hubController, 'on_upgrades_changed'):
                self.hubController.on_upgrades_changed.disconnect(self.OnUpgradesChanged)
            self.hubController = None
        super(BaseFuelCont, self).Close()


class FuelMagmaCont(BaseFuelCont):
    tooltipLabelPath = 'UI/Sovereignty/SovHub/HubWnd/TimeUntilMagmaRunsOut'
    texturePath = eveicon.magmatic_gas
    reagentTypeID = appConst.typeColonyReagentLava


class FuelIceCont(BaseFuelCont):
    tooltipLabelPath = 'UI/Sovereignty/SovHub/HubWnd/TimeUntilIceRunsOut'
    texturePath = eveicon.superionic_ice
    reagentTypeID = appConst.typeColonyReagentIce


class StartupCostCont(ContainerAutoSize):
    default_align = carbonui.Align.TOTOP

    def ApplyAttributes(self, attributes):
        self.hubController = attributes.hubController
        super(StartupCostCont, self).ApplyAttributes(attributes)
        self.ConstructUI()
        self.hubController.on_online_state_changed.connect(self.OnOnlineStateChanged)
        self.hubController.on_upgrades_changed.connect(self.OnUpgradesChanged)

    def ConstructUI(self):
        header = carbonui.TextDetail(parent=self, text=GetByLabel('UI/Sovereignty/SovHub/HubWnd/StartupCostHeader'), color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP, pickState=carbonui.PickState.ON)
        innerCont = ContainerAutoSize(parent=self, align=carbonui.Align.TOTOP)
        cont = ContainerAutoSize(name='lavaCont', parent=innerCont)
        self.lavaIcon = Sprite(name='lavaIcon', parent=cont, align=carbonui.Align.CENTERLEFT, pos=(0, 0, 16, 16), texturePath=GetIconTexturePathForReagent(appConst.typeColonyReagentLava), color=eveColor.TUNGSTEN_GREY)
        self.lavaIcon.hint = evetypes.GetName(appConst.typeColonyReagentLava)
        self.lavaLabel = carbonui.TextHeader(parent=cont, text='000', align=carbonui.Align.CENTERLEFT, left=20)
        cont = ContainerAutoSize(name='iceCont', parent=innerCont, left=100)
        self.iceIcon = Sprite(name='iceIcon', parent=cont, align=carbonui.Align.CENTERLEFT, pos=(0, 0, 16, 16), texturePath=GetIconTexturePathForReagent(appConst.typeColonyReagentIce), color=eveColor.TUNGSTEN_GREY)
        self.iceIcon.hint = evetypes.GetName(appConst.typeColonyReagentIce)
        self.iceLabel = carbonui.TextHeader(parent=cont, text='000', align=carbonui.Align.CENTERLEFT, left=20)

    def OnOnlineStateChanged(self, typeID):
        self.LoadUI()

    def OnUpgradesChanged(self):
        self.LoadUI()

    def LoadUI(self):
        startupLava = self.hubController.GetStartupCostForTypeID(appConst.typeColonyReagentLava)
        self.lavaLabel.text = startupLava or '000'
        startupIce = self.hubController.GetStartupCostForTypeID(appConst.typeColonyReagentIce)
        self.iceLabel.text = startupIce or '000'

    def Close(self):
        with ExceptionEater('Closing StartupCostCont'):
            self.hubController.on_online_state_changed.disconnect(self.OnOnlineStateChanged)
            self.hubController.on_upgrades_changed.disconnect(self.OnUpgradesChanged)
            self.hubController = None
        super(StartupCostCont, self).Close()
