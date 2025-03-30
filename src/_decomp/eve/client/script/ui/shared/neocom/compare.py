#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\compare.py
from collections import OrderedDict
import eveformat
import telemetry
import carbonui.const as uiconst
import dogma.data as dogma_data
import evetypes
import inventorycommon
import localization
import metaGroups
from carbonui.control.checkbox import Checkbox
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.services.setting import UserSettingBool
from dogma.attributes.format import FormatUnit, GetFormatAndValue
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.label_text import LabelTextTop
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.info.infoUtil import GetFittingAttributeIDs
from eve.common.script.util import eveFormat
from eveservices.menu import GetMenuService
from inventorycommon.const import compareCategories
from inventorycommon.typeHelpers import GetAveragePrice
from localization import GetByLabel
from utillib import KeyVal
LEFT_PANEL_MIN_WIDTH = 160
LEFT_PANEL_MAX_WIDTH = 280
allowedGuids = ['xtriui.InvItem',
 'xtriui.FittingSlot',
 'listentry.InvItem',
 'listentry.GenericMarketItem',
 'listentry.QuickbarItem',
 'listentry.InvAssetItem',
 'xtriui.ShipUIModule',
 'uicls.GenericDraggableForTypeID',
 'listentry.Item',
 'listentry.KillItems',
 'listentry.FittingModuleEntry']
EST_PRICE_CONFIG = 'compare_estPriceChecked'
only_show_diffrentiators = UserSettingBool('compare_onlyShowDifferent', False)

class TypeData(object):

    def __init__(self, typeID, itemID = None, godmaAttributes = None):
        if godmaAttributes is not None:
            self.godmaAttributes = godmaAttributes
        else:
            self.godmaAttributes = {}
            dynamicItemSvc = sm.GetService('dynamicItemSvc')
            if dynamicItemSvc.IsDynamicItem(typeID):
                for attributeID, value in dynamicItemSvc.GetDynamicItemAttributes(itemID).iteritems():
                    self.godmaAttributes[attributeID] = value

            else:
                for attribute in sm.GetService('godma').GetType(typeID).displayAttributes:
                    self.godmaAttributes[attribute.attributeID] = attribute.value

        self.typeID = typeID
        self.itemID = itemID

    def GetAttributeValue(self, attributeID):
        return self.godmaAttributes.get(attributeID, None)


class TypeCompare(Window):
    default_windowID = 'typecompare'
    default_iconNum = 'res:/ui/Texture/WindowIcons/comparetool.png'
    default_captionLabelPath = 'Tooltips/Neocom/CompareTool'
    default_descriptionLabelPath = 'Tooltips/Neocom/CompareTool_description'
    default_minSize = (350, 400)
    default_width = 600
    default_height = 500

    def ApplyAttributes(self, attributes):
        super(TypeCompare, self).ApplyAttributes(attributes)
        typeID = attributes.typeID
        self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.types = []
        self.attributeIDsUserSelectable = []
        self.attributesCombined = []
        self.attributeIDsCurrentlyChecked = []
        self.activeAttributesChecked = set()
        self.banAttrs = sm.GetService('info').GetSkillAttrs()
        self.attributeLimit = 10
        self.typeLimit = 40
        self.settingsinited = 0
        self.graphinited = 0
        self.topLevelMarketGroup = None
        self.ConstructLayout()
        if typeID:
            typeIDs = evetypes.GetVariations(typeID)
            for _typeID in typeIDs:
                if not evetypes.IsDynamicType(_typeID):
                    self.AddTypeID(_typeID)

        only_show_diffrentiators.on_change.connect(self.OnOnlyShowDiffrentiatorsSetting)

    def ConstructLayout(self):
        self.mainCont = Container(name='mainCont', parent=self.sr.main)
        self.ConstructAttributeScroll()
        self.ConstructTypeScroll()
        self.ConstructButtonGroup()

    def ConstructButtonGroup(self):
        btns = ((localization.GetByLabel('UI/Commands/UncheckAll'),
          self.SelectAll,
          (0,),
          None), (localization.GetByLabel('UI/Commands/ResetAll'),
          self.RemoveAllEntries,
          (),
          None))
        ButtonGroup(btns=btns, parent=self.sr.main, padTop=8, idx=0, button_size_mode=ButtonSizeMode.DYNAMIC)

    def ConstructAttributeScroll(self):
        self.leftCont = DragResizeCont(parent=self.mainCont, align=uiconst.TOLEFT, state=uiconst.UI_HIDDEN, settingsID='compare_DragResizeCont', minSize=LEFT_PANEL_MIN_WIDTH, defaultSize=200, maxSize=LEFT_PANEL_MAX_WIDTH)
        self.attributeScroll = eveScroll.Scroll(name='attributescroll', parent=self.leftCont, padding=(0,
         20,
         0,
         const.defaultPadding))
        self.attributeScroll.sr.id = 'typecompare_attributescroll'
        self.attributeScroll.hiliteSorted = 0
        self.attributeScroll.ShowHint(localization.GetByLabel('UI/Compare/NothingToCompare'))

    def ConstructTypeScroll(self):
        self.typeScroll = eveScroll.Scroll(name='typescroll', parent=self.mainCont, padTop=const.defaultPadding)
        self.typeScroll.ShowHint(localization.GetByLabel('UI/Compare/CompareToolHint'))
        self.typeScroll.sr.id = 'typecompare_typescroll'
        self.typeScroll.sr.content.OnDropData = self.OnDropData

    def SettingMenu(self, menuParent):
        onlyShowDifferent = only_show_diffrentiators.is_enabled()
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Compare/OnlyShowDifferent'), checked=onlyShowDifferent, callback=only_show_diffrentiators.toggle)

    def GetMenuMoreOptions(self):
        menuData = super(TypeCompare, self).GetMenuMoreOptions()
        menuData.AddCheckbox(text=GetByLabel('UI/Compare/OnlyShowDifferent'), setting=only_show_diffrentiators)
        return menuData

    def OnOnlyShowDiffrentiatorsSetting(self, value):
        self.ReloadAttributeScroll()
        self.ReloadTypeCompareScroll()

    def RemoveAllEntries(self, *args):
        self.types = []
        self.topLevelMarketGroup = None
        self.SelectAll()

    def SelectAll(self, onOff = 0):
        if onOff:
            return
        self.attributeIDsCurrentlyChecked = []
        self.activeAttributesChecked.clear()
        self.OnColumnChanged()

    def AddTypeID(self, typeID, itemID = None):
        currTypeIDs = [ node.typeID for node in self.types ]
        if typeID in currTypeIDs:
            return
        if not self._IsValidTopLevelMarketGroupID(typeID, itemID):
            eve.Message('CannotCompareNoneItem')
            return
        categoryID = evetypes.GetCategoryID(typeID)
        if categoryID not in compareCategories:
            ShowQuickMessage(localization.GetByLabel('UI/Compare/CannotCompareThisItem', typeID=typeID))
            return
        typeData = TypeData(typeID, itemID)
        if typeData not in self.types:
            self.types.append(typeData)
            self.OnColumnChanged()
            if only_show_diffrentiators.is_enabled():
                self.ReloadAttributeScroll()

    def AddVariantsOf(self, typeID):
        typeIDs = evetypes.GetVariations(typeID)
        for _typeID in typeIDs:
            self.AddTypeID(_typeID)

    def _IsValidTopLevelMarketGroupID(self, typeID, itemID):
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        if dynamicItemSvc.IsDynamicItem(typeID):
            mutatedItem = sm.GetService('dynamicItemSvc').GetDynamicItem(itemID)
            topLevelMarketGroupID = self.GetTopLevelMarketGroupID(mutatedItem.sourceTypeID)
        else:
            topLevelMarketGroupID = self.GetTopLevelMarketGroupID(typeID)
        return topLevelMarketGroupID != -1

    def RemoveEntry(self, node):
        nodes = self.typeScroll.GetSelected() or [node]
        toRemove = [ node.typeID for node in nodes ]
        self.types = [ typeData for typeData in self.types if typeData.typeID not in toRemove ]
        if not self.types:
            self.attributeIDsCurrentlyChecked = []
            self.activeAttributesChecked.clear()
            self.topLevelMarketGroup = None
        self.OnColumnChanged()

    def OnColumnChanged(self, force = 1, *args):
        self.attributesCombined = self.GetCombinedDogmaAttributes()
        if force:
            self.ReloadAttributeScroll()
        self.ReloadTypeCompareScroll()

    def GetTopLevelMarketGroupID(self, typeID):
        marketGroupIDFromType = None
        marketGroupID = evetypes.GetMarketGroupID(typeID)
        if marketGroupID is None:
            parentID = evetypes.GetParentIDOfVariations(typeID)
            if parentID is not None:
                marketGroupIDFromType = evetypes.GetMarketGroupID(parentID)
                topLevelMarketGroupID = self.GetTopLevelMarketGroupIDEx(marketGroupIDFromType)
            else:
                return -1
        else:
            topLevelMarketGroupID = self.GetTopLevelMarketGroupIDEx(marketGroupID)
        if not self.topLevelMarketGroup:
            if marketGroupIDFromType:
                self.topLevelMarketGroup = self.GetTopLevelMarketGroupIDEx(marketGroupIDFromType)
            else:
                self.topLevelMarketGroup = self.GetTopLevelMarketGroupIDEx(marketGroupID)
        return topLevelMarketGroupID

    def GetTopLevelMarketGroupIDEx(self, marketGroupID):
        mg = sm.GetService('marketutils').GetMarketGroup(marketGroupID)
        if mg and hasattr(mg, 'parentGroupID'):
            parentGroupID = mg.parentGroupID
            while parentGroupID:
                mg = sm.GetService('marketutils').GetMarketGroup(parentGroupID)
                parentGroupID = mg.parentGroupID

            return mg.marketGroupID
        else:
            return None

    def GetCombinedDogmaAttributes(self):
        attributeIDs = []
        attributes = []
        for typeData in self.types:
            dynamicItemSvc = sm.GetService('dynamicItemSvc')
            if dynamicItemSvc.IsDynamicItem(typeData.typeID):
                item = dynamicItemSvc.GetDynamicItem(typeData.itemID)
                attributeDict = sm.GetService('info').GetAttributeDictForType(item.sourceTypeID)
            else:
                attributeDict = sm.GetService('info').GetAttributeDictForType(typeData.typeID)
            for attributeID, value in attributeDict.iteritems():
                if attributeID not in self.banAttrs and attributeID not in attributeIDs:
                    attributeIDs.append(attributeID)
                    dgmAttribs = dogma_data.get_attribute(attributeID)
                    if dgmAttribs.published or dgmAttribs.attributeID in (const.attributeHp, const.attributeBaseWarpSpeed):
                        attributes.append(dgmAttribs)

        attributesToRemove = []
        for attribute in attributes:
            removeIt = True
            for typeData in self.types:
                value = typeData.GetAttributeValue(attribute.attributeID)
                if value:
                    removeIt = False
                    break

            if removeIt:
                attributesToRemove.append(attribute)

        return attributes

    def ReloadAttributeScroll(self):
        scrolllist = self.GetAttributeScrollList()
        self.attributeScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Compare/NothingToCompare'))

    def GetAttributeScrollList(self):
        attributes = self.GetAttributesToOffer()
        attributeIDs = {x.attributeID for x in attributes}
        self.attributeIDsUserSelectable = []
        categoryID = evetypes.GetCategoryID(self.types[0].typeID) if self.types else None
        if categoryID in (const.categoryShip, const.categoryDrone):
            scrolllist = self._GetScrollListShipOrDrone(attributes, attributeIDs, categoryID)
        else:
            scrolllist = []
            for attribute in attributes:
                self._AppendScrollEntry(attribute, scrolllist)

        if scrolllist and self.ShouldShowEstPriceCheckbox():
            estPriceEntry = self.GetEstPriceEntry()
            scrolllist.insert(0, estPriceEntry)
        return scrolllist

    def _GetScrollListShipOrDrone(self, attributes, attributeIDs, categoryID):
        scrolllist = []
        attrAndFittings = OrderedDict()
        attrAndFittings.update(sm.GetService('info').GetShipAndDroneAttributes())
        attrAndFittings.update(self.GetFittings())
        for caption, attrs in attrAndFittings.iteritems():
            normalAttributes = attrs['normalAttributes']
            groupedAttributes = [ x[1] for x in attrs.get('groupedAttributes', []) ]
            allAttributes = normalAttributes + groupedAttributes
            shipAttr = [ attribute for attribute in attributes if attribute.attributeID in allAttributes ]
            if shipAttr:
                scrolllist.append(GetFromClass(Header, {'label': caption}))
                for attribute in shipAttr:
                    self._AppendScrollEntry(attribute, scrolllist)

                if categoryID == const.categoryShip and caption == localization.GetByLabel('UI/Compare/Propulsion'):
                    if const.attributeBaseWarpSpeed in attributeIDs:
                        attribute = dogma_data.get_attribute(const.attributeBaseWarpSpeed)
                        self._AppendScrollEntry(attribute, scrolllist)

        if categoryID == const.categoryDrone:
            otherAttributes = [ x for x in attributes if x.attributeID not in self.attributeIDsUserSelectable ]
            if otherAttributes:
                scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/InfoWindow/Miscellaneous')}))
                for attribute in otherAttributes:
                    self._AppendScrollEntry(attribute, scrolllist)

        return scrolllist

    def _AppendScrollEntry(self, attribute, scrolllist):
        displayName = dogma_data.get_attribute_display_name(attribute.attributeID)
        if displayName:
            scrolllist.append(self.GetScrollEntry(attribute))
            self.attributeIDsUserSelectable.append(attribute.attributeID)

    @telemetry.ZONE_METHOD
    def GetAttributesToOffer(self):
        if not only_show_diffrentiators.is_enabled() or len(self.types) < 2:
            return self.attributesCombined
        else:
            return self._GetAttributesThatDiffrentiate()

    def _GetAttributesThatDiffrentiate(self):
        allAvailableAttributesByID = OrderedDict()
        for attribute in self.attributesCombined:
            allAvailableAttributesByID[attribute.attributeID] = attribute

        differentAttributesDict = OrderedDict()
        for eachAttributeID, attribute in allAvailableAttributesByID.iteritems():
            attributeValues = []
            for typeData in self.types:
                if eachAttributeID == const.attributeBaseWarpSpeed:
                    value = self.GetWarpValue(typeData)
                else:
                    value = typeData.GetAttributeValue(attribute.attributeID)
                if attributeValues and value not in attributeValues:
                    differentAttributesDict[eachAttributeID] = attribute
                    break
                else:
                    attributeValues.append(value)

        attributes = differentAttributesDict.values()
        return attributes

    def ShouldShowEstPriceCheckbox(self):
        if not only_show_diffrentiators.is_enabled():
            return True
        if len(self.types) < 2:
            return True
        estPriceSet = set()
        for typeData in self.types:
            estPriceSet.add(GetAveragePrice(typeData.typeID))

        return len(estPriceSet) > 1

    def GetFittings(self):
        fittingDict = {localization.GetByLabel('UI/Fitting/FittingWindow/Fitting'): {'normalAttributes': GetFittingAttributeIDs()}}
        return fittingDict

    def GetScrollEntry(self, entry):
        displayName = dogma_data.get_attribute_display_name(entry.attributeID)
        return GetFromClass(AttributeCheckbox, {'line': 1,
         'info': entry,
         'label': displayName,
         'iconID': getattr(entry, 'iconID', None),
         'item': entry,
         'text': FormatUnit(getattr(entry, 'unitID', None)) or ' ',
         'hint': displayName,
         'checked': entry.attributeID in self.attributeIDsCurrentlyChecked,
         'cfgname': entry.attributeID,
         'OnChange': self.OnAttributeSelectedChanged})

    def OnAttributeSelectedChanged(self, checkbox, *args):
        attributeID = checkbox.GetSettingsKey()
        if checkbox.GetValue():
            if len(self.activeAttributesChecked) < self.attributeLimit:
                if attributeID not in self.attributeIDsCurrentlyChecked:
                    self.attributeIDsCurrentlyChecked.append(attributeID)
                self.OnColumnChanged(force=0)
            else:
                checkbox.SetValue(False)
                message = localization.GetByLabel('UI/Compare/CanOnlyCompareAmountAttributes', amount=self.attributeLimit)
                eve.Message('CustomInfo', {'info': message})
        else:
            if attributeID in self.attributeIDsCurrentlyChecked:
                self.attributeIDsCurrentlyChecked.remove(attributeID)
            self.OnColumnChanged(force=0)

    def GetEstPriceEntry(self):
        return GetFromClass(SingleLineCheckbox, {'line': 1,
         'label': localization.GetByLabel('UI/Contracts/ContractsWindow/EstPrice'),
         'checked': settings.user.ui.Get(EST_PRICE_CONFIG, True),
         'OnChange': self.OnEstPriceSelectedChanged})

    def OnEstPriceSelectedChanged(self, checkbox, *args):
        settings.user.ui.Set(EST_PRICE_CONFIG, checkbox.GetValue())
        self.OnColumnChanged(force=0)

    def ReloadTypeCompareScroll(self):
        scrolllist, headers = self.GetCompareTypeInfoContentList()
        self.leftCont.display = bool(scrolllist)
        self.typeScroll.Load(contentList=scrolllist, headers=headers, noContentHint=localization.GetByLabel('UI/Compare/CompareToolHint'))

    def GetCompareTypeInfoContentList(self):
        scrolllist = []
        headers, uniqueHeaders, treatedHeaders, initialHeaders = ([],
         [],
         [],
         [])
        estPriceChecked = settings.user.ui.Get(EST_PRICE_CONFIG, True)
        estPriceHeaderText = localization.GetByLabel('UI/Contracts/ContractsWindow/EstPrice') if estPriceChecked else ''
        if self.types:
            headers = [localization.GetByLabel('/Carbon/UI/Common/TypeName'), localization.GetByLabel('UI/Compare/MetaGroup')]
            attrDictToUse = self.GetAttributesToOffer()
            self.activeAttributesChecked.clear()
            for typeData in self.types:
                data = KeyVal(typeID=typeData.typeID, itemID=typeData.itemID, godmaAttributes=typeData.godmaAttributes)
                typeName = evetypes.GetName(typeData.typeID)
                metaGroupID = evetypes.GetMetaGroupIDOrNone(typeData.typeID)
                text = '%s<t>%s' % (typeName, metaGroups.get_name(metaGroupID))
                data.Set('sort_%s' % headers[0], typeName)
                data.Set('sort_%s' % headers[1], metaGroupID)
                if estPriceChecked:
                    estPriceHeader = (estPriceHeaderText, -1)
                    if estPriceHeader not in uniqueHeaders:
                        uniqueHeaders.append(estPriceHeader)
                    estPrice = inventorycommon.typeHelpers.GetAveragePrice(typeData.typeID)
                    if estPrice is not None:
                        formattedIsk = eveFormat.FmtISK(estPrice, showFractionsAlways=1)
                        text += '<t><right>%s' % formattedIsk
                        data.Set('sort_%s' % estPriceHeaderText, estPrice)
                    else:
                        text += '<t>'
                        data.Set('sort_%s' % estPriceHeaderText, None)
                attributeLoop = {}
                for each in attrDictToUse:
                    if each.attributeID in self.attributeIDsCurrentlyChecked:
                        self.activeAttributesChecked.add(each.attributeID)
                        attributeLoop[each.attributeID] = each

                for each in self.attributeIDsUserSelectable:
                    attribute = attributeLoop.get(each, None)
                    if not attribute:
                        continue
                    displayNameRaw = dogma_data.get_attribute_display_name(attribute.attributeID)
                    displayName = eveformat.replace_text_ignoring_tags(displayNameRaw, old=' ', new='<br>')
                    if (displayName, attribute.attributeID) not in uniqueHeaders:
                        uniqueHeaders.append((displayName, attribute.attributeID))
                    if attribute.attributeID == const.attributeBaseWarpSpeed:
                        value = self.GetWarpValue(typeData)
                    else:
                        value = typeData.GetAttributeValue(attribute.attributeID)
                    if evetypes.GetCategoryID(typeData.typeID) == const.categoryCharge:
                        bsd, bad = sm.GetService('info').GetBaseDamageValue(typeData.typeID)
                        if displayNameRaw == localization.GetByLabel('UI/Compare/BaseShieldDamage'):
                            if bsd:
                                value = bsd[0]
                        elif displayNameRaw == localization.GetByLabel('UI/Compare/BaseArmorDamage'):
                            if bad:
                                value = bad[0]
                    data.Set('sort_%s' % displayName, value)
                    if value is None:
                        taa = localization.GetByLabel('UI/Generic/NotAvailableShort')
                    else:
                        taa = GetFormatAndValue(attribute, value)
                    text += '<t>%s' % taa

                data.label = text
                data.getIcon = 1
                data.GetMenu = self.GetEntryMenu
                data.viewMode = 'details'
                data.ignoreRightClick = 1
                data.OnDropData = self.OnDropData
                scrolllist.append(GetFromClass(Item, data))

            for header, attributeID in uniqueHeaders:
                if header in headers:
                    header = header + ' '
                headers.append(header)

            initialHeaders = headers
            treatedHeaders = []
            for each in initialHeaders:
                treatedHeaders.append(each.replace(' ', '<br>'))

        return (scrolllist, initialHeaders)

    def GetWarpValue(self, typeData):
        godma = sm.GetService('godma')
        cmp = max(godma.GetTypeAttribute(typeData.typeID, const.attributeBaseWarpSpeed, defaultValue=1), 1.0)
        cmp *= godma.GetTypeAttribute(typeData.typeID, const.attributeWarpSpeedMultiplier, defaultValue=1)
        cmp *= const.AU
        return cmp

    def GetEntryMenu(self, item):
        m = GetMenuService().GetMenuFromItemIDTypeID(None, item.typeID, includeMarketDetails=True).filter(['UI/Compare/CompareButton'])
        item.DoSelectNode()
        sel = self.typeScroll.GetSelected()
        text = localization.GetByLabel('UI/Commands/Remove')
        if len(sel) > 1:
            text = localization.GetByLabel('UI/Commands/RemoveMultiple', itemcount=len(sel))
        m += [(text, self.RemoveEntry, (item,))]
        return m

    def OnDropData(self, dragObj, nodes):
        for node in nodes:
            if getattr(node, '__guid__', None) in allowedGuids:
                typeID = self._GetNodeTypeID(node)
                if typeID:
                    if not sm.GetService('info').GetAttributeDictForType(typeID):
                        ShowQuickMessage(localization.GetByLabel('UI/Compare/CannotCompareThisItem', typeID=typeID))
                        return
                    if not hasattr(node, 'itemID'):
                        node.itemID = None
                    self.AddTypeID(typeID, node.itemID)

    def _GetNodeTypeID(self, node):
        invType = node.get('invtype')
        if invType:
            return invType
        typeID = node.get('typeID')
        if typeID:
            return typeID


class SingleLineCheckbox(CheckboxEntry):

    def Load(self, args):
        CheckboxEntry.Load(self, args)
        self.sr.checkbox.left = 4


class AttributeCheckbox(LabelTextTop):
    __guid__ = 'listentry.AttributeCheckbox'

    def Startup(self, *args):
        LabelTextTop.Startup(self, args)
        self.sr.checkbox = Checkbox(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, callback=self.CheckBoxChange, pos=(4, 4, 0, 0))

    def Load(self, args):
        LabelTextTop.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.SetSettingsKey(data.cfgname)
        self.sr.icon.left = 20
        if self.sr.icon.display:
            self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 2
            self.sr.text.left = self.sr.icon.left + self.sr.icon.width + 2
        else:
            self.sr.label.left = 24
            self.sr.text.left = 24

    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)

    def OnClick(self, *args):
        self.sr.checkbox.OnClick(*args)
