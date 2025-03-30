#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\accessGroups\accesGroupsWnd.py
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import WndCaptionLabel
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.structure.accessGroups.accessGroupListCont import GroupListCont
import carbonui.const as uiconst
from eve.client.script.ui.structure.accessGroups.groupCont import GroupCont
from eve.client.script.ui.structure.accessGroups.searchCont import SearchCont
from localization import GetByLabel
from carbonui.uicore import uicore

class AccessGroupsWnd(Window):
    default_captionLabelPath = 'UI/Structures/AccessGroups/GroupWndName'
    explanationLabelPath = 'UI/Structures/AccessGroups/GroupsExplanation'
    default_name = 'Groups window'
    default_windowID = 'GroupsWnd'
    default_width = 800
    default_height = 600
    default_minSize = (600, 400)
    default_iconNum = 'res:/UI/Texture/WindowIcons/accessGroups.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=32, clipChildren=True)
        self.helpIcon = MoreInfoIcon(parent=self.topParent, align=uiconst.CENTERLEFT, hint=GetByLabel(self.explanationLabelPath))
        if not settings.user.ui.Get('accessGroup_seenExtraInfo', False):
            uicore.animations.BlinkIn(self.helpIcon, startVal=0.1, endVal=1.0, duration=1.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_BOUNCE)
            self.helpIcon.OnMouseEnter = self.OnHelpIconMouseEnter
        self.controller = sm.GetService('structureControllers').GetAccessGroupController()
        self.mainCont = Container(name='mainCont', parent=self.sr.main, padding=0)
        self.searchCont = SearchCont(name='seachCont', parent=self.topParent, align=uiconst.TORIGHT, controller=self.controller)
        groupListParent = DragResizeCont(name='groupListCont', parent=self.mainCont, align=uiconst.TOLEFT_PROP, minSize=0.1, maxSize=0.5, defaultSize=0.5)
        self.groupCont = GroupCont(name='groupCont', parent=self.mainCont, padding=(0, 2, 0, 2), controller=self.controller)
        self.groupListCont = GroupListCont(name='groupListCont', parent=groupListParent, controller=self.controller)

    def OnHelpIconMouseEnter(self, *args):
        settings.user.ui.Set('accessGroup_seenExtraInfo', True)
        self.helpIcon.StopAnimations()
        MoreInfoIcon.OnMouseEnter(self.helpIcon, *args)
