#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\form.py
import log
import types
import carbonui.const as uiconst
import localization
from carbon.common.script.sys.service import Service
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditPassword import SingleLineEditPassword
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui import AxisAlignment
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.uicore import uicore
from carbonui.control.tabGroup import TabGroup
from eve.common.lib import appConst as const

class Form(Service):
    __guid__ = 'svc.form'
    __exportedcalls__ = {'GetForm': [],
     'ProcessForm': []}
    __servicename__ = 'form'
    __displayname__ = 'Form Service'
    __dependencies__ = []

    def __init__(self):
        Service.__init__(self)

    def GetForm(self, format, parent):
        _form, retfields, reqresult, panels, errorcheck, refresh = self._GetForm(format, parent)
        if _form.align == uiconst.TOALL:
            _form.SetSize(0, 0)
            _form.SetPosition(0, 0)
            _form.padding = const.defaultPadding
        elif _form.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
            _form.SetPosition(0, 0)
            _form.width = 0
            _form.padding = const.defaultPadding
        elif _form.align in (uiconst.TOLEFT, uiconst.TORIGHT):
            _form.SetPosition(0, 0)
            _form.height = 0
            _form.padding = const.defaultPadding
        else:
            _form.left = _form.top = const.defaultPadding
        return (_form,
         retfields,
         reqresult,
         panels,
         errorcheck,
         refresh)

    def _GetForm(self, format, parent, retfields = [], reqresult = [], errorcheck = None, tabpanels = [], tabgroup = [], refresh = [], wipe = 1):
        if not parent.IsUnder(uicore.desktop):
            log.LogTraceback('Form parent MUST be hooked on the desktop; it is impossible to know the real dimensions of stuff within otherwise.')
        self.retfields = retfields
        self.reqresult = reqresult
        self.errorcheck = errorcheck
        self.tabpanels = tabpanels
        self.tabgroup = tabgroup
        self.refresh = refresh
        if not isinstance(parent, FormWnd):
            log.LogTraceback('Incompatible formparent, please change it to xtriui.FormWnd')
        self.parent = parent
        self.parent.sr.panels = {}
        self.parent.sr.focus = None
        if wipe:
            self.retfields = []
            self.reqresult = []
            self.tabpanels = []
            self.tabgroup = []
            self.refresh = []
        for each in format:
            self.type = each
            typeName = self.type['type']
            self.leftPush = self.type.get('labelwidth', 0) or 80
            self.code = None
            if typeName == 'errorcheck':
                self.AddErrorcheck()
                continue
            elif typeName == 'data':
                self.AddData()
                continue
            elif typeName == 'tab':
                self.AddTab()
                continue
            elif typeName in ('btline', 'bbline'):
                self.AddLine()
                continue
            elif typeName == 'push':
                self.AddPush()
            elif typeName == 'header':
                self.AddHeader()
            elif typeName == 'labeltext':
                self.AddLabeltext()
            elif typeName == 'text':
                self.AddText()
            elif typeName == 'edit':
                self.AddEdit()
            elif typeName == 'textedit':
                self.AddTextedit()
            elif typeName == 'checkbox':
                self.AddCheckbox()
            elif typeName == 'combo':
                self.AddCombo()
            elif typeName == 'btnonly':
                self.AddBtnonly()
            else:
                log.LogWarn('Unknown fieldtype in form generator')
                continue
            if self.type.has_key('key'):
                if self.code:
                    self.retfields.append([self.code, self.type])
                    self.parent.sr.Set(self.type['key'], self.code)
                else:
                    self.parent.sr.Set(self.type['key'], self.new)
            if self.type.get('required', 0) == 1:
                self.reqresult.append([self.code, self.type])
            if self.type.get('selectall', 0) == 1 and getattr(self.code, 'SelectAll', None):
                self.code.SelectAll()
            if self.type.get('setfocus', 0) == 1:
                self.parent.sr.focus = self.code
            if self.type.has_key('stopconfirm') and hasattr(self.code, 'stopconfirm'):
                self.code.stopconfirm = self.type['stopconfirm']
            if self.type.get('frame', 0) == 1:
                idx = 0
                for child in self.new.children:
                    if child.name.startswith('Line'):
                        idx += 1

                Container(name='leftpush', parent=self.new, align=uiconst.TOLEFT, width=6, idx=idx)
                Container(name='rightpush', parent=self.new, align=uiconst.TORIGHT, width=6, idx=idx)
                Line(parent=self.new, align=uiconst.TOLEFT, idx=idx)
                Line(parent=self.new, align=uiconst.TORIGHT, idx=idx)

        if wipe and len(self.tabgroup):
            tabs = TabGroup(name='tabparent', parent=self.parent, idx=0)
            tabs.Startup(self.tabgroup, 'hybrid')
            maxheight = 0
            for panel in self.tabpanels:
                maxheight = max(maxheight, panel.height)

            self.parent.height = maxheight + tabs.height
        else:
            if len(self.tabpanels):
                for each in self.tabpanels:
                    each.state = uiconst.UI_HIDDEN

                self.tabpanels[0].state = uiconst.UI_PICKCHILDREN
            self.RefreshHeight(self.parent)
        uicore.registry.SetFocus(self)
        return (self.parent,
         self.retfields,
         self.reqresult,
         self.tabpanels,
         self.errorcheck,
         self.refresh)

    def RefreshHeight(self, w):
        w.height = sum([ x.height for x in w.children if x.state != uiconst.UI_HIDDEN and x.align in (uiconst.TOBOTTOM, uiconst.TOTOP) ])

    def AddErrorcheck(self):
        self.errorcheck = self.type['errorcheck']

    def AddData(self):
        self.retfields.append(self.type['data'])

    def AddTab(self):
        _form, _retfield, _required, _tabpanels, _errorcheck, _refresh = self._GetForm(self.type['format'], FormWnd(name='form', align=uiconst.TOTOP, parent=self.parent), self.retfields, self.reqresult, self.errorcheck, self.tabpanels, self.tabgroup, self.refresh, 0)
        if self.type.has_key('key'):
            self.parent.sr.panels[self.type['key']] = _form
        if self.type.get('panelvisible', 0):
            _form.state = uiconst.UI_PICKCHILDREN
        else:
            _form.state = uiconst.UI_HIDDEN
        if self.type.has_key('tabvisible'):
            if self.type['tabvisible'] == 1:
                self.tabgroup.append([self.type['tabtext'],
                 _form,
                 self,
                 None])
        else:
            self.tabgroup.append([self.type['tabtext'],
             _form,
             self,
             None])

    def AddPush(self):
        self.new = Container(name='push', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 6))

    def AddLine(self):
        (Container(parent=self.parent, align=uiconst.TOTOP, height=16),)

    def AddHeader(self):
        self.new = Container(name='headerField', parent=self.parent, align=uiconst.TOTOP, padding=(0, 8, 0, 0))
        header = eveLabel.EveLabelLarge(text=self.type.get('text', ''), parent=self.new, name='header', align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.new.height = max(self.type.get('height', 17), header.textheight)
        self.refresh.append((self.new, header))

    def AddLabeltext(self):
        self.new = Container(name='labeltextField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 20))
        text = eveLabel.EveLabelMedium(name='text', parent=self.new, align=uiconst.TOTOP, padding=(0, 4, 0, 0), state=uiconst.UI_NORMAL, text=self.type.get('text', ''))
        label = self.type.get('label', '')
        if label and label != '_hide':
            pad_top = 4 if self.type.get('text', '') else 0
            label = eveLabel.EveLabelSmall(name='label', parent=self.new, align=uiconst.TOTOP, padding=(8,
             pad_top,
             8,
             8), text=label)
            self.refresh.append((self.new, text, label))
        else:
            self.refresh.append((self.new, text))

    def AddText(self):
        left = self.type.get('left', 0)
        self.new = Container(name='textField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 20), padding=(left,
         0,
         0,
         0))
        fontsize = self.type.get('fontsize', 12)
        text = eveLabel.Label(text=self.type.get('text', ''), parent=self.new, align=uiconst.TOTOP, name='text', padding=(0, 3, 0, 3), fontsize=fontsize, maxLines=1 if bool(self.type.get('tabstops', [])) else None, state=uiconst.UI_NORMAL, tabs=self.type.get('tabstops', []))
        self.new.height = max(self.new.height, int(text.textheight + 6))
        self.refresh.append((self.new, text))

    def AddEdit(self):
        self.new = Container(name='editField', parent=self.parent, align=uiconst.TOTOP)
        config = 'edit_%s' % self.type['key']
        ints = self.type.get('intonly', None)
        floats = self.type.get('floatonly', None)
        passwordCharacter = self.type.get('passwordChar', None)
        decimalPlaces = SingleLineEditFloat.default_decimalPlaces
        minValue = maxValue = 0
        singleLineEditClass = SingleLineEditText
        if ints:
            singleLineEditClass = SingleLineEditInteger
            minValue, maxValue = ints
        elif floats:
            singleLineEditClass = SingleLineEditFloat
            if len(floats) > 2:
                minValue, maxValue, decimalPlaces = floats
            else:
                minValue, maxValue = floats
        elif passwordCharacter:
            singleLineEditClass = SingleLineEditPassword
        self.code = singleLineEditClass(name=config, parent=self.new, setvalue=self.type.get('setvalue', ''), padding=(self.leftPush,
         2,
         0,
         2), align=uiconst.TOTOP, maxLength=self.type.get('maxlength', None) or self.type.get('maxLength', None), readonly=self.type.get('readonly', 0), autoselect=self.type.get('autoselect', 0), isTypeField=self.type.get('isTypeField', False), isCharacterField=self.type.get('isCharacterField', False), isCharCorpOrAllianceField=self.type.get('isCharCorpOrAllianceField', False), passwordCharacter=self.type.get('passwordChar', None), minValue=minValue, maxValue=maxValue, decimalPlaces=decimalPlaces)
        self.new.height = self.code.height + self.code.padTop * 4
        width = self.type.get('width', None)
        if width:
            self.code.SetAlign(uiconst.TOLEFT)
            self.code.width = width
        if self.type.has_key('OnReturn'):
            self.code.data = {'key': self.type['key']}
            self.code.OnReturn = self.type['OnReturn']
        if self.type.has_key('unusedkeydowncallback'):
            self.code.OnUnusedKeyDown = self.type['unusedkeydowncallback']
        if self.type.has_key('onanychar'):
            self.code.OnAnyChar = self.type['onanychar']
        label = self.type.get('label', '')
        text = self.type.get('text', None)
        caption = text or label
        if label == '_hide':
            self.code.padLeft = 0
        elif caption:
            l = eveLabel.EveLabelSmall(text=caption, align=uiconst.CENTERLEFT, parent=self.new, name='label', left=7, width=self.leftPush - 6)

    def AddTextedit(self):
        self.new = Container(name='texteditField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 68))
        self.code = EditPlainText(setvalue=self.type.get('setvalue', '') or self.type.get('text', ''), parent=self.new, padding=(self.leftPush,
         2,
         0,
         2), readonly=self.type.get('readonly', 0), showattributepanel=self.type.get('showAttribPanel', 0), maxLength=self.type.get('maxlength', None) or self.type.get('maxLength', None))
        label = self.type.get('label', '')
        if label == '_hide':
            self.code.padLeft = 0
        elif label:
            eveLabel.EveLabelSmall(text=label, parent=self.new, name='label', left=7, width=self.leftPush - 6, top=5)

    def AddCheckbox(self):
        self.new = Container(name='checkboxCont', parent=self.parent, align=uiconst.TOTOP, pos=(0, 0, 0, 18))
        group = self.type.get('group', None)
        if group:
            self.code = RadioButton(text=self.type.get('text', ''), parent=self.new, settingsKey=self.type.get('name', 'none'), retval=self.type['key'], checked=self.type.get('setvalue', 0), groupname=group, callback=self.parent.OnCheckboxChange)
        else:
            self.code = Checkbox(text=self.type.get('text', ''), parent=self.new, settingsKey=self.type.get('name', 'none'), checked=self.type.get('setvalue', 0), callback=self.parent.OnCheckboxChange)
        self.code.data = {}
        onchange = self.type.get('OnChange', None) or self.type.get('onchange', None)
        if onchange:
            self.code.SetSettingsKey(self.type['key'])
            self.code.data = {'key': self.type['key'],
             'callback': onchange}
        if self.type.has_key('showpanel'):
            self.code.data['showpanel'] = self.type['showpanel']
        if self.code.sr.label:
            self.refresh.append((self.code, self.code.sr.label))
        if self.type.get('hidden', 0):
            self.code.state = uiconst.UI_HIDDEN

    def AddCombo(self):
        self.new = Container(name='comboField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 32))
        options = self.type.get('options', [(localization.GetByLabel('UI/Common/None'), None)])
        self.code = Combo(label='', parent=self.new, options=options, name=self.type.get('key', 'combo'), select=self.type.get('setvalue', ''), padding=(self.leftPush,
         2,
         0,
         2), align=uiconst.TOTOP, callback=self.type.get('callback', None), labelleft=self.leftPush, prefskey=self.type.get('prefskey', None))
        self.new.height = self.code.height + self.code.padTop * 4
        width = self.type.get('width', None)
        if width:
            self.code.SetAlign(uiconst.TOLEFT)
            self.code.width = width
        label = self.type.get('label', '')
        if label == '_hide':
            self.code.padLeft = 0
        else:
            eveLabel.EveLabelSmall(text=label, parent=self.new, name='label', left=7, width=self.leftPush - 6, align=uiconst.CENTERLEFT)

    def AddBtnonly(self):
        self.new = Container(name='btnonly', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 20))
        align = uiconst.TORIGHT
        for wantedbtn in self.type['buttons']:
            if wantedbtn.has_key('align'):
                al = {'left': uiconst.CENTERLEFT,
                 'right': uiconst.CENTERRIGHT}
                align = al.get(wantedbtn['align'], uiconst.CENTERRIGHT)

        uniSize = self.type.get('uniSize', True)
        if uniSize:
            size_mode = ButtonSizeMode.EQUAL
        else:
            size_mode = ButtonSizeMode.DYNAMIC
        ButtonGroup(parent=self.new, align=uiconst.TOTOP, button_size_mode=size_mode, button_alignment=axis_alignment_from_legacy_align(align), buttons=[ Button(label=data['caption'], func=data['function'], args=data.get('args', 'self'), btn_modalresult=data.get('btn_modalresult', 0), btn_default=data.get('btn_default', 0), btn_cancel=data.get('btn_cancel', 0)) for data in self.type['buttons'] ])

    def ProcessForm(self, retfields, required, errorcheck = None):
        result = {}
        for each in retfields:
            if type(each) == dict:
                result.update(each)
                continue
            value = each[0].GetValue()
            if each[1]['type'] == 'checkbox' and each[1].has_key('group') and value == 1:
                result[each[1]['group']] = each[1]['key']
            else:
                result[each[1]['key']] = value

        if errorcheck:
            hint = errorcheck(result)
            if hint == 'silenterror':
                return
            if hint:
                eve.Message('CustomInfo', {'info': hint})
                return
        if len(required):
            for each in required:
                retval = each[0].GetValue()
                if retval is None or retval == '' or type(retval) in types.StringTypes and retval.strip() == '':
                    fieldname = ''
                    if each[1].has_key('label'):
                        fieldname = each[1]['label']
                        if fieldname == '_hide':
                            fieldname = each[1]['key']
                    else:
                        fieldname = each[1]['key']
                    eve.Message('MissingRequiredField', {'fieldname': fieldname})
                    return
                if each[1]['type'] == 'checkbox' and each[1].has_key('group'):
                    if each[1]['group'] not in result:
                        eve.Message('MissingRequiredField', {'fieldname': each[1]['group']})
                        return

        return result


def axis_alignment_from_legacy_align(align):
    if align in {uiconst.TOPLEFT,
     uiconst.BOTTOMLEFT,
     uiconst.CENTERLEFT,
     uiconst.TOLEFT}:
        return AxisAlignment.START
    elif align in {uiconst.TOPRIGHT,
     uiconst.BOTTOMRIGHT,
     uiconst.CENTERRIGHT,
     uiconst.TORIGHT}:
        return AxisAlignment.END
    elif align in {uiconst.CENTER, uiconst.CENTERTOP, uiconst.CENTERBOTTOM}:
        return AxisAlignment.CENTER
    else:
        return AxisAlignment.CENTER


class FormWnd(Container):
    __guid__ = 'xtriui.FormWnd'

    def _OnClose(self):
        Container._OnClose(self)
        windowKeys = self.sr.panels.keys()
        for key in windowKeys:
            if not self.sr.panels.has_key(key):
                continue
            wnd = self.sr.panels[key]
            del self.sr.panels[key]
            if wnd is not None and not wnd.destroyed:
                wnd.Close()

    def ShowPanel(self, panelkey):
        for key in self.sr.panels:
            self.sr.panels[key].state = uiconst.UI_HIDDEN

        self.sr.panels[panelkey].state = uiconst.UI_NORMAL

    def OnCheckboxChange(self, sender, *args):
        if sender.data.has_key('callback'):
            sender.data['callback'](sender)
        if sender.data.has_key('showpanel') and self.sr.panels.has_key(sender.data['showpanel']):
            self.ShowPanel(sender.data['showpanel'])

    def OnChange(self, *args):
        pass
