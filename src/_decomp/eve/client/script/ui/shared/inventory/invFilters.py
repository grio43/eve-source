#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\invFilters.py
from math import pi
import eveicon
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.dragResizeCont import DragResizeCont
import carbonui.const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.themeColored import FillThemeColored
from localization import GetByLabel
from carbonui.uicore import uicore
from signals import Signal

class InvFilters(DragResizeCont):
    default_name = 'treeBottomCont'
    default_align = uiconst.TOBOTTOM
    default_state = (uiconst.UI_PICKCHILDREN,)
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        self.on_filters_updated = Signal(signalName='on_filters_updated')
        self.on_expand_collapse_animation = Signal(signalName='on_expand_collapse_animating')
        show_filter_toggle_button = attributes.get('show_filter_toggle_button', True)
        self.filtersEnabledBtnColor = None
        DragResizeCont.ApplyAttributes(self, attributes)
        self.windowID = attributes.windowID
        self.filterEntries = []
        self.ConstructHeader()
        self.ConstrucEnabledStateButton(show_filter_toggle_button)
        self.ConstructFilterContainer()

    def ConstructHeader(self):
        self.filterHeaderCont = Container(name='filterHeaderCont', parent=self, align=uiconst.TOTOP, height=24, padRight=8, state=uiconst.UI_NORMAL)
        self.filterHeaderCont.OnDblClick = self.OnExpandFiltersBtn

    def ConstrucEnabledStateButton(self, show_filter_toggle_button):
        self.createFilterBtn = ButtonIcon(name='createFilterBtn', parent=ContainerAutoSize(parent=self.filterHeaderCont, align=uiconst.TORIGHT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.add, func=self.OnCreateFilterBtn, hint=GetByLabel('UI/Inventory/CreateFilter'))
        if show_filter_toggle_button:
            filtersEnabledBtn = Container(name='filtersEnabledBtn', parent=self.filterHeaderCont, align=uiconst.TORIGHT, state=uiconst.UI_NORMAL, width=24, pickRadius=7, idx=0)
            filtersEnabledBtn.OnClick = self.OnFiltersEnabledBtnClicked
            self.filtersEnabledBtnColor = Sprite(bgParent=filtersEnabledBtn, texturePath='res:/UI/Texture/CharacterCreation/radiobuttonColor.dds', color=eveColor.SUCCESS_GREEN[:3] + (0.0,))
            Sprite(bgParent=filtersEnabledBtn, texturePath='res:/UI/Texture/CharacterCreation/radiobuttonBack.dds', opacity=0.4)
            Sprite(bgParent=filtersEnabledBtn, texturePath='res:/UI/Texture/CharacterCreation/radiobuttonShadow.dds', color=(0.4, 0.4, 0.4, 0.4))
        labelCont = Container(name='labelCont', parent=self.filterHeaderCont, clipChildren=True)
        Label(left=24, parent=labelCont, text=GetByLabel('UI/Inventory/MyFilters'), align=uiconst.CENTERLEFT)
        self.expandFiltersBtn = ButtonIcon(name='expandFiltersBtn', parent=labelCont, align=uiconst.TOLEFT, iconSize=7, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', width=24, func=self.OnExpandFiltersBtn)

    def ConstructFilterContainer(self):
        self.filterCont = ScrollContainer(name='filterCont', parent=self, align=uiconst.TOALL)

    def OnCreateFilterBtn(self, *args):
        sm.GetService('itemFilter').CreateFilter()

    def OnFiltersEnabledBtnClicked(self, *args):
        for filterEntry in self.filterEntries:
            filterEntry.checkbox.SetChecked(False)

    def OnExpandFiltersBtn(self, *args):
        if self.filterCont.pickState == uiconst.TR2_SPS_ON:
            self.CollapseFilters()
        else:
            self.ExpandFilters()

    def ExpandFilters(self, animate = True):
        self.expandFiltersBtn.SetRotation(0)
        self.expandFiltersBtn.Disable()
        self.EnableDragResize()
        self.minSize = 100
        self.maxSize = 0.5
        if animate:
            self.on_expand_collapse_animation(animationStart=True)
            height = settings.user.ui.Get('invFiltersHeight_%s' % self.windowID, 150)
            height = max(self.GetMinSize(), min(self.GetMaxSize(), height))
            uicore.animations.MorphScalar(self, 'height', self.height, height, duration=0.3)
            uicore.animations.FadeIn(self.filterCont, duration=0.3, sleep=True)
            self.on_expand_collapse_animation(animationStart=False)
        self.expandFiltersBtn.Enable()
        self.filterCont.EnableScrollbars()
        self.filterCont.Enable()
        settings.user.ui.Set('invFiltersExpanded_%s' % self.windowID, True)

    def CollapseFilters(self, animate = True):
        self.filterCont.Disable()
        self.expandFiltersBtn.Disable()
        self.expandFiltersBtn.SetRotation(pi)
        self.DisableDragResize()
        height = self.filterHeaderCont.height + self.dragArea.height
        self.minSize = self.maxSize = height
        self.filterCont.DisableScrollbars()
        if animate:
            self.on_expand_collapse_animation(animationStart=True)
            uicore.animations.MorphScalar(self, 'height', self.height, height, duration=0.3)
            uicore.animations.FadeOut(self.filterCont, duration=0.3, sleep=True)
            self.on_expand_collapse_animation(animationStart=False)
        self.height = height
        self.filterCont.opacity = 0.0
        self.expandFiltersBtn.Enable()
        settings.user.ui.Set('invFiltersExpanded_%s' % self.windowID, False)

    def ConstructFilters(self):
        for filterEntry in self.filterEntries:
            filterEntry.Close()

        self.filterEntries = []
        for filt in sm.GetService('itemFilter').GetFilters():
            filterEntry = FilterEntry(parent=self.filterCont, filter=filt, eventListener=self)
            self.filterEntries.append(filterEntry)

    def ExpandOrCollapeFilters(self):
        if not settings.user.ui.Get('invFiltersExpanded_%s' % self.windowID, False):
            self.CollapseFilters(animate=False)
        else:
            self.ExpandFilters(animate=False)

    def SetActiveFilters(self, filters):
        if self.filtersEnabledBtnColor:
            if filters:
                uicore.animations.FadeIn(self.filtersEnabledBtnColor, 0.9, curveType=uiconst.ANIM_OVERSHOT)
            else:
                uicore.animations.FadeOut(self.filtersEnabledBtnColor)

    def GetActiveFilters(self):
        filters = []
        for filterEntry in self.filterEntries:
            flt = filterEntry.GetFilter()
            if flt:
                filters.append(flt)

        return filters

    def SetSingleFilter(self, selectedEntry):
        for entry in self.filterEntries:
            if entry != selectedEntry:
                entry.checkbox.SetChecked(False)

    def DeselectAllFilters(self):
        for entry in self.filterEntries:
            entry.checkbox.SetChecked(False)

    def UpdateFilters(self, *args):
        self.on_filters_updated()

    def Close(self):
        self.on_filters_updated.clear()
        self.on_expand_collapse_animation.clear()
        DragResizeCont.Close(self)


class FilterEntry(Container):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 22

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.eventListener = attributes.eventListener
        self.filter = attributes.filter
        filtName, _, _ = self.filter
        self.checkbox = Checkbox(name='checkbox', parent=self, checked=False, callback=self.OnCheckbox, align=uiconst.CENTERLEFT, text=filtName, left=5, wrapLabel=False)
        self.checkbox.GetMenu = self.GetMenu
        self.hoverBG = ListEntryUnderlay(bgParent=self)

    def OnClick(self):
        self.checkbox.ToggleState()

    def OnDblClick(self):
        self.eventListener.SetSingleFilter(self)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        self.checkbox.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.checkbox.OnMouseExit()

    def GetFilter(self):
        if self.checkbox.checked:
            return self.filter

    def OnMouseDown(self, *args):
        super(FilterEntry, self).OnMouseDown()
        self.checkbox.OnMouseDown()

    def OnMouseUp(self, *args):
        super(FilterEntry, self).OnMouseUp()
        self.checkbox.OnMouseUp()

    def OnCheckbox(self, checkbox):
        self.eventListener.UpdateFilters()

    def GetMenu(self):
        m = []
        text = self.checkbox.GetLabelText()
        m.append((GetByLabel('UI/Inventory/Filters/Edit'), self.EditFilter, [text]))
        m.append((GetByLabel('UI/Commands/Remove'), sm.GetService('itemFilter').RemoveFilter, [text]))
        return m

    def EditFilter(self, filterName):
        self.eventListener.DeselectAllFilters()
        sm.GetService('itemFilter').EditFilter(filterName)
