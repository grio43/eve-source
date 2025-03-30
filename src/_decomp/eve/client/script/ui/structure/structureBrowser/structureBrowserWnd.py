#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\structureBrowserWnd.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import WndCaptionLabel
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.structure.structureBrowser.browserMyCorpStructures import BrowserMyCorpStructures
from eve.client.script.ui.structure.structureBrowser.browserAllStructures import BrowserAllStructures
from eve.common.lib import appConst
from eve.client.script.ui.structure.structureBrowser.browserSkyhooks import BrowserAllSkyhooks
from eve.common.script.sys import idCheckers
from localization import GetByLabel
import carbonui.const as uiconst

class StructureBrowserWnd(Window):
    default_captionLabelPath = 'UI/Structures/Browser/StructureBrowser'
    descriptionLabelPath = 'UI/Structures/Browser/StructureBrowserDescription'
    default_name = 'Structure Browser'
    default_windowID = 'StructureBrowser'
    default_width = 800
    default_height = 600
    default_iconNum = 'res:/UI/Texture/WindowIcons/structureBrowser.png'
    default_minSize = (600, 450)

    def ApplyAttributes(self, attributes):
        super(StructureBrowserWnd, self).ApplyAttributes(attributes)
        self.browserMyStructures = None
        self.tabs = None
        self.controller = sm.GetService('structureControllers').GetStructureBrowserController()
        self.browserCont = Container(name='browserCont', parent=self.sr.main)
        self.browserAllStructures = BrowserAllStructures(parent=self.browserCont, structureBrowserController=self.controller, padTop=0)
        if idCheckers.IsNPCCorporation(session.corpid):
            self.browserAllStructures.LoadPanel()
        else:
            self.tabs = self.header.tab_group
            self.tabs.AddTab(GetByLabel('UI/Structures/Browser/AllStructures'), self.browserAllStructures, tabID='allStructures', hint=GetByLabel('UI/StructureBrowser/TabAllStructures') + '\n' + GetByLabel('UI/StructureBrowser/Delayed5Minutes'))
            if session.corprole & appConst.corpRoleStationManager:
                self.browserMyStructures = BrowserMyCorpStructures(parent=self.browserCont, padTop=4, structureBrowserController=self.controller)
                self.tabs = self.header.tab_group
                self.tabs.AddTab(GetByLabel('UI/Structures/Browser/MyStructures'), self.browserMyStructures, tabID='myStructures', hint=GetByLabel('UI/StructureBrowser/TabMyStructures') + '\n' + GetByLabel('UI/StructureBrowser/Delayed5Minutes'))
            skyhookController = sm.GetService('structureControllers').GetSkyhookBrowserController()
            self.browserSkyhooks = BrowserAllSkyhooks(parent=self.browserCont, skyhookController=skyhookController, padTop=0)
            self.tabs.AddTab(GetByLabel('UI/StructureBrowser/MySkyhooks'), self.browserSkyhooks, tabID='corpSkyhook', hint=GetByLabel('UI/Structures/Browser/TabMySkyhooks') + '\n' + GetByLabel('UI/StructureBrowser/Delayed5Minutes'))
            self.tabs.AutoSelect()

    def ConstructTopParent(self):
        topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=topParent, state=uiconst.UI_DISABLED, pos=(0, -8, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        WndCaptionLabel(text=GetByLabel('UI/Structures/Browser/StructureBrowser'), subcaption=GetByLabel('UI/StructureBrowser/Delayed5Minutes'), parent=topParent)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def ForceProfileSettingsSelected(self):
        if self.tabs:
            self.header.select_tab('myStructures')
        if self.browserAllStructures:
            self.browserMyStructures.ForceProfileSettingsSelected()

    def CloseByUser(self, *args):
        browserController = sm.GetService('structureControllers').GetStructureBrowserController()
        if not browserController.PlayerWantsToLeaveProfile():
            return
        browserController.SetProfileChangedValue(False)
        Window.CloseByUser(self, *args)
