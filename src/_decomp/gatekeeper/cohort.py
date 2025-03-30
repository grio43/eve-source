#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\gatekeeper\cohort.py


class Cohort(object):

    def __init__(self, cohortID, name, description):
        self.cohortID = cohortID
        self.cohortName = name
        self.description = description

    @staticmethod
    def FromFSDData(dataRow):
        return Cohort(cohortID=dataRow['cohortID'], name=dataRow['cohortName'], description=dataRow['description'])


class CohortGroup(object):

    def __init__(self, groupID, name, description, cohortList):
        self.cohortGroupID = groupID
        self.cohortGroupName = name
        self.description = description
        self.cohorts = []
        self.cohorts.extend(cohortList)

    @staticmethod
    def FromFSDData(dataRow):
        cohortList = []
        cohortData = dataRow['cohorts']
        for cohort in cohortData:
            cohortList.append(Cohort.FromFSDData(cohort))

        return CohortGroup(groupID=dataRow['cohortGroupID'], description=dataRow['description'], name=dataRow['cohortGroupName'], cohortList=cohortList)


class CohortLoader(object):

    def _LoadRawData(self):
        import fsd.schemas.binaryLoader as fsdBinaryLoader
        return fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/cohorts.static')

    def GetCohortGroupDictWithCohorts(self):
        data = self._LoadRawData()
        cohortGroupDict = {}
        for key, value in data.iteritems():
            group = CohortGroup.FromFSDData(value)
            cohortGroupDict[key] = group

        return cohortGroupDict

    def GetCohortDictionary(self):
        cohortGroups = self.GetCohortGroupDictWithCohorts()
        cohortDict = {}
        for group in cohortGroups.itervalues():
            for cohort in group.cohorts:
                cohortDict[cohort.cohortID] = cohort

        return cohortDict
