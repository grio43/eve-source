#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\slash_command.py
from carbon.common.script.util.commonutils import StripTags
from carbonui.uicore import uicore
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_LEGIONEER
ROLE_SLASH = ROLE_GML | ROLE_LEGIONEER

def handle_slash_command(text, channel_controller):
    command_lines = StripTags(text, ignoredTags=('br',)).split('<br>')
    for command_line in command_lines:
        try:
            slash_result = uicore.cmd.Execute(command_line)
            if slash_result is not None:
                sm.GetService('logger').AddText('slash result: %s' % slash_result, 'slash')
            elif text.startswith('/tutorial') and session and session.role & ROLE_GML:
                sm.GetService('tutorial').SlashCmd(command_line)
            elif text.startswith('/advantage') and session and session.role & ROLE_GML:
                sm.GetService('fwAdvantageSvc').HandleSlashCmd(command_line)
            elif sm.GetService('publicQaToolsClient').CommandAllowed(command_line):
                sm.GetService('publicQaToolsClient').SlashCmd(command_line)
            elif session and session.role & ROLE_SLASH:
                if command_line.lower().startswith('/mark'):
                    sm.StartService('logger').LogError('SLASHMARKER: ', (session.userid, session.charid), ': ', command_line)
                slashRes = sm.GetService('slash').SlashCmd(command_line)
                if slashRes is not None:
                    sm.GetService('logger').AddText('slash result: %s' % slashRes, 'slash')
            channel_controller.add_game_message(u'<color=green>slash: {}</color>'.format(command_line))
        except:
            channel_controller.add_game_message(u'<color=red>slash failed: {}</color>'.format(command_line))
            raise
