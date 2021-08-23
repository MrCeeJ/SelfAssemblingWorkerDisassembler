from math import floor
from typing import List, Optional

from sc2 import UnitTypeId, AbilityId
from sc2.position import Point2
from sc2.unit import Unit
from sharpy.knowledges import Knowledge
from sharpy.managers.core.roles import UnitTask
from sharpy.plans.acts import *


class StayAtHomeSentry(ActBase):
    def __init__(self):
        super().__init__()
        self.sentry_tag: Optional[int] = None

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)

    async def execute(self) -> bool:
        sentry = self.get_sentry()
        if not sentry:
            return True
        else:
            await self.micro_sentry(sentry)
        return False

    async def micro_sentry(self, sentry):
        self.roles.set_task(UnitTask.Reserved, sentry)
        if sentry.energy < 75 or self.cache.own(UnitTypeId.ORACLE).amount < 1:
            return
        else:
            sentry(AbilityId.HALLUCINATION_ORACLE)

    def get_sentry(self) -> Optional[Unit]:
        if self.ai.time < 0 and self.sentry_tag:
            return None  # wait a while
        sentry = self.cache.by_tag(self.sentry_tag)
        if sentry:
            return sentry

        available_sentry = self.cache.own(UnitTypeId.SENTRY)
        if not available_sentry:
            return None

        sentry = available_sentry.closest_to(self.zone_manager.own_main_zone.center_location)
        self.sentry_tag = sentry.tag
        return sentry

