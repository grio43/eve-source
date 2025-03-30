#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\breadcrumbLabel.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst, contentGroupProvider
iconSize = 24

class BreadcrumbLabel(ContainerAutoSize):
    default_name = 'BreadcrumbLabel'
    default_alignMode = uiconst.TOLEFT

    def UpdateContentGroup(self, contentGroupID, itemID):
        self.Flush()
        contentGroup = contentGroupProvider.GetContentGroup(contentGroupID, itemID)
        self.ConstructBreadcrumbEntries(contentGroup)
        entry = CurrentContentGroupEntry(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, contentGroup=contentGroup, opacity=0.0)
        animations.FadeIn(entry, duration=1.0)
        self.SetSizeAutomatically()

    def ConstructBreadcrumbEntries(self, contentGroup):
        if contentGroup.contentGroupID != contentGroupConst.contentGroupHome:
            for contentGroup in contentGroup.GetAncestorList():
                BreadcrumbEntry(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, contentGroup=contentGroup)
                Label(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, fontSize=12, text='/', padRight=16, opacity=0.5)


class BreadcrumbEntry(ContainerAutoSize):
    OPACITY_HOVER = 1.2
    default_name = 'BreadcrumbEntry'
    default_padRight = 16
    default_alignMode = uiconst.BOTTOMLEFT
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.5
    fontSize = 12

    def ApplyAttributes(self, attributes):
        super(BreadcrumbEntry, self).ApplyAttributes(attributes)
        self.contentGroup = attributes.contentGroup
        Label(parent=self, align=uiconst.BOTTOMLEFT, text=self.contentGroup.GetName(), fontsize=self.fontSize, opacity=1.0)
        self.SetSizeAutomatically()

    def OnClick(self):
        from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=self.contentGroup.GetID(), itemID=self.contentGroup.itemID)

    def OnMouseEnter(self, *args):
        animations.FadeTo(self, self.opacity, self.OPACITY_HOVER, duration=0.1)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, self.default_opacity, duration=0.2)


class CurrentContentGroupEntry(BreadcrumbEntry):
    default_opacity = 1.0
