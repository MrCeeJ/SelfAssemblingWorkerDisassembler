from SelfAssemblingWorkerDisassembler.auto_gateways import AutoGateways
from SelfAssemblingWorkerDisassembler.auto_stargates import AutoStargates
from SelfAssemblingWorkerDisassembler.dodge_ramp_attack import DodgeRampAttack
from SelfAssemblingWorkerDisassembler.oracle_ninjas import OracleNinjas
from SelfAssemblingWorkerDisassembler.stay_at_home_sentry import StayAtHomeSentry
from sc2 import UnitTypeId, Race
from sc2.ids.upgrade_id import UpgradeId
from sharpy.interfaces import IZoneManager
from sharpy.knowledges import KnowledgeBot
from sharpy.plans import BuildOrder, Step, SequentialList
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *


def get_two_gate_stalker_plan():
    return [
        Step(Supply(11),
             GridBuilding(UnitTypeId.PYLON, 1, priority=True), None),
        Step(UnitReady(UnitTypeId.PYLON, 1),
             GridBuilding(UnitTypeId.GATEWAY, 1, priority=True)),
        Step(UnitReady(UnitTypeId.GATEWAY, 1),
             GridBuilding(UnitTypeId.CYBERNETICSCORE, 1, priority=True)),
        Step(UnitReady(UnitTypeId.GATEWAY, 0.8),
             GridBuilding(UnitTypeId.GATEWAY, 2)),
        Step(UnitExists(UnitTypeId.GATEWAY, 1, include_not_ready=True),
             BuildGas(1), None),
        Step(UnitExists(UnitTypeId.GATEWAY, 2, include_not_ready=True),
             BuildGas(2), None),
        Step(UnitExists(UnitTypeId.GATEWAY, 1),
             GridBuilding(UnitTypeId.PYLON, 2)),
        Step(UnitReady(UnitTypeId.CYBERNETICSCORE, 1),
             GridBuilding(UnitTypeId.STARGATE, 1, priority=True)),
        Step(UnitReady(UnitTypeId.STARGATE, 0.5),
             Tech(UpgradeId.WARPGATERESEARCH)),
        # Step(UnitReady(UnitTypeId.STARGATE, 0.5),
        #      Expand(1, priority=True)),
        Step(Supply(36),
             GridBuilding(UnitTypeId.PYLON, 3)),
        Step(UnitReady(UnitTypeId.NEXUS, 2),
             GridBuilding(UnitTypeId.TWILIGHTCOUNCIL, 1)),
        Step(UnitReady(UnitTypeId.NEXUS, 2),
             GridBuilding(UnitTypeId.FORGE, 1)),
        Step(UnitReady(UnitTypeId.NEXUS, 3),
             GridBuilding(UnitTypeId.FLEETBEACON, 1)),
    ]


def get_one_base_plan():
    # Oracle Rush build order
    one_base_start = [
        Step(Supply(11),
             GridBuilding(UnitTypeId.PYLON, 1, priority=True), None),
        Step(UnitReady(UnitTypeId.PYLON, 1),
             GridBuilding(UnitTypeId.GATEWAY, 1, priority=True)),
        Step(UnitExists(UnitTypeId.GATEWAY, 1, include_pending=True),
             BuildGas(2), None),
        Step(UnitReady(UnitTypeId.GATEWAY, 1),
             GridBuilding(UnitTypeId.CYBERNETICSCORE, 1, priority=True)),
        # Step(UnitExists(UnitTypeId.CYBERNETICSCORE, 1, include_pending=True),
        #      BuildGas(2), None),
        Step(Supply(22),
             GridBuilding(UnitTypeId.PYLON, 2)),
        Step(UnitReady(UnitTypeId.CYBERNETICSCORE, 1),
             GridBuilding(UnitTypeId.STARGATE, 1, priority=True)),
        Step(UnitExists(UnitTypeId.STARGATE, include_pending=True),
             Tech(UpgradeId.WARPGATERESEARCH)),
        Step(UnitExists(UnitTypeId.STARGATE, include_pending=True),
             Expand(1, priority=True)),
        # Step(UnitReady(UnitTypeId.STARGATE, 1), BuildGas(3), None),
        Step(Supply(36),
             GridBuilding(UnitTypeId.PYLON, 3)),
        Step(UnitReady(UnitTypeId.PROBE, 50),
             Expand(2, priority=True)),
        Step(UnitReady(UnitTypeId.PROBE, 70),
             Expand(3, priority=True)),
        Step(UnitReady(UnitTypeId.NEXUS, 2),
             GridBuilding(UnitTypeId.FORGE, 1, priority=True)),
        Step(UnitReady(UnitTypeId.FORGE, 1),
             GridBuilding(UnitTypeId.TWILIGHTCOUNCIL, 1, priority=True),
             TechReady(UpgradeId.PROTOSSSHIELDSLEVEL1)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL, 1),
             GridBuilding(UnitTypeId.FORGE, 2, priority=True)),
        Step(UnitReady(UnitTypeId.STARGATE, 1),
             GridBuilding(UnitTypeId.FLEETBEACON, 1, priority=True),
             TechReady(UpgradeId.PROTOSSAIRARMORSLEVEL1, percentage=33)),
    ]
    return []


def get_gasless_expand_plan():
    # Greedy build order
    gasless_start_plan = [
        Step(Supply(12), GridBuilding(UnitTypeId.PYLON, 1), None),
        Step(UnitReady(UnitTypeId.PYLON, 1), GridBuilding(UnitTypeId.GATEWAY, 1)),
        Step(UnitReady(UnitTypeId.GATEWAY, 1), BuildGas(1), None),
        Step(UnitReady(UnitTypeId.GATEWAY, 1), GridBuilding(UnitTypeId.CYBERNETICSCORE, 1)),
        Step(UnitReady(UnitTypeId.PYLON, 1), Expand(2)),
        Step(UnitReady(UnitTypeId.CYBERNETICSCORE, 1), BuildGas(2), None),
        Step(Supply(22), GridBuilding(UnitTypeId.PYLON, 2)),
        Step(UnitReady(UnitTypeId.CYBERNETICSCORE, 1), GridBuilding(UnitTypeId.STARGATE, 1)),
        Step(UnitReady(UnitTypeId.STARGATE, 1), BuildGas(3), None),
        Step(Supply(36), GridBuilding(UnitTypeId.PYLON, 3)),
        Step(UnitReady(UnitTypeId.NEXUS, 3), BuildGas(4)),
        Step(UnitReady(UnitTypeId.NEXUS, 4), BuildGas(8)),
        Step(UnitReady(UnitTypeId.ORACLE, 2), GridBuilding(UnitTypeId.FORGE, 1)),
        Step(UnitReady(UnitTypeId.FORGE, 1), GridBuilding(UnitTypeId.TWILIGHTCOUNCIL, 1)),
        # Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL, 1), GridBuilding(UnitTypeId.FORGE, 2)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL, 1), GridBuilding(UnitTypeId.FLEETBEACON, 1)),
    ]
    return []


def get_chrono_plan():
    return [
        Step(
            UnitReady(UnitTypeId.PYLON, 0.6),
            ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS),
            skip=UnitExists(UnitTypeId.PROBE, 26),
        ),
        Step(
            None,
            ChronoUnit(UnitTypeId.ORACLE, UnitTypeId.STARGATE),
            skip=UnitExists(UnitTypeId.ORACLE, 5, include_pending=True),
            skip_until=UnitExists(UnitTypeId.STARGATE),
        ),
        Step(
            None,
            ChronoUnit(UnitTypeId.VOIDRAY, UnitTypeId.STARGATE),
            skip=UnitExists(UnitTypeId.ORACLE, 5, include_pending=True),
        ),
        Step(
            None,
            ChronoUnit(UnitTypeId.TEMPEST, UnitTypeId.STARGATE),
            skip_until=UnitExists(UnitTypeId.STARGATE),
        ),
        Step(
            None,
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY),
            skip_until=UnitExists(UnitTypeId.GATEWAY),
            skip=UnitExists(UnitTypeId.WARPGATE)
        ),
        Step(
            UnitExists(UnitTypeId.WARPGATE),
            ChronoBuilding(UnitTypeId.WARPGATE),
            skip=UnitExists(UnitTypeId.ORACLE),
        )
    ]


def get_probes_plan():
    return [
        Step(
            UnitExists(UnitTypeId.NEXUS, 1),
            ProtossUnit(UnitTypeId.PROBE, 26),
        ),
        Step(
            UnitExists(UnitTypeId.ORACLE, 1),
            ProtossUnit(UnitTypeId.PROBE, 28),
        ),
        Step(
            UnitExists(UnitTypeId.NEXUS, 2),
            ProtossUnit(UnitTypeId.PROBE, 44),
        ),
        Step(
            UnitExists(UnitTypeId.NEXUS, 3),
            ProtossUnit(UnitTypeId.PROBE, 60),
        )
    ]


def get_expansion_plan():
    return [
        Step(
            UnitExists(UnitTypeId.PROBE, 22),
            Expand(2)
        ),
        Step(
            UnitExists(UnitTypeId.PROBE, 40),
            Expand(3)
        ),
        Step(
            UnitExists(UnitTypeId.PROBE, 55),
            Expand(4)
        )
    ]


def get_gas_plan():
    return [
        Step(
            UnitExists(UnitTypeId.PROBE, 30),
            BuildGas(3)
        ),
        Step(
            UnitExists(UnitTypeId.PROBE, 35),
            BuildGas(4)
        ),
        Step(
            UnitExists(UnitTypeId.PROBE, 40),
            BuildGas(5)
        ),
        Step(
            UnitExists(UnitTypeId.PROBE, 45),
            BuildGas(6)
        )
    ]


def get_unit_plan():
    return BuildOrder(
        ProtossUnit(UnitTypeId.ORACLE, 3, priority=True),
        ProtossUnit(UnitTypeId.ZEALOT, 1),
        ProtossUnit(UnitTypeId.SENTRY, 1),
        ProtossUnit(UnitTypeId.STALKER, 100),
        Step(UnitExists(UnitTypeId.ORACLE, 3), ProtossUnit(UnitTypeId.VOIDRAY, 3, priority=True)),
        Step(UnitExists(UnitTypeId.VOIDRAY, 3), ProtossUnit(UnitTypeId.TEMPEST, 3, priority=True)),
        Step(UnitExists(UnitTypeId.SENTRY, 1), StayAtHomeSentry()),
    )


def get_scaling_plan(self):
    # Initial build complete, starting dynamic
    return BuildOrder(
        AutoPylon(),
        # Step(RequireCustom(expand_function(self)), Expand(2)),
        # AutoExpand(),  # wtf? why not working?
        # AutoGas(),
        AutoGateways(),
        AutoStargates(),
    )


def get_upgrade_plan():
    return BuildOrder(
        Step(UnitExists(UnitTypeId.ORACLE), Tech(UpgradeId.PROTOSSSHIELDSLEVEL1)),
        Step(UnitExists(UnitTypeId.ORACLE), Tech(UpgradeId.PROTOSSAIRARMORSLEVEL1)),
        Step(UnitExists(UnitTypeId.ORACLE), Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.BLINKTECH)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSSHIELDSLEVEL2)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSAIRARMORSLEVEL2)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSSHIELDSLEVEL3)),
        Step(UnitExists(UnitTypeId.ORACLE), Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL1)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSAIRARMORSLEVEL3)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSAIRWEAPONSLEVEL1)),
        Step(UnitReady(UnitTypeId.FLEETBEACON), Tech(UpgradeId.PROTOSSAIRWEAPONSLEVEL2)),
        Step(UnitReady(UnitTypeId.FLEETBEACON), Tech(UpgradeId.PROTOSSAIRWEAPONSLEVEL3)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL2)),
        Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL), Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL3)),
    )


#
# def expand_function(self, ai):
#     return lambda k: self.zone_manager.own_main_zone.minerals_running_low


class SelfAssemblingWorkerDisassembler(KnowledgeBot):
    tactic_index: int
    zone_manager: IZoneManager

    def __init__(self, build_name: str = "default"):
        super().__init__("")
        self.build_name = build_name

    async def on_start(self):
        await super().on_start()
        self.zone_manager = self.knowledge.get_required_manager(IZoneManager)

    async def pre_step_execute(self):
        if self.tactic_index != 1 and self.time < 5 * 60:
            self.knowledge.gather_point = self.zone_manager.expansion_zones[-2].gather_point

    async def create_plan(self) -> BuildOrder:
        if self.build_name == "default":
            self.tactic_index = 0  # select_build_index(self.knowledge, "build.oracles", 0, 2)
        else:
            self.tactic_index = int(self.build_name)
        self.building_solver.wall_type = 2  # WallType.ProtossMainZerg
        chrono_plan = get_chrono_plan()
        unit_plan = get_unit_plan()
        scaling_plan = get_scaling_plan(self)
        upgrade_plan = get_upgrade_plan()
        probes_plan = get_probes_plan()
        expansion_plan = get_expansion_plan()
        gas_plan = get_gas_plan()
        if self.tactic_index == 0:
            self.knowledge.print("Two gate stalker", "Build")
            opener = get_two_gate_stalker_plan()
        elif self.tactic_index == 1:
            self.knowledge.print("One Base Oracles", "Build")
            opener = get_one_base_plan()
        elif self.tactic_index == 2:
            self.knowledge.print("Gassless Expand", "Build")
            opener = get_gasless_expand_plan()
        else:
            opener = get_two_gate_stalker_plan()
        return BuildOrder(
            BuildOrder(
                probes_plan,
                opener,
                chrono_plan,
                unit_plan,
                scaling_plan,
                upgrade_plan,
                expansion_plan,
                gas_plan,
            ),
            SequentialList(
                PlanZoneDefense(),
                RestorePower(),
                DistributeWorkers(),
                PlanZoneGather(),
                OracleNinjas(self.game_info),
                Step(UnitReady(UnitTypeId.ORACLE, 0.5), PlanZoneAttack(3)),
                Step(None, DodgeRampAttack(self.townhalls.amount * 10)),
                PlanFinishEnemy(),
            ),
        )


class LadderBot(SelfAssemblingWorkerDisassembler):
    @property
    def my_race(self):
        return Race.Protoss
