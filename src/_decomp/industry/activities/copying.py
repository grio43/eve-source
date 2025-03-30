#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\activities\copying.py
import industry

class Copying(industry.Activity):
    REQUIRES_ORIGINAL = True
    MAX_RUNS = 500

    def job_time(self, job):
        return self.time * float(job.licensedRuns or 1) * job.runs

    def job_cost(self, job):
        return job.prices.get(job.blueprint.blueprintTypeID, 0) * industry.COST_PERCENTAGE * float(job.licensedRuns or 0) * float(job.runs)

    def job_material_runs(self, job):
        return job.runs * job.licensedRuns

    def job_output_products(self, job):
        product = industry.Blueprint(blueprintTypeID=job.blueprint.blueprintTypeID, timeEfficiency=job.blueprint.timeEfficiency, materialEfficiency=job.blueprint.materialEfficiency, runsRemaining=job.licensedRuns, quantity=job.runs, original=False)
        return [product]

    def job_output_extras(self, job):
        return [job.blueprint]
