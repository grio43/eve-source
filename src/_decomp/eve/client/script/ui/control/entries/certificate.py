#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\certificate.py
import localization
import utillib
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import uiconst
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.entries.skill import SkillTreeEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from eve.common.lib import appConst as const
from menu import MenuLabel
HEIGHT = HEIGHT_NORMAL

class CertEntry(ListGroup):
    __guid__ = 'listentry.CertEntry'
    isDragObject = True
    default_iconSize = 22

    def Startup(self, *args):
        super(CertEntry, self).Startup(*args)
        self.progressIcon = Sprite(name='progressIcon', parent=self, align=uiconst.CENTERRIGHT, pos=(2, 0, 16, 16), color=COLOR_SKILL_1)

    def Load(self, node):
        node.showlen = False
        self.certificate = node.certificate
        self.certID = self.certificate.certificateID
        self.level = node.level
        super(CertEntry, self).Load(node)
        self.sr.label.text = self.certificate.GetLabel(self.level)
        currLevel = self.certificate.GetLevel()
        if currLevel >= self.level:
            self.progressIcon.SetTexturePath('res:/ui/Texture/classes/Skills/SkillRequirementMet.png')
            self.progressIcon.hint = localization.GetByLabel('UI/InfoWindow/TrainedAndOfRequiredLevel')
        else:
            self.progressIcon.SetTexturePath('res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png')
            self.progressIcon.hint = localization.GetByLabel('UI/InfoWindow/NotTrained')

    def GetMenu(self):
        m = [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (self.certID,))]
        if session.role & ROLE_GML == ROLE_GML:
            m.append(('GM: Give all skills', self.GMGiveAllSkills, ()))
        return m

    def GMGiveAllSkills(self):
        skills = sm.GetService('certificates').GetCertificate(self.certID).SkillsByTypeAndLevel(self.level)
        for typeID, level in skills:
            if sm.GetService('skills').MySkillLevel(typeID) < level:
                sm.RemoteSvc('slash').SlashCmd('/giveskill me %s %s' % (typeID, level))

    def GetHeight(self, *args):
        node, _ = args
        node.height = HEIGHT
        return node.height

    def ShowInfo(self, *args):
        abstractinfo = utillib.KeyVal(certificateID=self.certID, level=self.level)
        sm.StartService('info').ShowInfo(const.typeCertificate, abstractinfo=abstractinfo)

    def OnDblClick(self, *args):
        self.ShowInfo()

    @staticmethod
    def GetSubContent(node, *args):
        skillSvc = sm.GetService('skills')
        filterAcquired = settings.user.ui.Get('masteries_filter_acquired', False)
        scrolllist = []
        skills = sm.GetService('certificates').GetCertificate(node.certificate.certificateID).SkillsByTypeAndLevel(node.level)
        for typeID, lvl in skills:
            try:
                if filterAcquired and skillSvc.GetSkill(typeID).trainedSkillLevel >= lvl:
                    continue
            except AttributeError:
                pass

            scrolllist.append(GetFromClass(SkillTreeEntry, {'line': True,
             'typeID': typeID,
             'lvl': lvl,
             'indent': 2,
             'hint': sm.GetService('skills').GetSkillToolTip(typeID, lvl)}))

        return scrolllist

    def GetHint(self):
        return self.certificate.GetDescription()

    def GetDragData(self, *args):
        return (self.sr.node,)

    def UpdateLabel(self):
        text = self.certificate.GetLabel(self.level)
        self.sr.label.text = text
        self.sr.node.label = text
