#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\activities\reaction.py
import industry

class Reaction(industry.Activity):
    REQUIRES_ORIGINAL = True

    def job_output_products(self, job):
        output = []
        for product in self.products:
            output.append(industry.Material(typeID=product.typeID, quantity=job.runs * (product.quantity or 1)))

        return output

    def job_cost(self, job):
        return job.prices.get(job.blueprint.blueprintTypeID, 0) * float(job.runs)
