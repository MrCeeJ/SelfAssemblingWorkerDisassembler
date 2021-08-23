import random
from typing import Optional

from sc2.client import Client
from sc2.ids.buff_id import BuffId
from sc2.position import Point2, Point3
from sharpy.interfaces import ICombatManager, IZoneManager
from sharpy.knowledges import Knowledge
from sharpy.plans.acts import ActBase
from sc2 import UnitTypeId, AbilityId
from sc2.ids import buff_id
from sc2.unit import Unit
import math

from sharpy.managers.core.roles import UnitTask


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def get_unit_midpoint(units: []) -> Point2:
    total_x = 0
    total_y = 0
    count = 0
    for u in units:
        if u:
            total_x += u.position.x
            total_y += u.position.y
            count += 1
    return Point2((total_x / count, total_y / count))


def get_midpoint(points: []) -> Point2:
    total_x = 0
    total_y = 0
    count = 0
    for p in points:
        if p:
            total_x += p.x
            total_y += p.y
            count += 1
    return Point2((total_x / count, total_y / count))


def get_air_threat_range(e: Unit, buffer: float):
    threat_range = 0
    if e.can_attack_air:
        threat_range = e.air_range + buffer
        if e.type_id == UnitTypeId.CYCLONE:
            threat_range += 7  # Take account of lock on
        elif e.type_id == UnitTypeId.STALKER:
            threat_range += 1  # Take account of movement speed
        elif e.type_id == UnitTypeId.VIKING:
            threat_range += 1  # Take account of sight range advantage
        elif e.type_id == UnitTypeId.MISSILETURRET:
            threat_range += 1  # Something sneaking gong on here, range upgrade perhaps?
    elif e.type_id is UnitTypeId.BUNKER:
        threat_range = 7 + buffer
    return threat_range


class OracleNinjas(ActBase):
    combat: ICombatManager
    zone_manager: IZoneManager

    def __init__(self, info):
        # Oracle kiting parameters
        self.hallucination_safe_distance = 3
        self.hallucination_danger_distance: float = 2
        self.hallucination_snipe_distance = 3
        self.safe_distance = 4  # slow kiting below 4
        self.danger_distance: float = 3  # take damage at 2
        self.snipe_distance = 4
        self.risky_distance = 2
        self.arrived_distance = 1
        self.corner_distance = 4

        self.attack_target_map = {}
        self.move_target_map = {}
        self.direction_map = {}
        self.game_info = info
        self.target = None
        self.client = None
        super().__init__()

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)
        self.combat = knowledge.get_required_manager(ICombatManager)
        self.zone_manager = knowledge.get_required_manager(IZoneManager)
        self.client: Client = self.ai._client

    async def execute(self) -> bool:
        # Start Oracle Attack
        oracles = self.cache.own(UnitTypeId.ORACLE)
        for oracle in oracles:
            if oracle:
                busy = (
                        await self.locked_on(oracle) or
                        await self.no_energy(oracle) or
                        await self.snipe(oracle) or
                        await self.in_danger(oracle) or
                        await self.no_shields(oracle) or
                        await self.has_attack_target(oracle) or
                        await self.attack_workers(oracle) or
                        await self.attack_army(oracle) or
                        await self.attack_buildings(oracle) or
                        await self.arrived(oracle) or
                        await self.stuck(oracle) or
                        await self.explore(oracle))
                if busy:
                    self.roles.set_task(UnitTask.Reserved, oracle)
                else:
                    self.roles.clear_task(oracle)
        return True

    async def no_energy(self, o):
        if o.energy < 25:
            if o.buffs and BuffId.ORACLEWEAPON in o.buffs:
                return False
            else:
                self.set_home_target(o)
                await self.safe_move(o)
                return True
        return False

    async def locked_on(self, o):
        locked_on: bool = False
        msg = "LOCK_ON"
        if buff_id.LOCKON in o.buffs:
            locked_on = True
        nearest_cyclone: Optional[Unit] = None
        nearest_distance: float = 1000000
        cyclones = self.cache.enemy_in_range(o.position, 15).of_type(UnitTypeId.CYCLONE)
        if cyclones:
            for e in cyclones:
                dist = e.distance_to(o.position)
                if dist < nearest_distance:
                    nearest_cyclone = e
        if nearest_cyclone:
            new_x, new_y = rotate((o.position.x, o.position.y),
                                  (nearest_cyclone.position.x, nearest_cyclone.position.y),
                                  self.get_direction(o) * math.pi)

            away = Point2((new_x, new_y))
            if not (0 < new_x < self.game_info.map_size.width) or not (
                    0 < new_y < self.game_info.map_size.height):
                self.change_direction(o)
            self.client.debug_text_world(msg, o.position3d, None, 16)
            o.move(away)
        return locked_on

    async def in_danger(self, o):
        danger: bool = False
        msg = "DANGER"
        enemy_positions = []
        nearest_enemy: Optional[Unit] = None
        nearest_distance: float = 1000000
        enemies = self.cache.enemy_in_range(o.position, 15)
        if enemies:
            for e in enemies:
                threat_range = get_air_threat_range(e, self.get_danger_distance(o))
                if threat_range:
                    dist = e.distance_to(o.position)
                    enemy_positions.append(e.position)
                    if threat_range > dist:
                        danger = True
                        if dist < nearest_distance:
                            nearest_distance = dist
                            nearest_enemy = e

        if nearest_enemy:
            enemy_midpoint = get_midpoint(enemy_positions)
            weighted_midpoint = get_midpoint((enemy_midpoint, nearest_enemy.position))
            new_x, new_y = rotate((o.position.x, o.position.y),
                                  (weighted_midpoint.x, weighted_midpoint.y),
                                  self.get_direction(o) * 5 * math.pi / 6)
            away = Point2((new_x, new_y))
            if not (0 < new_x < self.game_info.map_size.width) or not (
                    0 < new_y < self.game_info.map_size.height):
                self.change_direction(o)
            self.client.debug_text_world(msg, o.position3d, None, 16)
            o.move(away)
        return danger

    async def no_shields(self, o):
        msg = "SHIELD"
        if o.shield_percentage < 0.5 and not o.is_hallucination:
            self.set_home_target(o)
            o(AbilityId.BEHAVIOR_PULSARBEAMOFF)
            await self.safe_move(o)
            self.client.debug_text_world(msg, o.position3d, None, 16)
            return True
        return False

    async def has_attack_target(self, o):
        msg = "TARGETED"
        target = self.get_attack_target(o)
        if target and target.health > 0 and target.distance_to(o) < 6:
            if target.distance_to(o) < 4:
                if o.weapon_cooldown == 0:
                    msg = "FOCUS"
                    o(AbilityId.BEHAVIOR_PULSARBEAMON)
                    o.smart(target)
            else:
                msg = "TRACK"
                o.move(target.position)
            self.client.debug_text_world(msg, o.position3d, None, 16)
            return True
        else:
            self.clear_attack_target(o)
            return False

    def set_attack_target(self, o: Unit, t: Unit):
        self.attack_target_map[o.tag] = t.tag

    def get_attack_target(self, o: Unit) -> Optional[Unit]:
        if o.tag in self.attack_target_map:
            target_tag = self.attack_target_map[o.tag]
            return self.cache.by_tag(target_tag)
        else:
            return None

    def clear_attack_target(self, o: Unit) -> Unit:
        if o.tag in self.attack_target_map:
            del self.attack_target_map[o.tag]

    async def attack_workers(self, o: Unit):
        msg = "SCV"
        enemy_workers = self.cache.enemy_in_range(o.position, 15).of_type(
            [UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.DRONE, UnitTypeId.MULE])
        if enemy_workers:
            # Targeting algo : target nearest, penalising gas miners, but lower the effective distance by missing health to prioritise low units
            def worker_sort(u: Unit):
                gas_factor = 1
                if u.is_carrying_vespene:
                    gas_factor = 2
                else:
                    gas = self.cache.enemy([UnitTypeId.ASSIMILATOR, UnitTypeId.REFINERY, UnitTypeId.EXTRACTOR])
                    if gas:
                        d_g = u.position.distance_to_closest(gas)
                        d_m = u.position.distance_to_closest(self.cache.mineral_fields)
                        if d_g < d_m:
                            gas_factor = 2
                risk_factor = 0
                enemies = self.cache.enemy_in_range(u.position, 10)
                if enemies:
                    for e in enemies:
                        if e.can_attack_air:
                            risk_factor = 10 - e.distance_to(u.position)
                return u.shield_health_percentage * (o.distance_to(u) + 3) * gas_factor + risk_factor

            if len(enemy_workers) > 1:
                enemy_workers.sort(key=worker_sort)
            target = enemy_workers.first
            self.set_attack_target(o, target)
            if o.distance_to(target) < 4:
                msg = "FIRE"
                o(AbilityId.BEHAVIOR_PULSARBEAMON)
                if o.weapon_cooldown == 0:
                    o.smart(target)
                else:
                    o.move(target.position)
            else:
                o.move(target.position)
            self.client.debug_text_world(msg, o.position3d, None, 16)
            return True
        return False

    async def attack_army(self, o):
        msg = "ARMY"
        if o.energy > 50:  # or (o.energy > 50 and BuffId.ORACLEWEAPON in o.buffs)
            enemy_targets = self.cache.enemy_in_range(o.position, 15).filter(
                lambda unit: not unit.is_flying and not unit.can_attack_air and not unit.is_structure)
            if enemy_targets.exists:
                enemy_targets.sort(key=lambda u: u.health * u.shield_health_percentage * o.distance_to(u))
                target = enemy_targets.first
                self.set_attack_target(o, target)
                if o.distance_to(target) < 4:
                    o(AbilityId.BEHAVIOR_PULSARBEAMON)
                    o.smart(target)
                else:
                    o.move(target)
                self.client.debug_text_world(msg, o.position3d, None, 16)
                return True
        else:
            o(AbilityId.BEHAVIOR_PULSARBEAMOFF)
        return False

    async def snipe(self, o: Unit):
        msg = "SNIPE"
        if o.shield_percentage > 0.5 and (o.energy > 25 or o.energy > 5 and o.has_buff(BuffId.ORACLEWEAPON)):
            snipe_targets = self.cache.enemy_in_range(o.position, 10).of_type([UnitTypeId.MARINE])
            if snipe_targets:
                if snipe_targets.amount == 1:
                    target = snipe_targets.first
                    mid = get_midpoint((o.position, target.position))
                    enemies = self.cache.enemy_in_range(target.position, 15)
                    if enemies:
                        for e in enemies:
                            threat_range = 0
                            if e.can_attack_air:
                                threat_range = e.air_range + self.get_snipe_distance(o)
                            elif e.type_id is UnitTypeId.BUNKER:
                                threat_range = 7 + self.get_snipe_distance(o)
                            if threat_range > 0:
                                if mid.distance_to(e) < threat_range:
                                    return False
                    self.set_attack_target(o, target)
                    if o.distance_to(target) < 4:
                        o(AbilityId.BEHAVIOR_PULSARBEAMON)
                        o.smart(target)
                    else:
                        o.move(target)
                    self.client.debug_text_world(msg, o.position3d, None, 16)
                    return True
        return False

    async def attack_buildings(self, o: Unit):
        msg = "BUILDINGS"
        if o.energy > 150:
            enemy_targets = self.cache.enemy_in_range(o.position, 15).filter(
                lambda unit: not unit.is_flying and not unit.can_attack_air)
            if enemy_targets.exists:
                enemy_targets.sort(key=lambda u: u.health * u.shield_health_percentage * o.distance_to(u))
                target = enemy_targets.first
                self.set_attack_target(o, target)
                if o.distance_to(target) < 4:
                    o(AbilityId.BEHAVIOR_PULSARBEAMON)
                o.smart(target)
                self.client.debug_text_world(msg, o.position3d, None, 16)
                o.move(target)
                return True
            else:
                o(AbilityId.BEHAVIOR_PULSARBEAMOFF)
        return False

    async def arrived(self, o):
        msg = "ARRIVED"
        destination = self.get_target(o)
        if destination.distance_to(o.position) < self.arrived_distance:
            self.client.debug_text_world(msg, o.position3d, None, 16)
            self.get_new_target(o)
        return False

    def get_direction(self, o):
        if o.tag not in self.direction_map:
            self.direction_map[o.tag] = random.sample({-1, 1}, 1)[0]
        return self.direction_map[o.tag]

    def change_direction(self, o):
        if o.tag not in self.direction_map:
            self.direction_map[o.tag] = random.sample({-1, 1}, 1)[0]
        else:
            self.direction_map[o.tag] *= -1
        return self.direction_map[o.tag]

    def set_home_target(self, o):
        midpoint = Point2((self.game_info.map_size.x / 2, self.game_info.map_size.y / 2))
        home_pos = self.zone_manager.own_main_zone.gather_point
        if midpoint:
            self.move_target_map[o.tag] = midpoint
        else:
            self.move_target_map[o.tag] = home_pos

    def get_new_target(self, o):
        if o.tag in self.move_target_map:
            del self.move_target_map[o.tag]
        return self.get_target(o)

    def get_target(self, o: Unit):
        if o.tag in self.move_target_map:
            return self.move_target_map[o.tag]
        else:
            target = self.find_target(o)
            self.move_target_map[o.tag] = target
            return target

    def find_target(self, o: Unit):
        if o.energy < 25:
            return self.zone_manager.own_main_zone.gather_point
        enemy_main_minerals = self.zone_manager.enemy_main_zone.mineral_line_center
        if o.distance_to(enemy_main_minerals) > self.arrived_distance:
            return enemy_main_minerals
        else:
            expansions = self.zone_manager.enemy_expansion_zones[:-3]  # should skip my bases
            zone = random.choice(expansions)
            return zone.mineral_line_center

    async def stuck(self, o):
        msg = "STUCK"
        buffer = self.corner_distance
        min_x = 0 + buffer
        max_x = self.game_info.map_size.width - buffer
        min_y = 0 + buffer
        max_y = self.game_info.map_size.height - buffer
        if (o.position.x < min_x or o.position.x > max_x) and (o.position.y < min_y or o.position.y > max_y):
            self.set_home_target(o)  # ESCAPE : Run halfway down the side furthest from the enemy
            self.client.debug_text_world(msg, o.position3d, None, 16)
            await self.safe_move(o)
            return True
        return False

    async def explore(self, o):
        target = self.get_target(o)
        # todo: midpoint distance < setting, get random loc
        return await self.safe_move(o)

    async def safe_move(self, o: Unit):
        msg = "MOVE"
        target = self.get_target(o)
        nearest_enemy: Optional[Unit] = None
        nearest_distance: float = 100000
        enemies = self.cache.enemy_in_range(o.position, 15)
        if enemies:
            for e in enemies:
                threat_range = get_air_threat_range(e, self.get_safe_distance(o))
                dist = e.distance_to(o.position)
                if threat_range > dist:
                    if dist < nearest_distance:
                        nearest_distance = dist
                        nearest_enemy = e
        if nearest_enemy:
            msg = "KITE"
            new_x, new_y = rotate((o.position.x, o.position.y),
                                  (nearest_enemy.position.x, nearest_enemy.position.y),
                                  self.get_direction(o) * 3 * math.pi / 4)
            if not (0 < new_x < self.game_info.map_size.width) or not (
                    0 < new_y < self.game_info.map_size.height):
                self.change_direction(o)
            new_point = Point2((new_x, new_y))
            self.client.debug_text_world(msg, o.position3d, None, 16)
            o.move(new_point)
        else:
            self.client.debug_text_world(msg, o.position3d, None, 16)
            o.move(target)
        return True

    # todo: use additional hunting
    async def get_remaining_target(self):
        target = await self.find_attack_position(self.ai)
        return target

    async def find_attack_position(self, ai):
        main_pos = self.zone_manager.own_main_zone.center_location

        target = random.choice(list(ai.expansion_locations_list))
        last_distance2 = target.distance_to(main_pos)
        target_known = False
        if ai.enemy_structures.exists:
            for building in ai.enemy_structures:
                if building.health > 0:
                    current_distance2 = target.distance_to(main_pos)
                    if not target_known or current_distance2 < last_distance2:
                        target = building.position
                        last_distance2 = current_distance2
                        target_known = True
        return target

    def get_danger_distance(self, o: Unit):
        if o.is_hallucination:
            return self.hallucination_danger_distance
        else:
            return self.danger_distance

    def get_snipe_distance(self, o: Unit):
        if o.is_hallucination:
            return self.hallucination_snipe_distance
        else:
            return self.snipe_distance

    def get_safe_distance(self, o: Unit):
        if o.is_hallucination:
            return self.hallucination_safe_distance
        else:
            return self.safe_distance