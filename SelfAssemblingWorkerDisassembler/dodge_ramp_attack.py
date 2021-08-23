from sc2.position import Point2
from sharpy.interfaces.combat_manager import MoveType
from sharpy.plans.tactics import PlanZoneAttack


class DodgeRampAttack(PlanZoneAttack):
    async def execute(self) -> bool:
        base_ramp = self.zone_manager.expansion_zones[-1].ramp
        for effect in self.ai.state.effects:
            if effect.id != "FORCEFIELD":
                continue
            pos: Point2 = base_ramp.bottom_center
            for epos in effect.positions:
                if pos.distance_to_point2(epos) < 5:
                    return await self.small_retreat()

        return await super().execute()

    async def small_retreat(self):
        attacking_units = self.roles.attacking_units
        natural = self.zone_manager.expansion_zones[-2]

        for unit in attacking_units:
            self.combat.add_unit(unit)

        self.combat.execute(natural.gather_point, MoveType.DefensiveRetreat)
        return False
