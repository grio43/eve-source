#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\deployment\stargateSystemEntry.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.util.stringManip import GetAsUnicode
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.stateFlag import FlagIconWithState
from localization import GetByLabel
from menu import MenuLabel

class StargateDestSystemsEntry(BaseListEntryCustomColumns):
    default_name = 'StructureEntryMyCorp'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.BuildUI()

    def BuildUI(self):
        self.nameLabel = self.AddColumnText()
        distCont = self.AddColumnContainer()
        self.distLabel = EveLabelMedium(parent=distCont, name='distLabel', align=uiconst.CENTERRIGHT, left=10)
        jumpCont = self.AddColumnContainer()
        self.jumpLabel = EveLabelMedium(parent=jumpCont, name='jumpLabel', align=uiconst.CENTERRIGHT, left=10)
        self.corpCont = self.AddColumnContainer()
        self.corpFlag = FlagIconWithState(parent=self.corpCont, left=4, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.structureLabel = EveLabelMedium(parent=self.corpCont, name='jumpLabel', align=uiconst.CENTERLEFT, left=20, state=uiconst.UI_NORMAL)
        self.linkLabel = self.AddColumnText()
        self.LoadUI()

    def LoadUI(self):
        node = self.node
        jumpGate = node.jumpGate
        alignedToCurrentSystem = jumpGate and jumpGate.alignedToCurrentSystem
        self.nameLabel.text = node.systemName
        self.distLabel.text = node.distText
        self.jumpLabel.text = node.jumpText
        self.corpFlag.display = False
        if jumpGate:
            if node.corpFlagInfo:
                self.corpFlag.ModifyIcon(node.corpFlagInfo)
                self.corpFlag.hint = node.corpFlagInfo.flagProperties.ownerText
                self.corpFlag.display = True
            if alignedToCurrentSystem:
                linkColor = (0, 1, 0, 0.75)
            else:
                linkColor = (1, 0, 0, 0.75)
            structureText = GetShowInfoLink(jumpGate.typeID, jumpGate.structureName, jumpGate.structureID)
            labelState = uiconst.UI_NORMAL
        else:
            structureText = GetByLabel('UI/Structures/Deployment/NoGate')
            labelState = uiconst.UI_DISABLED
            linkColor = (1, 1, 1, 0.75)
        self.structureLabel.text = structureText
        self.structureLabel.state = labelState
        self.linkLabel.text = self.GetLinkText(node)
        self.linkLabel.SetRGBA(*linkColor)

    def GetMenu(self):
        node = self.node
        m = [(MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (const.typeSolarSystem, node.solarSystemID))]
        if node.hasGate:
            m = [(MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (const.typeSolarSystem, node.solarSystemID))]
        return m

    @staticmethod
    def GetHeaders():
        return [GetByLabel('UI/Common/LocationTypes/System'),
         GetByLabel('UI/Common/Distance'),
         GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Structures/Deployment/StargateHeader'),
         GetByLabel('UI/Structures/Deployment/LinkHeader')]

    @staticmethod
    def GetLinkText(node):
        if not node.jumpGate:
            return GetByLabel('UI/Structures/Deployment/GateLinkUnavailable')
        if node.jumpGate.alignedToCurrentSystem:
            return GetByLabel('UI/Structures/Deployment/GateLinkAvailable')
        return GetByLabel('UI/Structures/Deployment/GateLinkElsewhere')

    @staticmethod
    def GetDynamicHeight(node, width):
        return 20

    @staticmethod
    def GetStringFromNode(node):
        structureName = node.jumpGate.structureName if node.jumpGate else GetByLabel('UI/Structures/Deployment/NoGate')
        textList = [node.systemName,
         node.distText,
         node.jumpText,
         '      ' + structureName,
         StargateDestSystemsEntry.GetLinkText(node)]
        text = '<t>'.join(textList)
        return GetAsUnicode(text)
