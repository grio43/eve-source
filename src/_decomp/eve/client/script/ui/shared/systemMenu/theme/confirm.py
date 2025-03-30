#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\confirm.py
import localization
from carbonui import uiconst
from carbonui.uicore import uicore
from utillib import KeyVal

def confirm_remove_custom_color_theme(theme):
    result = uicore.Message(msgkey='ConfirmDeleteCustomTheme', params={'theme_name': theme.name}, buttons=[KeyVal(id=uiconst.ID_YES, label=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/ConfirmDeleteTheme')), KeyVal(id=uiconst.ID_NO, label=localization.GetByLabel('UI/Common/Cancel'))], default=uiconst.ID_NO)
    return result == uiconst.ID_YES


def confirm_discard_unsaved_color_theme_changes():
    result = uicore.Message(msgkey='ConfirmDiscardUnsavedCustomThemeChanges', buttons=[KeyVal(id=uiconst.ID_YES, label=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/ConfirmDiscardChanges')), KeyVal(id=uiconst.ID_NO, label=localization.GetByLabel('UI/Common/Cancel'))], default=uiconst.ID_NO)
    return result == uiconst.ID_YES
