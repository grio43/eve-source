#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\evolution_value.py
from carbonui import Align, TextColor, TextHeadline
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from localization import GetByLabel

class BaseEvolutionValueContainer(ContainerAutoSize):
    default_clipChildren = True
    COLOR_VALUE_LABEL = TextColor.HIGHLIGHT
    LABEL_PATH_VALUE = None
    LABEL_PATH_MAXED_OUT = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/MaxedOut'

    def __init__(self, *args, **kwargs):
        super(BaseEvolutionValueContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._value = TextHeadline(name='value_label', parent=self, align=Align.TOTOP, color=self.COLOR_VALUE_LABEL)

    def _get_stage(self, controller):
        raise NotImplementedError('Must implement _get_stage in derived class')

    def _get_maxed_out(self, controller):
        raise NotImplementedError('Must implement _get_maxed_out in derived class')

    def _get_at_minimum(self, controller):
        raise NotImplementedError('Must implement _get_at_minimum in derived class')

    def load(self, controller):
        stage = self._get_stage(controller)
        is_at_minimum = self._get_at_minimum(controller)
        is_maxed_out = self._get_maxed_out(controller)
        if is_maxed_out:
            self._value.text = GetByLabel(self.LABEL_PATH_VALUE, level=stage - 1)
        elif is_at_minimum:
            self._value.text = GetByLabel(self.LABEL_PATH_VALUE, level=stage - 1)
        else:
            self._value.text = GetByLabel(self.LABEL_PATH_VALUE, level=stage - 1)
        self.SetSizeAutomatically()


class DevelopmentValueContainer(BaseEvolutionValueContainer):
    LABEL_PATH_VALUE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/DevelopmentValue'

    def _get_stage(self, controller):
        return controller.get_current_development_stage()

    def _get_maxed_out(self, controller):
        return controller.is_development_maxed_out()

    def _get_at_minimum(self, controller):
        return controller.is_development_at_minimum()


class AnarchyValueContainer(BaseEvolutionValueContainer):
    LABEL_PATH_VALUE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/AnarchyValue'

    def _get_stage(self, controller):
        return controller.get_current_anarchy_stage()

    def _get_maxed_out(self, controller):
        return controller.is_anarchy_maxed_out()

    def _get_at_minimum(self, controller):
        return controller.is_anarchy_at_minimum()
