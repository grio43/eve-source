#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\accessGroups\groupInfoWnd.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium, WndCaptionLabel
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.common.script.sys.idCheckers import IsNPCCorporation
from localization import GetByLabel
import carbonui.const as uiconst
from utillib import KeyVal

class GroupInfoWnd(Window):
    default_minSize = (200, 130)
    default_width = 300
    default_iconNum = 'res:/UI/Texture/WindowIcons/accessGroups.png'
    default_captionLabelPath = 'UI/Structures/AccessGroups/AccessGroup'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        mainIcon = SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_NORMAL, pos=(0, -8, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        mainIcon.GetDragData = self.GetDragDataForIcon
        mainIcon.isDragObject = True
        self.groupID = attributes.groupID
        self.groupInfo = GetGroupInfo(self.groupID)
        isNPCCorpGroup = IsNPCCorporation(self.groupInfo.creatorID)
        self.groupName = self.groupInfo['name']
        groupDisplayName = cfg.eveowners.Get(self.groupInfo.creatorID).name if isNPCCorpGroup else self.groupName
        WndCaptionLabel(text=groupDisplayName, parent=self.topParent)
        scrollContainer = ScrollContainer(parent=self.sr.main, padding=(10, 0, 10, 10))
        self.contentCont = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, columns=1)
        self.LoadContentCont()
        w, h = self.contentCont.GetAbsoluteSize()
        newHeight = h + self.topParent.height + 40
        self.height = newHeight

    def LoadContentCont(self):
        self.contentCont.Flush()
        groupDesc = self.groupInfo['description']
        admins = self.groupInfo['admins']
        if groupDesc:
            EveLabelMedium(parent=self.contentCont, text=groupDesc, padTop=6, align=uiconst.TOTOP)
        else:
            descText = GetByLabel('UI/Structures/AccessGroups/NoGroupDescription')
            EveLabelMedium(parent=self.contentCont, text=descText, align=uiconst.TOTOP, padTop=6, italic=True)
        for adminID in admins:
            ownerInfo = cfg.eveowners.Get(adminID)
            charName = ownerInfo.name
            charText = GetShowInfoLink(ownerInfo.typeID, charName, itemID=adminID)
            text = GetByLabel('UI/Structures/AccessGroups/GroupOwner', ownerName=charText)
            EveLabelMedium(parent=self.contentCont, text=text, align=uiconst.TOTOP, padTop=6, state=uiconst.UI_NORMAL)

    def GetDragDataForIcon(self):
        ret = KeyVal(nodeType='AccessGroupEntry', groupID=self.groupID, label=self.groupName)
        return [ret]


def GetGroupInfo(groupID):
    accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
    groupInfo = accessGroupsController.GetGroupInfoFromID(groupID, fetchToServer=True)
    return groupInfo
