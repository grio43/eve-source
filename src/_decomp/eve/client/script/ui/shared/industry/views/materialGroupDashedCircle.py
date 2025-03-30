#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\views\materialGroupDashedCircle.py
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML
import carbonui.const as uiconst
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.views.dashedCircle import DashedCircle
from eve.client.script.ui.shared.industry.views.industryTooltips import MaterialGroupTooltipPanel
from localization import GetByLabel
from menu.menuLabel import MenuLabel
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty

class MaterialGroupDashedCircle(DashedCircle):

    def ApplyAttributes(self, attributes):
        DashedCircle.ApplyAttributes(self, attributes)
        self.materialsByGroupID = attributes.materialsByGroupID
        self.jobData = attributes.jobData

    def UpdateMaterialsByGroup(self, materialsByGroupID):
        self.materialsByGroupID = materialsByGroupID

    def LoadTooltipPanel(self, tooltipPanel, *args):
        self.tooltipPanel = MaterialGroupTooltipPanel(materialsByGroupID=self.materialsByGroupID, tooltipPanel=tooltipPanel, jobData=self.jobData)

    def GetMenu(self):
        menu = []
        menu.append(MenuEntryData(text=MenuLabel('UI/Market/MarketQuote/BuyAll'), func=self.BuyAllMaterial, internalName='BuyAllMaterial'))
        menu.append(MenuEntryData(text=MenuLabel('UI/Industry/BuyMissingMaterials'), func=self.BuyMultipleTypesMissing, internalName='BuyMultipleTypesMissing'))
        menu.append(MenuEntryData(text=MenuLabel('UI/Industry/CopyMaterialInformation'), func=self.CopyToClipboard, internalName='CopyToClipboard'))
        if session.role & ROLE_GML == ROLE_GML:
            menu += [None]
            menu.append(MenuEntryData(text='GM: Give me these materials', func=self.DoCreateMaterials))
        return menu

    def BuyAllMaterial(self, *args):
        return self.BuyMaterial(qtyAttr='quantity')

    def BuyMultipleTypesMissing(self, *args):
        return self.BuyMaterial(qtyAttr='missing')

    def BuyMaterial(self, qtyAttr = 'quantity'):
        buyDict = self._GetMaterialDict(qtyAttr)
        BuyMultipleTypesWithQty(buyDict)

    def _GetMaterialDict(self, qtyAttr):
        buyDict = {}
        for materialGroupID, materials in self.materialsByGroupID:
            for material in materials:
                if material.typeID is None:
                    continue
                qty = getattr(material, qtyAttr)
                if qty:
                    buyDict[material.typeID] = qty

        return buyDict

    def CopyToClipboard(self):
        dataList = [self.AddRow(self.jobData.blueprint.GetName(), self.jobData.blueprint.typeID), '']
        for materialGroupID, materials in self.materialsByGroupID:
            groupName = GetByLabel(industryUIConst.LABEL_BY_INDUSTRYGROUP[materialGroupID])
            dataList.append(self.AddRow('%s' % groupName))
            dataList.append(self.AddRow('Item', 'Required', 'Available', 'Est. Unit price', 'typeID'))
            for material in materials:
                if material.typeID is None:
                    dataList.append(self.AddRow('No item selected'))
                else:
                    dataList.append(self.AddRow(material.GetName(), material.quantity, material.available, material.GetEstimatedUnitPrice(), material.typeID))

            dataList.append('')

        data = '\n'.join(dataList)
        blue.clipboard.SetClipboardData(data)

    def DoCreateMaterials(self):
        materialDict = self._GetMaterialDict(qtyAttr='quantity')
        items = [ (typeID, qty) for typeID, qty in materialDict.iteritems() ]
        sm.GetService('info').DoCreateMaterials(commands=items, qty=1)

    def AddRow(self, col1 = '', col2 = '', col3 = '', col4 = '', col5 = ''):
        return '%s\t%s\t%s\t%s\t%s' % (col1,
         col2,
         col3,
         col4,
         col5)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
