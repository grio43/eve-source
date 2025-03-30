#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\ContextMenu.py
import eveicon
from carbonui import uiconst
from carbonui.control.contextMenu.menuEntryData import MenuEntryData, MenuEntryDataCheckbox, MenuEntryDataRadioButton, MenuEntryDataCaption, MenuEntryDataSlider
from carbonui.primitives.container import Container
from carbonui.services.setting import UserSettingEnum, UserSettingBool, UserSettingNumeric
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class _MySampleCont(Container):
    default_bgColor = eveColor.MATTE_BLACK

    def ApplyAttributes(self, attributes):
        super(_MySampleCont, self).ApplyAttributes(attributes)
        EveLabelMedium(parent=self, text='Right click me!', align=uiconst.CENTER)


class Sample1(Sample):
    name = 'Basic'
    description = "Right-click menus are implemented through GetMenu methods on whatever UI object that's pickable (clickable). Normally, you'll want to return an instance of MenuData"

    def sample_code(self, parent):
        from carbonui.control.contextMenu.menuData import MenuData

        def OnEntryClicked(name):
            ShowQuickMessage('{name} executed'.format(name=name))

        class MyContWithMenu(_MySampleCont):

            def GetMenu(self):
                m = MenuData()
                m.AddEntry('First option', func=lambda : OnEntryClicked('First option'))
                m.AddEntry('Second option', func=lambda : OnEntryClicked('Second option'))
                m.AddEntry('Disabled option', isEnabled=False)
                return m

        MyContWithMenu(name='myContWithMenu', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=200, height=200)


class Sample2(Sample):
    name = 'Submenus'
    description = 'Submenus should be used strategically to avoid excessively long menus'

    def sample_code(self, parent):
        from carbonui.control.contextMenu.menuData import MenuData

        def OnEntryClicked(name):
            ShowQuickMessage('{name} executed'.format(name=name))

        class MyContWithMenu(_MySampleCont):

            def GetMenu(self):
                m = MenuData()
                m.AddEntry('First Group', subMenuData=[MenuEntryData('Option A', func=lambda : OnEntryClicked('A')), MenuEntryData('Option B', func=lambda : OnEntryClicked('B'))])
                m.AddEntry('Second Group', subMenuData=[MenuEntryData('Option C', func=lambda : OnEntryClicked('C')), MenuEntryData('Option D', func=lambda : OnEntryClicked('D'))])
                return m

        MyContWithMenu(name='myContWithMenu', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=200, height=200)


class Sample3(Sample):
    name = 'Icons'
    description = 'Icons should be used to draw attention to primary actions in right-click menus, and not used for everything'

    def sample_code(self, parent):
        from carbonui.control.contextMenu.menuData import MenuData

        def OnEntryClicked(name):
            ShowQuickMessage('{name} executed'.format(name=name))

        class MyContWithMenu(_MySampleCont):

            def GetMenu(self):
                m = MenuData()
                m.AddEntry('Add something', func=lambda : OnEntryClicked('Add'), texturePath=eveicon.add)
                m.AddEntry('Refresh something', func=lambda : OnEntryClicked('Refresh'), texturePath=eveicon.refresh)
                m.AddEntry('Secondary action', func=lambda : OnEntryClicked('Secondary action'))
                m.AddSeparator()
                m.AddEntry('Remove something', func=lambda : OnEntryClicked('Remove'), texturePath=eveicon.trashcan)
                return m

        MyContWithMenu(name='myContWithMenu', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=200, height=200)


def OnSettingChanged(value):
    ShowQuickMessage('Setting changed to {value}'.format(value=value))


class Sample4(Sample):
    name = 'Settings'
    description = 'This example also shows the possibility of passing in a list of MenuEntryData instances to MenuData'

    def sample_code(self, parent):
        from carbonui.control.contextMenu.menuData import MenuData
        my_binary_setting = UserSettingBool('my_binary_setting', False)
        my_binary_setting.on_change.connect(OnSettingChanged)
        my_second_binary_setting = UserSettingBool('my_second_binary_setting', True)
        my_second_binary_setting.on_change.connect(OnSettingChanged)
        my_int_setting = UserSettingEnum('my_setting', 1, options=[1, 2, 3])
        my_int_setting.on_change.connect(OnSettingChanged)
        my_numeric_setting = UserSettingNumeric('my_slider_setting', default_value=5.0, min_value=0.0, max_value=10.0)
        my_numeric_setting.on_change.connect(OnSettingChanged)

        class MyContWithMenu(_MySampleCont):

            def GetMenu(self):
                return MenuData([MenuEntryDataCaption(text='Settings Caption'),
                 MenuEntryDataCheckbox(text='My setting #1', setting=my_binary_setting, isEnabled=False, hint='Sorry ... Disabled!'),
                 MenuEntryDataCheckbox(text='My setting #2', setting=my_second_binary_setting),
                 None,
                 MenuEntryData('A radio group', subMenuData=[MenuEntryDataRadioButton(text='Option 1', value=1, setting=my_int_setting), MenuEntryDataRadioButton(text='Option 2', value=2, setting=my_int_setting), MenuEntryDataRadioButton(text='Option 3', value=3, setting=my_int_setting)]),
                 None,
                 MenuEntryDataSlider('My Numeric Value', my_numeric_setting, min_label=str(my_numeric_setting.min_value), max_label=str(my_numeric_setting.max_value))])

        MyContWithMenu(name='myContWithMenu', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=200, height=200)
