#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\stateSetting.py
SETTING_OLD_FLAG_STATES_CONFIG_NAME = 'flagStates'
SETTING_OLD_BACKGROUND_STATES_CONFIG_NAME = 'backgroundStates'
SETTING_FLAG_STATES_CONFIG_NAME = 'flagStates2'
SETTING_BACKGROUND_STATES_CONFIG_NAME = 'backgroundStates2'
SETTING_OLD_FLAG_ORDER_CONFIG_NAME = 'flagOrder'
SETTING_OLD_BACKGROUND_ORDER_CONFIG_NAME = 'backgroundOrder'
SETTING_FLAG_ORDER_CONFIG_NAME = 'flagOrder2'
SETTING_BACKGROUND_ORDER_CONFIG_NAME = 'backgroundOrder2'
SETTING_NOT_PRESENT = -99
orderSettingNames = {'flag': SETTING_FLAG_ORDER_CONFIG_NAME,
 'background': SETTING_BACKGROUND_ORDER_CONFIG_NAME}
stateSettingNames = {'flag': SETTING_FLAG_STATES_CONFIG_NAME,
 'background': SETTING_BACKGROUND_STATES_CONFIG_NAME}

def GetOrderConfigName(where):
    return orderSettingNames.get(where, None)


def GetStateConfigName(where):
    return stateSettingNames.get(where, None)
