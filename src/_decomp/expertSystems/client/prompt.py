#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\prompt.py
import eveformat
import localization
from carbonui import uiconst
from carbonui.uicore import uicore
from expertSystems.client.const import Color

def prompt_remove_expert_system(expert_system_type_id):
    response = uicore.Message('CustomQuestion', {'header': localization.GetByLabel('UI/ExpertSystem/RemovePromptTitle'),
     'question': u'{}<br><br>{}'.format(localization.GetByLabel('UI/ExpertSystem/RemovePromptBody', expert_system=expert_system_type_id), eveformat.color(localization.GetByLabel('UI/ExpertSystem/RemoveWarning'), color=Color.warning))}, buttons=uiconst.YESNO)
    return response == uiconst.ID_YES
