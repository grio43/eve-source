#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\activities\research_material.py
import industry

class ResearchMaterial(industry.Activity):
    REQUIRES_ORIGINAL = True

    def blueprint_level(self, blueprint):
        return blueprint.materialEfficiency / industry.STEP_MATERIAL_EFFICIENCY

    def blueprint_levels(self):
        return [ self.time * industry.RESEARCH_TIMES[i] for i in range(industry.MAX_MATERIAL_EFFICIENCY / industry.STEP_MATERIAL_EFFICIENCY) ]

    def job_time(self, job):
        levels = self.blueprint_levels()
        current = self.blueprint_level(job.blueprint)
        return sum([ levels[min(current + i, len(levels) - 1)] for i in range(job.runs) ])

    def job_max_runs(self, job):
        return min(industry.Activity.job_max_runs(self, job), (industry.MAX_MATERIAL_EFFICIENCY - job.blueprint.materialEfficiency) / industry.STEP_MATERIAL_EFFICIENCY)

    def job_cost(self, job):
        return job.prices.get(job.blueprint.blueprintTypeID, 0) * industry.COST_PERCENTAGE * self.job_time(job) / float(self.time)

    def job_output_products(self, job):
        blueprint = job.blueprint.copy()
        blueprint.materialEfficiency = min(blueprint.materialEfficiency + industry.STEP_MATERIAL_EFFICIENCY * job.runs, industry.MAX_MATERIAL_EFFICIENCY)
        return [blueprint]

    def job_validate(self, job):
        max_level = len(self.blueprint_levels())
        current = self.blueprint_level(job.blueprint)
        if current < 0 or current >= max_level:
            job.add_error(industry.Error.RESEARCH_LIMIT, current, max_level)
