from math import floor

from sharpy.plans.acts import Expand, BuildGas
from sc2 import UnitTypeId


class AutoGas(BuildGas):
    """Builds gas automatically, one base behind."""

    def __init__(self):
        super().__init__(0)

    async def execute(self):
        count = max(self.to_count, await self.dynamic_worker_count_calc())
        # max(await self.base_count_calc(), await self.worker_count_calc(), self.to_count)
        self.to_count = count
        return await super().execute()

    async def worker_count_calc(self) -> int:
        worker_count = self.cache.own(UnitTypeId.PROBE).amount
        if worker_count < 16:
            return 0
        else:
            return floor(worker_count / 11)

    async def dynamic_worker_count_calc(self) -> int:
        # Wait until we have a pylon
        pylon_count = self.cache.own(UnitTypeId.PYLON).amount
        gateway_count = self.cache.own(UnitTypeId.GATEWAY).amount
        if pylon_count is 0:
            return 0
        elif gateway_count is 0:
            return 1
        else:
            worker_count = self.cache.own(UnitTypeId.PROBE).amount
            base, remainder = divmod(worker_count, 22)
            base *= 2
            if remainder > 12:
                base += 2
            elif remainder > 6:
                base += 1
            return base

    async def base_count_calc(self) -> int:
        townhall_count = self.cache.own(UnitTypeId.NEXUS).amount
        if townhall_count < 2:
            return 0
        elif townhall_count is 2:
            return 2
        elif townhall_count is 3:
            return 4
        else:
            return townhall_count * 2
