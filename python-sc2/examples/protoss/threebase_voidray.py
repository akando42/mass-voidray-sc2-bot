import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import sc2
from sc2 import Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.ids.buff_id import BuffId
from sc2.player import Bot, Computer


class ThreebaseVoidrayBot(sc2.BotAI):
    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")

        if not self.townhalls.ready:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
            return
        else:
            nexus = self.townhalls.ready.random

        # If this random nexus is not idle and has not chrono buff, chrono it with one of the nexuses we have
        if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            nexuses = self.structures(UnitTypeId.NEXUS)
            abilities = await self.get_available_abilities(nexuses)
            for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                    loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                    break

        # If we have at least 5 void rays, attack closes enemy unit/building, or if none is visible: attack move towards enemy spawn
        if self.units(UnitTypeId.VOIDRAY).amount > 5:
            for vr in self.units(UnitTypeId.VOIDRAY):
                # Activate charge ability if the void ray just attacked
                if vr.weapon_cooldown > 0:
                    vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                # Choose target and attack, filter out invisible targets
                targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(vr)
                    vr.attack(target)
                else:
                    vr.attack(self.enemy_start_locations[0])

        # Distribute workers in gas and across bases
        await self.distribute_workers()

        # If we are low on supply, build pylon
        if (
            self.supply_left < 2
            and self.already_pending(UnitTypeId.PYLON) == 0
            or self.supply_used > 15
            and self.supply_left < 4
            and self.already_pending(UnitTypeId.PYLON) < 2
        ):
            # Always check if you can afford something before you build it
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)

        # Train probe on nexuses that are undersaturated (avoiding distribute workers functions)
        # if nexus.assigned_harvesters < nexus.ideal_harvesters and nexus.is_idle:
        if self.supply_workers + self.already_pending(UnitTypeId.PROBE) < self.townhalls.amount * 22 and nexus.is_idle:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)

        # If we have less than 3 nexuses and none pending yet, expand
        if self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) < 3:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()

        # Once we have a pylon completed
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.GATEWAY).ready:
                # If we have gateway completed, build cyber core
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    if (
                        self.can_afford(UnitTypeId.CYBERNETICSCORE)
                        and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                    ):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            else:
                # If we have no gateway, build gateway
                if self.can_afford(UnitTypeId.GATEWAY) and self.already_pending(UnitTypeId.GATEWAY) == 0:
                    await self.build(UnitTypeId.GATEWAY, near=pylon)

        # Build gas near completed nexuses once we have a cybercore (does not need to be completed
        if self.structures(UnitTypeId.CYBERNETICSCORE):
            for nexus in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break

                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break

                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                        worker.build(UnitTypeId.ASSIMILATOR, vg)
                        worker.stop(queue=True)

        # If we have less than 3  but at least 3 nexuses, build stargate
        if self.structures(UnitTypeId.PYLON).ready and self.structures(UnitTypeId.CYBERNETICSCORE).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if (
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) >= 3
                and self.structures(UnitTypeId.STARGATE).ready.amount + self.already_pending(UnitTypeId.STARGATE) < 3
            ):
                if self.can_afford(UnitTypeId.STARGATE):
                    await self.build(UnitTypeId.STARGATE, near=pylon)

        # Save up for expansions, loop over idle completed stargates and queue void ray if we can afford
        if self.townhalls.amount >= 3:
            for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                if self.can_afford(UnitTypeId.VOIDRAY):
                    sg.train(UnitTypeId.VOIDRAY)


def main():
    sc2.run_game(
        sc2.maps.get("(2)CatalystLE"),
        [Bot(Race.Protoss, ThreebaseVoidrayBot()), Computer(Race.Protoss, Difficulty.Easy)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
