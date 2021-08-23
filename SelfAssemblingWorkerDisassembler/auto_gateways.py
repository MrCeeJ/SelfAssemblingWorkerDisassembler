from math import ceil

from sharpy.plans.acts import GridBuilding
from sc2 import UnitTypeId


class AutoGateways(GridBuilding):
    """Builds barracks automatically when needed based on left over minerals or command centre count."""

    def __init__(self):
        self.TYPE = UnitTypeId.GATEWAY
        super().__init__(self.TYPE, 0)

    async def execute(self):
        base_count = self.base_count_calc()
        worker_count = self.worker_count_calc()
        self.to_count = min(base_count, worker_count)
        self.mineral_dump()
        return await super().execute()

    # Limit the number of gateways based on worker count
    def worker_count_calc(self) -> int:
        worker_count = self.cache.own(UnitTypeId.PROBE).amount
        if worker_count < 20:
            return 1
        elif worker_count < 40:
            return 2
        elif worker_count < 50:
            return 5
        else:
            return ceil(worker_count / 10)

    # Limit the number of gateways to 2 per base
    def base_count_calc(self) -> int:
        townhall_count = self.cache.own(
            {UnitTypeId.NEXUS}
        ).amount
        return townhall_count * 2

    def mineral_dump(self) -> int:
        building_count = self.cache.own(
            {self.TYPE}).amount
        mineral_count = self.ai.minerals

        if mineral_count >= 750:
            self.print(f"Minerals too high, requesting more gateways {mineral_count}")
            self.to_count = building_count + 1
