#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\mathtasks.py
from behaviors.tasks import Task
import geo2

class WriteVectorToBlackboard(Task):

    def OnEnter(self):
        x = self.attributes.x
        y = self.attributes.y
        z = self.attributes.z
        self.SendBlackboardValue(self.attributes.outputVectorAddress, (x, y, z))
        self.SetStatusToSuccess()


class AddToVectorInBlackboard(Task):

    def OnEnter(self):
        x = self.attributes.x
        y = self.attributes.y
        z = self.attributes.z
        input_vector = self.GetLastBlackboardValue(self.attributes.inputVectorAddress)
        output_vector = geo2.Vec3AddD(input_vector, (x, y, z))
        self.SendBlackboardValue(self.attributes.outputVectorAddress, output_vector)
        self.SetStatusToSuccess()


class AddVectorsInBlackboard(Task):

    def OnEnter(self):
        first_vector = self.GetLastBlackboardValue(self.attributes.firstVectorAddress)
        second_vector = self.GetLastBlackboardValue(self.attributes.secondVectorAddress)
        output_vector = geo2.Vec3AddD(first_vector, second_vector)
        self.SendBlackboardValue(self.attributes.outputVectorAddress, output_vector)
        self.SetStatusToSuccess()


class SubtractVectorsInBlackboard(Task):

    def OnEnter(self):
        first_vector = self.GetLastBlackboardValue(self.attributes.firstVectorAddress)
        second_vector = self.GetLastBlackboardValue(self.attributes.secondVectorAddress)
        output_vector = geo2.Vec3SubtractD(first_vector, second_vector)
        self.SendBlackboardValue(self.attributes.outputVectorAddress, output_vector)
        self.SetStatusToSuccess()
