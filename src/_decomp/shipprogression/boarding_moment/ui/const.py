#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\const.py
from shipprogression.boarding_moment.ui.steps.attributes_step import AttributesStep
from shipprogression.boarding_moment.ui.steps.designer_step import DesignerStep
from shipprogression.boarding_moment.ui.steps.title_step import TitleStep
from shipprogression.boarding_moment.ui.steps.traits_step import TraitsStep
UI_MOMENT_TRAITS = [{'step': AttributesStep,
  'duration_offset': 1.7}, {'step': TraitsStep,
  'delay': 1.8,
  'duration_offset': 0.7}]
UI_MOMENT_DESIGNER = [{'step': DesignerStep,
  'duration_offset': 0.7}]
UI_MOMENT_TITLE = [{'step': TitleStep,
  'duration_offset': 0.7}]
