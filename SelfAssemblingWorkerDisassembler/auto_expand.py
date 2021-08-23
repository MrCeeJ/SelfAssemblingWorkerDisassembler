from math import ceil

from sharpy.plans.acts import Expand
from sc2 import UnitTypeId


class AutoExpand(Expand):
    """Builds bases automatically when needed based on current worker count."""

    def __init__(self):
        super().__init__(0)

    async def execute(self):
        stargates = self.get_count(UnitTypeId.STARGATE, False, include_not_ready=True)
        if stargates:
            new_count = await self.base_count_calc()
            if self.to_count is new_count:
                return False
            else:
                self.to_count = max(new_count, self.to_count)
                return await super().execute()
        else:
            self.to_count = 0
            return False

    async def base_count_calc(self) -> int:
        worker_count = self.cache.own(UnitTypeId.PROBE).amount
        target = 20
        if worker_count < target:
            return 1
        elif worker_count < 2 * target:
            return 2
        elif worker_count < 3 * target:
            return 3
        elif worker_count < 4 * target:
            return 4
        else:
            return ceil(worker_count / target)

#
#
# from math import ceil
#
# from sharpy.plans.acts import Expand
# from sc2 import UnitTypeId
#
#
# class AutoExpand(Expand):
#     """Builds bases automatically when needed based on current worker count."""
#
#     def __init__(self):
#         super().__init__(0)
#
#     async def execute(self):
#         new_count = await self.worker_count_calc()  # min(await self.worker_count_calc(), await self.supply_count_calc())
#         if self.to_count is new_count:
#             return False
#         else:
#             self.to_count = new_count
#             return await super().execute()
#
#     async def worker_count_calc(self) -> int:
#         worker_count = self.cache.own(UnitTypeId.PROBE).amount
#         if worker_count < 24:
#             return 0
#         elif worker_count < 48:
#             return 1
#         elif worker_count < 70:
#             return 2
#         else:
#             return ceil(worker_count / 24)
#
#     async def supply_count_calc(self) -> int:
#         supply_count = self.cache.own.
#         if supply_count < 40:
#             return 0
#         elif supply_count < 60:
#             return 1
#         elif supply_count < 80:
#             return 2
#         elif supply_count < 100:
#             return 3
#         else:
#             return ceil(supply_count / 20)
