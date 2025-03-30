#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crate\view\fixed.py
from carbonui import const as uiconst, ButtonVariant
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from crates.const import MAX_MULTI_OPEN
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionLarge
from eve.client.script.ui.crate.button import CrateButton
import localization
import uthread

def center(text):
    return u'<center>{}</center>'.format(text)


class FixedView(Container):

    def ApplyAttributes(self, attributes):
        super(FixedView, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.shouldAnimateView = attributes.shouldAnimateView
        self.openCrateButton = None
        uthread.new(self.Layout)

    def Layout(self):
        self.Flush()
        self.mainCont = Container(parent=self, align=uiconst.TOALL, padding=(380, 38, 24, 24), padLeft=380, padTop=38)
        cont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOBOTTOM)
        buttonGroupCont = ContainerAutoSize(parent=cont, align=uiconst.BOTTOMRIGHT, minWidth=400, idx=0, top=8)
        self.buttonGroup = ButtonGroup(parent=buttonGroupCont, align=uiconst.CENTER)
        self.contentCont = Container(name='contentCont', parent=self.mainCont, align=uiconst.TOALL, padBottom=8)
        self.descriptionLabel = EveCaptionLarge(name='descriptionLabel', parent=self.contentCont, align=uiconst.TOTOP, text=self.controller.caption, opacity=0.0)
        self.LayoutScroll()
        self.LayoutButtons()
        self.ShowContent()

    def LayoutScroll(self):
        self.scroll = LootScroll(parent=self.contentCont, name='lootScroll', align=uiconst.TOALL, controller=self.controller, opacity=0.0)
        if self.controller.stacksize <= 0:
            self.scroll.Hide()
            self.descriptionLabel.Hide()

    def RevealButtons(self):
        self.LayoutButtons()
        for button in self.buttonGroup.buttons:
            animations.FadeTo(button)

    def LayoutButtons(self):
        self.buttonGroup.FlushButtons()
        self.openCrateButton = None
        if self.controller.stacksize > 0:
            if self.controller.stacksize > 1:
                if self.controller.stacksize > MAX_MULTI_OPEN:
                    text = localization.GetByLabel('UI/Crate/OpenMultiple', quantity=MAX_MULTI_OPEN)
                else:
                    text = localization.GetByLabel('UI/Crate/OpenAll', quantity=self.controller.stacksize)
                Button(parent=self.buttonGroup, label=text, func=self.OpenMultiple, variant=ButtonVariant.GHOST)
            text = localization.GetByLabel('UI/Crate/OpenCrate', quantity=self.controller.stacksize)
            self.openCrateButton = CrateButton(parent=self.buttonGroup, align=uiconst.NOALIGN, label=text, func=self.OpenCrate, name='CrateButton_OpenButton')
        else:
            Button(parent=self.buttonGroup, label=localization.GetByLabel('UI/Crate/Finish'), func=self.controller.Finish, args=())

    def ShowContent(self):
        if self.shouldAnimateView:
            self.AnimEntry()
        else:
            self.descriptionLabel.opacity = 1.0
            self.scroll.opacity = 1.0

    def AnimEntry(self):
        animations.FadeTo(self.descriptionLabel)
        uthread.new(self.scroll.AnimEntry, offset=0.0, child_offset=0.0)
        if self.openCrateButton:
            animations.FadeTo(self.openCrateButton, timeOffset=0.0, callback=self.openCrateButton.Enable)

    def OpenCrate(self, button):
        self.DisableButtons()
        try:
            animations.FadeTo(self.contentCont, startVal=self.contentCont.opacity, endVal=0.2)
            self.controller.OpenCrate()
        finally:
            self.RevealButtons()
            animations.FadeIn(self.contentCont)

    def OpenMultiple(self, btn):
        self.DisableButtons()
        try:
            animations.FadeTo(self.contentCont, startVal=self.contentCont.opacity, endVal=0.2, duration=0.1)
            self.controller.OpenMultipleCrates()
        finally:
            self.RevealButtons()
            animations.FadeIn(self.contentCont)
            self.descriptionLabel.opacity = 0.0
            self.scroll.opacity = 0.0
            uthread.new(self.AnimEntry)

    def DisableButtons(self, *args):
        for button in self.buttonGroup.buttons:
            button.Disable()


class LootItemEntry(Container):
    default_height = 40
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(LootItemEntry, self).ApplyAttributes(attributes)
        self.item = attributes.item
        self.AddGrid()
        self.AddIcon()
        self.AddLabel()

    def AddGrid(self):
        self.grid = LayoutGrid(parent=self, align=uiconst.TOPLEFT, columns=2)

    def AddIcon(self):
        self.icon = None

    def AddLabel(self):
        self.label = EveLabelMedium(parent=self.grid, align=uiconst.CENTERLEFT, text=self.item.get_name())

    def AnimEntry(self, offset = 0.0):
        if self.label:
            animations.FadeTo(self.label, timeOffset=offset)
        if self.icon:
            animations.FadeTo(self.icon, duration=0.15, timeOffset=offset)
            animations.MorphVector2(self.icon, 'scale', startVal=(4.0, 4.0), endVal=(0.9, 0.9), duration=0.15, timeOffset=offset, sleep=True)
            animations.MorphVector2(self.icon, 'scale', startVal=(0.9, 0.9), endVal=(1.0, 1.0), duration=0.15)
            animations.SpGlowFadeOut(self.icon, duration=0.3)
            animations.MorphScalar(self.icon, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3)


class LootItemFromTypeEntry(LootItemEntry):

    def AddIcon(self):
        icon = Icon(align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=32, height=32, typeID=self.item.typeID, isCopy=self.item.is_copy())
        techIcon = self.item.get_tech_icon()
        if techIcon:
            iconCont = Container(align=uiconst.CENTER, width=32, height=32)
            techIcon.SetParent(iconCont)
            icon.SetParent(iconCont)
            self.icon = iconCont
        else:
            self.icon = icon
        self.grid.AddCell(self.icon, cellPadding=(8, 8))


class SpecialLootItemEntry(LootItemEntry):

    def AddIcon(self):
        self.icon = Sprite(align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=32, height=32, texturePath=self.item.get_icon())
        self.grid.AddCell(self.icon, cellPadding=(8, 8))


class LootScroll(ScrollContainer):

    def ApplyAttributes(self, attributes):
        super(LootScroll, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        for item in self.controller.GetSortedLoot():
            LootItemFromTypeEntry(parent=self, item=item)

        for item in self.controller.GetSpecialLoot():
            (SpecialLootItemEntry(parent=self, item=item),)

    @property
    def verticalScrollPosition(self):
        return self.GetPositionVertical()

    @verticalScrollPosition.setter
    def verticalScrollPosition(self, fraction):
        self.ScrollToVertical(fraction)

    def AnimEntry(self, offset = 0.0, child_offset = 0.1):
        animations.FadeTo(self, duration=0.5, timeOffset=offset)
        for i, entry in enumerate(self.mainCont.children):
            uthread.new(entry.AnimEntry, offset=child_offset * i + offset)

        animations.MorphScalar(self, 'verticalScrollPosition', duration=2.0, timeOffset=offset + 0.6, sleep=True)
        animations.MorphScalar(self, 'verticalScrollPosition', startVal=1.0, endVal=0.0, duration=1.0, timeOffset=0.4)


class FixedViewForRandomizedLoot(FixedView):

    def LayoutScroll(self):
        self.scroll = LootScroll(parent=self.contentCont, name='lootScroll', align=uiconst.TOALL, controller=self.controller)
        self.descriptionLabel.Hide()
        self.controller.ClaimAllLoot()

    def LayoutButtons(self):
        self.buttonGroup.FlushButtons()
        self.openCrateButton = None
        if self.controller.stacksize > 0:
            if self.controller.stacksize > 1:
                if self.controller.stacksize > MAX_MULTI_OPEN:
                    text = localization.GetByLabel('UI/Crate/HackMultiple', quantity=MAX_MULTI_OPEN)
                else:
                    text = localization.GetByLabel('UI/Crate/HackAll', quantity=self.controller.stacksize)
                Button(parent=self.buttonGroup, label=text, func=self.OpenMultiple, variant=ButtonVariant.GHOST)
            text = localization.GetByLabel('UI/Crate/HackCrate', quantity=self.controller.stacksize)
            self.openCrateButton = CrateButton(parent=self.buttonGroup, align=uiconst.NOALIGN, label=text, func=self.OpenCrate)
            self.openCrateButton.Enable()
        else:
            Button(parent=self.buttonGroup, label=localization.GetByLabel('UI/Crate/Finish'), func=self.controller.Finish, args=())

    def ShowContent(self):
        pass
