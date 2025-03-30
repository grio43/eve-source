#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\templateSavingUtil.py
import codecs
import logging
import os
import blue
import localization
from bannedwords.client import bannedwords
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate
from carbonui import Align, uiconst, TextBody
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.checkbox import Checkbox
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.planet.colonyTemplate import ColonyTemplate
from eve.client.script.ui.shared.planet.planetUtil import IsSerenity
from localization import GetByLabel

class ConfirmExportWnd(Window):
    default_minSize = (480, 240)
    default_fixedWidth = 480
    default_fixedHeight = 200
    default_captionLabelPath = 'UI/PI/SaveNewTemplate'
    default_windowID = 'comfirmPIexport'

    def ApplyAttributes(self, attributes):
        super(ConfirmExportWnd, self).ApplyAttributes(attributes)
        defaultNote = attributes.defaultNote
        captionPath = attributes.captionPath
        okPath = attributes.okPath
        self.MakeUnResizeable()
        self.result = None
        self.btnGroup = ButtonGroup(parent=self.content, align=Align.TOBOTTOM, button_size_mode=ButtonSizeMode.STRETCH)
        self.innerCont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, callback=self._UpdateWindowHeight)
        self.SetCaption(GetByLabel(captionPath))
        self.btnGroup.AddButton(GetByLabel(okPath), self.ClickOK)
        self.btnGroup.AddButton(GetByLabel('UI/Common/Buttons/Cancel'), self.Close)
        TextBody(parent=self.innerCont, align=Align.TOTOP, text=GetByLabel('UI/PI/EnterTemplateName'), top=8)
        self.editField = SingleLineEditText(parent=self.innerCont, maxLength=200, setvalue=defaultNote, align=Align.TOTOP, top=2, OnReturn=self.ClickOK)
        if IsSerenity():
            self.cb = Checkbox(parent=self.innerCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/PI/DoNotIncludeCmdCtr'), top=2)
        else:
            self.cb = None
        self._UpdateWindowHeight()

    def _UpdateWindowHeight(self):
        btnTopPadding = 12
        height = self.innerCont.height + self.btnGroup.height + btnTopPadding
        _, height = self.GetWindowSizeForContentSize(height=height)
        self.SetFixedHeight(height)

    def ClickOK(self, *args):
        note = StripTags(self.editField.GetValue())
        if self.cb:
            includeCmdCtr = not self.cb.GetValue()
        else:
            includeCmdCtr = False
        self.result = {'note': note,
         'includeCmdCtr': includeCmdCtr}
        self.SetModalResult(1)


def GetDefaultStoragePath():
    return os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'PlanetaryInteractionTemplates')


def SaveToLocalFile(newJSON, filename = None, encoding = None):
    try:
        ct = ColonyTemplate(newJSON, '')
        bannedwords.check_words_allowed(ct.description)
    except UserError as e:
        raise
    except Exception as e:
        logging.exception('PI Templates: Error while saving file')
        uicore.Message('CustomError', {'error': GetByLabel('UI/PI/ErrorSavingToFile')})
        return False

    try:
        defaultStoragePath = GetDefaultStoragePath()
        if filename is None:
            dateStr = str(FmtDate(blue.os.GetWallclockTime(), 'll').replace(':', ''))
            filename = u'{0}.json'.format(os.path.join(defaultStoragePath, dateStr))
        if not os.path.exists(defaultStoragePath):
            os.makedirs(defaultStoragePath)
        if encoding is None:
            outfile = codecs.open(filename, 'w')
        else:
            outfile = codecs.open(filename, 'w', encoding=encoding)
        outfile.write(newJSON)
        ShowQuickMessage(GetByLabel('UI/PI/WrittenToFile', path=filename))
    except Exception as e:
        logging.exception('PI Templates: Error while saving file')
        uicore.Message('CustomError', {'error': GetByLabel('UI/PI/ErrorSavingToFile')})
        return False

    sm.ScatterEvent('OnPITemplatesUpdated')
    ShowQuickMessage(GetByLabel('UI/PI/SavedToLocalSuccess'))
    return True
