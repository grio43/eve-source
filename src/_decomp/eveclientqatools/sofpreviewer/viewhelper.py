#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\viewhelper.py
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
import carbonui.const as uiconst

def CreateSlider(label, minValue, maxValue, startValue, valueChangedFunc, parent):
    name = GetGenericName(label)
    container = CreateContainer(name, parent, padTop=0, padBottom=16)
    slider = _CreateSlider(name, label, minValue, maxValue, startValue, valueChangedFunc, container)
    return slider


def CreateDropdownWithCheckbox(label, values, select, dropdownCallback, checkboxLabel, checkboxCallback, parent):
    name = GetGenericName(label)
    container = CreateContainer(name, parent)
    dropdown = CreateCombo(name, values, dropdownCallback, select, label, container)
    checkbox = CreateCheckbox(name, checkboxLabel, checkboxCallback, container)
    return (dropdown, checkbox)


def CreateLabel(name, width, height, parent, align = uiconst.TOLEFT):
    container = CreateContainer(name, parent)
    label = Label(name=name, text=name, align=align, width=width, height=height, padLeft=5, padRight=5, padTop=0, padBottom=0, parent=container)
    return label


def CreateScrollContainer(name, width, height, parent, align = uiconst.TOTOP):
    container = ScrollContainer(name=name + '_scrollContainer', align=align, width=width, height=height, padLeft=5, padRight=5, padTop=10, parent=parent)
    return container


def CreateDropdown(label, values, callback, select, parent, align = uiconst.TOLEFT):
    name = GetGenericName(label)
    container = CreateContainer(name, parent)
    combo = CreateCombo(name, values, callback, select, label, container, align)
    return combo


def CreateInput(label, value, callback, parent, align = uiconst.TOLEFT):
    name = GetGenericName(label)
    container = CreateContainer(name, parent)
    inputField = _CreateInput(name, value, callback, label, container, align)
    return inputField


def GetComboListIndex(comboContentList, name):
    for index, each in enumerate(comboContentList):
        if each.lower() == name.lower():
            return index


def GetGenericName(label):
    return label.replace(' ', '_').replace(':', '').strip().lower()


def TrySettingComboOptions(comboBox, options, selectedValue):
    options = sorted(options)
    if 'None' in options:
        o = options.pop(options.index('None'))
        options.insert(0, o)
    optionTuple = [ (name, i) for i, name in enumerate(options) ]
    comboBox.LoadOptions(optionTuple)
    return TrySettingComboValue(comboBox, selectedValue)


def TrySettingComboValue(comboBox, selectedValue):
    try:
        comboBox.SelectItemByLabel(selectedValue)
    except RuntimeError:
        comboBox.SelectItemByIndex(0)
        print "Could not select '%s', defaulting to '%s'" % (selectedValue, comboBox.GetKey())

    return comboBox.GetKey()


def CreateCheckbox(name, checkboxLabel, checkboxCallback, parent, align = uiconst.TOLEFT, noPadding = False):
    return Checkbox(name=name + '_constraint', align=align, width=75, height=32, padLeft=0 if noPadding else 10, parent=parent, text=checkboxLabel, callback=checkboxCallback)


def CreateCombo(name, values, callback, select, label, parent, align = uiconst.TOLEFT, width = 150):
    return Combo(name=name + '_combo', align=align, width=width, height=32, parent=parent, label=label, options=[ (name, i) for i, name in enumerate(values) ], callback=callback, select=select)


def _CreateInput(name, value, callback, label, parent, align = uiconst.TOLEFT):
    return SingleLineEditText(name=name + '_input', align=align, label=label, parent=parent, width=150, height=18, setvalue=value, OnFocusLost=callback, OnReturn=callback)


def _CreateSlider(name, label, minValue, maxValue, startVal, valueChangeFunc, parent, align = uiconst.TOLEFT):
    return Slider(name=name, align=align, label=label, parent=parent, width=150, height=18, minValue=minValue, maxValue=maxValue, value=startVal, on_dragging=valueChangeFunc, callback=valueChangeFunc)


def CreateContainer(name, parent, padTop = 16, padBottom = 0, align = uiconst.TOTOP):
    return Container(name=name + '_container', parent=parent, align=align, height=32, padTop=padTop, padBottom=padBottom, padLeft=5, padRight=5)
