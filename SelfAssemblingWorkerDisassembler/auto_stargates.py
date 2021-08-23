from math import ceil

from sharpy.plans.acts import GridBuilding
from sc2 import UnitTypeId


class AutoStargates(GridBuilding):
    """Builds barracks automatically when needed based on left over minerals or command centre count."""

    def __init__(self):
        self.TYPE = UnitTypeId.STARGATE
        super().__init__(self.TYPE, 0)

    async def execute(self):
        base_count = await self.base_count_calc()
        worker_count = await self.worker_count_calc()
        self.to_count = min(base_count, worker_count)
        return await super().execute()

    # Limit the number of gateways based on worker count
    async def worker_count_calc(self) -> int:
        worker_count = self.cache.own(UnitTypeId.PROBE).amount
        if worker_count < 30:
            return 0
        elif worker_count < 60:
            return 1
        elif worker_count < 90:
            return 2
        elif worker_count < 120:
            return 3
        else:
            return ceil(worker_count / 30)

    # Limit the number of stargates to 1 per base
    async def base_count_calc(self) -> int:
        townhall_count = self.cache.own(
            {UnitTypeId.NEXUS}
        ).amount
        return townhall_count * 1

    async def mineral_dump(self) -> int:
        building_count = self.cache.own(
            {self.TYPE}).amount
        mineral_count = self.ai.minerals
        vespene_count = self.ai.vespene

        if mineral_count >= 600 and vespene_count >= 400:
            self.print(f"Resources too high, requesting more Stargates: {mineral_count} / {vespene_count}")
            self.to_count = building_count + 1
