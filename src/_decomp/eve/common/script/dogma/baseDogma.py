#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\baseDogma.py
import carbon.common.script.sys.service as service
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsCharacter
from eveexceptions import UserError

class BaseDogma(service.Service):
    __guid__ = 'svc.baseDogma'

    def Run(self, *args):
        service.Service.Run(self, *args)

    def __init__(self):
        service.Service.__init__(self)

    def SkillCheck(self, env, arg1, arg2):
        dogmaLM = env.dogmaLM
        if IsCharacter(env.charID):
            dogmaLM.CheckSkillRequirementsForType(env.charID, env.itemTypeID, arg1)
        return 1

    def UserError(self, env, arg1, arg2):
        dogmaLM = env.dogmaLM
        moduleID = env.itemID
        args = {'moduleName': (const.UE_TYPEID, env.itemTypeID)}
        if arg1 == 'NotEnoughPower':
            args['moduleType'] = env.itemTypeID
            args['require'] = dogmaLM.GetAttributeValue(moduleID, const.attributePower)
            shipID = env.shipID
            powerOutput = dogmaLM.GetAttributeValue(shipID, const.attributePowerOutput)
            args['remaining'] = powerOutput - dogmaLM.GetAttributeValue(shipID, const.attributePowerLoad)
            args['total'] = powerOutput
        elif arg1 == 'NotEnoughCpu':
            args['require'] = dogmaLM.GetAttributeValue(moduleID, const.attributeCpu)
            shipID = env.shipID
            cpuOutput = dogmaLM.GetAttributeValue(shipID, const.attributeCpuOutput)
            args['remaining'] = cpuOutput - dogmaLM.GetAttributeValue(shipID, const.attributeCpuLoad)
            args['total'] = cpuOutput
            args['moduleType'] = env.itemTypeID
        raise UserError(arg1, args)
