#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\ProcessorContainer.py
import blue
import localization
import uthread
import utillib
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.effect import UIEffects
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveIcon, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.planet import planetCommon
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import BasePinContainer, CaptionAndSubtext
from eve.common.script.planet.entities import basePin
from fsdBuiltData.common.planet import get_schematic, get_schematic_name

class ProcessorContainer(BasePinContainer):
    default_name = 'ProcessorContainer'
    default_width = 320
    INFO_CONT_HEIGHT = 100
    panelIDs = [planetCommon.PANEL_SCHEMATICS, planetCommon.PANEL_PRODUCTS] + BasePinContainer.panelIDs

    def ApplyAttributes(self, attributes):
        BasePinContainer.ApplyAttributes(self, attributes)
        if not attributes.panelID and self.pin.schematicID is None:
            self.ShowPanel(planetCommon.PANEL_SCHEMATICS)

    def PanelShowSchematics(self):
        self.schematicsCont = Container(parent=self.actionCont, name='schematicsCont', align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        btnGroup = ButtonGroup(parent=self.schematicsCont, line=False)
        self.submitBtn = btnGroup.AddButton(localization.GetByLabel('UI/PI/Common/InstallSchematic'), self.InstallSchematic)
        self.schematicsScroll = eveScroll.Scroll(parent=self.schematicsCont, name='schematicsScroll', align=uiconst.TOALL)
        self.schematicsScroll.Startup()
        self.schematicsScroll.sr.id = 'planetProcessorSchematicsScroll'
        self.schematicsScroll.multiSelect = False
        self.schematicsScroll.OnSelectionChange = self.OnSchematicScrollSelectionChange
        uthread.new(self.LoadSchematicsScroll)
        return self.schematicsCont

    def LoadSchematicsScroll(self):
        scrolllist = []
        for schematic in planetCommon.GetSchematicData(self.pin.typeID):
            typeID = schematic.outputs[0].typeID
            data = utillib.KeyVal(label=planetCommon.GetProductNameAndTier(typeID), schematic=schematic, itemID=None, typeID=typeID, getIcon=True, OnClick=None, OnDblClick=self.InstallSchematic)
            sortBy = (planetCommon.GetTierByTypeID(typeID), schematic.name)
            scrolllist.append((sortBy, GetFromClass(SchematicItem, {'label': planetCommon.GetProductNameAndTier(typeID),
              'schematic': schematic,
              'itemID': None,
              'typeID': typeID,
              'getIcon': True,
              'OnClick': None,
              'OnDblClick': self.InstallSchematic})))

        scrolllist = SortListOfTuples(scrolllist)
        self.schematicsScroll.Load(contentList=scrolllist, headers=[])
        self._InitSelectedNode()
        self.UpdateSubmitBtn()

    def _InitSelectedNode(self):
        for node in self.schematicsScroll.GetNodes():
            if self.GetPersistedSchematicSelected() == node.typeID:
                self.schematicsScroll.SelectNode(node)
                self.schematicsScroll.ScrollToNode(node)

    def OnSchematicScrollSelectionChange(self, entries):
        self.UpdateSubmitBtn()

    def UpdateSubmitBtn(self):
        entries = self.schematicsScroll.GetSelected()
        if entries:
            self.submitBtn.Enable()
        else:
            self.submitBtn.Disable()

    def InstallSchematic(self, *args):
        entries = self.schematicsScroll.GetSelected()
        if not entries:
            return
        entry = entries[0]
        schematicID = entry.schematic.schematicID
        self.planetUISvc.myPinManager.InstallSchematic(self.pin.id, schematicID)
        self.RenderIngredientGauges()
        typeID = entry.schematic.outputs[0].typeID
        self.PersistSchematicSelected(typeID)
        self.ShowPanel(planetCommon.PANEL_CREATEROUTE, typeID, entry.schematic.outputs[0].quantity)

    def PersistSchematicSelected(self, typeID):
        settings.char.ui.Set(self._GetSchematicSettingID(), typeID)

    def GetPersistedSchematicSelected(self):
        if self.pin.schematicID:
            schematic = planetCommon.GetSchematicDataForID(self.pin.schematicID)
            return schematic.outputs[0].typeID
        else:
            return settings.char.ui.Get(self._GetSchematicSettingID(), None)

    def _GetSchematicSettingID(self):
        return 'planetProcessor_%s' % self.pin.typeID

    def _GetInfoCont(self):
        self.currProductTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/Producing'), align=uiconst.TOTOP)
        self.ingredientsTxt = CaptionAndSubtext(parent=self.infoContLeft, state=uiconst.UI_DISABLED, caption=localization.GetByLabel('UI/PI/Common/SchematicInput'), align=uiconst.TOTOP, padding=(0, 2, 0, 2))
        self.ingredientCont = Container(name='ingredientCont', parent=self.infoContLeft, height=42, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP)
        self.RenderIngredientGauges()
        self.currCycleGauge = Gauge(parent=self.infoContRight, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, width=140, align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        self.amountPerCycleTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/OutputPerCycle'), align=uiconst.TOTOP)
        self.amountPerHourTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/OutputPerHour'), align=uiconst.TOTOP)

    def RenderIngredientGauges(self):
        self.ingredientCont.Flush()
        self.ingredientGauges = {}
        i = 0
        colony = sm.GetService('planetUI').planet.GetColony(session.charid)
        for typeID, amount in self.pin.GetConsumables().iteritems():
            hasIncomingRoute = colony.colonyData.HasIncomingRoute(self.pin.id, typeID)
            gauge = ProcessorGaugeContainer(parent=self.ingredientCont, iconTypeID=typeID, maxAmount=amount, align=uiconst.TOLEFT, hasIncomingRoute=hasIncomingRoute, padRight=2)
            self.ingredientGauges[typeID] = gauge
            i += 1

        if not self.pin.GetConsumables():
            self.ingredientsTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/NoSchematicSelected'))
        else:
            self.ingredientsTxt.SetSubtext('')

    def _UpdateInfoCont(self):
        if self.pin.schematicID:
            schematicObj = get_schematic(self.pin.schematicID)
            schematicName = get_schematic_name(self.pin.schematicID, schematicObj)
            for typeID, schematicType in schematicObj.types.iteritems():
                if not schematicType.isInput:
                    outputPerCycle = schematicType.quantity
                    outputTypeID = typeID

            if self.pin.activityState < basePin.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                status = localization.GetByLabel('UI/Common/Inactive')
            elif self.pin.IsActive():
                nextCycle = self.pin.GetNextRunTime()
                if nextCycle is None or nextCycle < blue.os.GetWallclockTime():
                    status = localization.GetByLabel('UI/PI/Common/ProductionCompletionImminent')
                else:
                    status = '<color=green>%s</color>' % localization.GetByLabel('UI/PI/Common/InProduction')
                currCycle = self.pin.GetCycleTime() - (self.pin.GetNextRunTime() - blue.os.GetWallclockTime())
                currCycleProportion = currCycle / float(self.pin.GetCycleTime())
            else:
                status = localization.GetByLabel('UI/PI/Common/WaitingForResources')
                currCycle = 0
                currCycleProportion = 0.0
        else:
            schematicName = localization.GetByLabel('UI/PI/Common/NothingExtracted')
            status = localization.GetByLabel('UI/Common/Inactive')
            currCycleProportion = 0.0
            currCycle = 0
            outputPerCycle = 0
            outputTypeID = None
        for typeID, amountNeeded in self.pin.GetConsumables().iteritems():
            amount = self.pin.GetContents().get(typeID, 0)
            gauge = self.ingredientGauges.get(typeID)
            if not gauge:
                continue
            gauge.SetValue(float(amount) / amountNeeded)
            gauge.hint = localization.GetByLabel('UI/PI/Common/ProductionGaugeHint', resourceName=planetCommon.GetProductNameAndTier(typeID), amount=amount, amountNeeded=amountNeeded)

        errorText = self._GetErrorText()
        if errorText:
            schematicName += '\n' + errorText
        self.currProductTxt.SetSubtext(schematicName)
        if self.pin.schematicID:
            if self.pin.activityState < basePin.STATE_IDLE:
                self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            else:
                self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=long(currCycle), totalTime=self.pin.GetCycleTime()))
        self.currProductTxt.SetIcon(outputTypeID)
        self.currCycleGauge.SetValueInstantly(currCycleProportion)
        self.currCycleGauge.SetText(status)
        self.amountPerCycleTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=outputPerCycle))
        self.amountPerHourTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=self.pin.GetOutputVolumePerHour()))

    def _GetErrorText(self):
        errorText = ''
        if self.IsSomeConsumableUnfulfilled():
            errorText = localization.GetByLabel('UI/PI/Common/InputRoutesMissing')
        elif self.IsSomeProductUnrouted():
            errorText = localization.GetByLabel('UI/PI/Common/NotRouted')
        if errorText:
            errorText = '<color=red>%s</color>' % errorText
        return errorText


class ProcessorGaugeContainer(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_name = 'ProcessorGauge'
    default_left = 0
    default_top = 0
    default_width = 32
    default_height = 42

    def ApplyAttributes(self, attributes):
        self.uiEffects = UIEffects()
        Container.ApplyAttributes(self, attributes)
        self.value = attributes.Get('value', 0.0)
        self.left = attributes.Get('left', 0)
        self.top = attributes.Get('top', 0)
        self.typeID = iconTypeID = attributes.Get('iconTypeID', 6)
        hasIncomingRoute = attributes.hasIncomingRoute
        color = planetCommon.PLANET_COLOR_USED_PROCESSOR
        self.icon = eveIcon.Icon(parent=self, pos=(2, 2, 28, 28), state=uiconst.UI_DISABLED, typeID=iconTypeID, size=16, ignoreSize=True)
        gaugeCont = Container(parent=self, pos=(0,
         0,
         self.width,
         self.width), align=uiconst.TOPLEFT)
        self.gauge = Fill(parent=gaugeCont, align=uiconst.TOLEFT, width=0, color=color, state=uiconst.UI_DISABLED)
        self.bgFill = Fill(parent=gaugeCont, state=uiconst.UI_DISABLED)
        if hasIncomingRoute:
            self.bgFill.color = (255 / 255.0,
             128 / 255.0,
             0 / 255.0,
             0.15)
        else:
            self.bgFill.color = planetCommon.PLANET_COLOR_NEEDSATTENTION
            self.bgFill.opacity = 0.3
        self.busy = False
        self.SetValue(self.value)

    def SetValue(self, value, frequency = 8.0):
        if self.busy or value == self.value:
            return
        if value > 1.0:
            value = 1.0
        uthread.new(self._SetValue, value, frequency)

    def _SetValue(self, value, frequency):
        if not self or self.destroyed:
            return
        self.busy = True
        self.value = value
        self.uiEffects.MorphUIMassSpringDamper(self.gauge, 'width', int(self.width * value), newthread=0, float=0, dampRatio=0.6, frequency=frequency, minVal=0, maxVal=self.width, maxTime=1.0)
        if not self or self.destroyed:
            return
        self.busy = False

    def GetMenu(self):
        ret = sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)
        if session.role & ROLE_GML == ROLE_GML:
            ret.append(('GM / WM Extras', self.GetGMMenu()))
        return ret

    def GetGMMenu(self):
        return [('Add commodity to pin', self.AddCommodity, [])]

    def AddCommodity(self):
        pinID = sm.GetService('planetUI').currentContainer.pin.id
        sm.GetService('planetUI').planet.GMAddCommodity(pinID, self.typeID)


class SchematicItem(Item):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        schematicID = planetCommon.GetSchematicByOutput(self.sr.node.typeID)
        schematic = planetCommon.GetSchematicDataForID(schematicID)
        planetCommon.LoadSchematicTooltipPanel(tooltipPanel, schematic)
