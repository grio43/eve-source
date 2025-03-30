#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\assetMenu.py
import types
import carbonui.const as uiconst
import uthread
import charactercreator.const as ccConst
import localization
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.login.charcreation_new.charCreationUtils import CCLabel
from eve.client.script.ui.login.charcreation_new.colorPalette import CCColorPalette
from eve.client.script.ui.login.charcreation_new.assetPicker import CharCreationAssetPicker, femaleModifierDisplayNames, maleModifierDisplayNames
GROUPNAMES = {ccConst.SKINGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Complexion',
 ccConst.HAIRGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Hair',
 ccConst.EYESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Eyes',
 ccConst.MAKEUPGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Makeup',
 ccConst.SKINDETAILSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/SkinDetails',
 ccConst.CLOTHESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Clothes',
 ccConst.BODYGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Shape',
 ccConst.BACKGROUNDGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Backgrounds',
 ccConst.POSESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Poses',
 ccConst.LIGHTSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Lights',
 ccConst.PIERCINGGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Piercings',
 ccConst.TATTOOGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Tattoos',
 ccConst.SCARSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Scars',
 ccConst.PROSTHETICS: 'UI/Login/CharacterCreation/AssetMenu/Groups/Prosthetics',
 ccConst.AUGMENTATIONS: 'UI/Login/CharacterCreation/AssetMenu/Groups/Augmentations',
 ccConst.ARCHETYPESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Archetypes'}

class CharCreationAssetMenu(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.name = attributes.menuType or 'CharCreationAssetMenu'
        sm.GetService('cc').LogInfo('CharCreationAssetMenu::ApplyAttributes:: name = ', self.name)
        if attributes.genderID == 0:
            modifierNames = femaleModifierDisplayNames
        else:
            modifierNames = maleModifierDisplayNames
        self.mainContainter = Container(parent=self, name='mainAssetMenuCont', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.mainContainter.clipChildren = 1
        self.togglerIdx = None
        self.toggleFunc = attributes.toggleFunc
        if self.toggleFunc:
            self.togglerIdx = idx = attributes.get('togglerIdx', -1)
            if idx == -1:
                padTop = 16
                padBottom = 4
            else:
                padTop = 4
                padBottom = 16
            self.menuToggler = CharCreationMenuToggler(parent=self.mainContainter, caption=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BodyModifications'), padTop=padTop, padBottom=padBottom, menuType=attributes.menuType, func=self.ToggleMenu, idx=idx)
        for groupID, modifiers in attributes.groups:
            if self._AreAllModifiersEmpty(modifiers):
                continue
            if type(groupID) == types.IntType:
                caption = localization.GetByLabel(GROUPNAMES.get(groupID, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
            else:
                caption = localization.GetByLabel(modifierNames.get(groupID, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
            CharCreationAssetPicker(parent=self.mainContainter, modifier=groupID, caption=caption, padTop=4, padBottom=4, genderID=attributes.genderID, bloodlineID=attributes.bloodlineID, charID=attributes.charID, isSubmenu=False, groupID=groupID)
            for modifier in modifiers:
                if self._IsModifierEmpty(modifier):
                    continue
                caption = localization.GetByLabel(modifierNames.get(modifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
                CharCreationAssetPicker(parent=self.mainContainter, modifier=modifier, caption=caption, padTop=-2, padBottom=4, genderID=attributes.genderID, bloodlineID=attributes.bloodlineID, isSubmenu=True, groupID=groupID)

        menuState = settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})
        for pickerContainer in self.mainContainter.children:
            if isinstance(pickerContainer, CharCreationMenuToggler):
                continue
            key = pickerContainer.modifier or 'group_%s' % getattr(pickerContainer, 'groupID', '')
            if not pickerContainer.isSubmenu and menuState.get(key, 0):
                pickerContainer.Expand(initing=True)

        if self.togglerIdx and self.menuToggler:
            self.menuToggler.SetOrder(self.togglerIdx)

    def _AreAllModifiersEmpty(self, modifiers):
        return modifiers and not any([ not self._IsModifierEmpty(modifier) for modifier in modifiers ])

    def _IsModifierEmpty(self, modifier):
        if type(modifier) is types.IntType:
            return False
        itemTypes, _ = uicore.layer.charactercreation.controller.GetAvailableStyles(modifier)
        if itemTypes:
            return False
        return True

    def ToggleMenu(self, *args):
        if self.toggleFunc:
            self.toggleFunc()

    def CheckIfOversize(self, currentPicker = None):
        canCollapse = []
        totalExpandedHeight = 0
        for each in self.mainContainter.children:
            if not isinstance(each, CharCreationAssetPicker):
                continue
            if each.state == uiconst.UI_HIDDEN:
                continue
            if each.IsExpanded():
                if not each.isSubmenu:
                    subs = each.GetMySubmenus()
                    totalExpandedHeight += each.padTop + each.GetExpandedHeight() + each.padBottom
                    if each is not currentPicker and currentPicker not in each.GetMySubmenus():
                        canCollapse.append((each._expandTime, each))
                else:
                    totalExpandedHeight += each.padTop + each.GetExpandedHeight() + each.padBottom
                if each is not currentPicker and each.isSubmenu:
                    canCollapse.append((each._expandTime, each))
            else:
                totalExpandedHeight += each.padTop + each.GetCollapsedHeight() + each.padBottom

        canCollapse.sort()
        availableSpace = uicore.desktop.height - 150 - ccConst.BUTTON_AREA_HEIGHT
        if totalExpandedHeight > availableSpace:
            diff = totalExpandedHeight - availableSpace
            for expandTime, each in canCollapse:
                if each.IsExpanded():
                    uthread.new(each.Collapse)
                    diff -= each.GetExpandedHeight() - each.GetCollapsedHeight()
                if diff <= 0:
                    break


class CharCreationMenuToggler(Container):
    __guid__ = 'uicls.CharCreationMenuToggler'
    __notifyevents__ = ['OnColorPaletteChanged']
    FULLHEIGHT = 22
    COLLAPSEHEIGHT = 22
    default_align = uiconst.TOTOP
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = COLLAPSEHEIGHT
    default_pos = None
    default_name = 'CharCreationMenuToggler'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        info = uicore.layer.charactercreation.controller.GetInfo()
        Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self.colorPaletteParent = Container(parent=self, align=uiconst.TOLEFT, width=CCColorPalette.COLORPALETTEWIDTH, name='colorPaletteParent', state=uiconst.UI_DISABLED)
        self.captionParent = Container(parent=self, align=uiconst.TOTOP, height=self.COLLAPSEHEIGHT, name='captionParent', state=uiconst.UI_NORMAL)
        self.func = attributes.func
        self.captionParent.OnClick = self.Toggle
        self.captionParent.OnMouseEnter = self.OnCaptionEnter
        self.captionParent.OnMouseExit = self.OnCaptionExit
        self.menuType = attributes.menuType
        self.caption = CCLabel(parent=self.captionParent, align=uiconst.CENTERLEFT, left=10, letterspace=3, shadowOffset=(0, 0), text=attributes.caption, uppercase=1, color=ccConst.COLOR, fontsize=13)
        if self.menuType != 'tattooMenu':
            self.caption.SetAlpha(0.5)
        self.keepColor = 0
        self.AddRadioButton()
        Fill(parent=self.captionParent, color=(0.4, 0.4, 0.4, 0.5))
        self.bevel = bevel = Frame(parent=self.captionParent, color=(1.0, 1.0, 1.0, 0.2), frameConst=ccConst.FILL_BEVEL, state=uiconst.UI_HIDDEN)
        frame = Frame(parent=self.captionParent, frameConst=ccConst.FRAME_SOFTSHADE, color=(1.0, 1.0, 1.0, 0.5))
        frame.padding = (-12, -5, -12, -15)
        self.height = self.captionParent.height
        sm.RegisterNotify(self)

    def AddRadioButton(self, *args):
        self.shadowIcon = Sprite(parent=self.captionParent, name='shadowIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonShadow.dds', color=(0.4, 0.4, 0.4, 0.6))
        self.backIcon = Sprite(parent=self.captionParent, name='backIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonBack.dds')
        self.radioBtnFill = Container(parent=self.captionParent, state=uiconst.UI_HIDDEN, align=uiconst.CENTERRIGHT, pos=(0, 0, 32, 32), idx=0)
        self.radioBtnHilite = Sprite(parent=self.radioBtnFill, name='radioBtnHilite', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonWhite.dds')
        self.radioBtnColor = Sprite(parent=self.radioBtnFill, name='radioBtnColor', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonColor.dds')
        if self.menuType == 'tattooMenu':
            self.SetRadioBtnColor(color='green')

    def OnCaptionEnter(self, *args):
        uicore.layer.charactercreation.controller.SetHintText(None, localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BodyModHelp'))
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_menu_mouse_over_play'))
        if not self.keepColor:
            self.caption.SetAlpha(1.0)
            if self.menuType == 'tattooMenu':
                self.SetRadioBtnColor(color='red')
            elif self.menuType == 'assetMenu':
                self.SetRadioBtnColor(color='green')
        if self.bevel:
            self.bevel.state = uiconst.UI_DISABLED

    def OnCaptionExit(self, *args):
        uicore.layer.charactercreation.controller.SetHintText(None)
        if self.menuType != 'tattooMenu':
            self.caption.SetAlpha(0.5)
        if not self.keepColor:
            if self.menuType == 'tattooMenu':
                self.SetRadioBtnColor(color='green')
            else:
                self.radioBtnFill.state = uiconst.UI_HIDDEN
            if self.bevel:
                self.bevel.state = uiconst.UI_HIDDEN

    def Toggle(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        self.keepColor = 1
        if self.func:
            self.func()
            self.ResetRadioButton()

    def ResetRadioButton(self, *args):
        self.keepColor = 0
        if self.menuType != 'tattooMenu':
            self.caption.SetAlpha(0.5)
        if self.menuType == 'tattooMenu':
            self.SetRadioBtnColor(color='green')
        else:
            self.radioBtnFill.state = uiconst.UI_HIDDEN

    def OnColorPaletteChanged(self, width):
        self.colorPaletteParent.width = width

    def SetRadioBtnColor(self, color = 'green', *args):
        if color == 'green':
            self.radioBtnFill.state = uiconst.UI_DISABLED
            self.radioBtnColor.SetRGB(0, 1, 0)
            self.radioBtnHilite.SetAlpha(0.7)
        elif color == 'red':
            self.radioBtnFill.state = uiconst.UI_DISABLED
            self.radioBtnColor.SetRGB(1, 0, 0)
            self.radioBtnHilite.SetAlpha(0.3)
