import sc2
# from sc2.unit import Unit
# from sc2.units import Units
from sc2 import BotAI, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2, Point3


class CompetitiveBot(BotAI):
    NAME: str = "VoidRay"
    """This bot's name"""
    RACE: Race = Race.Protoss
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    def __init__(self):
        ### Initiating built in Classes
        sc2.BotAI.__init__(self)

    async def on_start(self):
        print("Game started")

    async def on_step(self, iteration):
        nexus = self.townhalls.ready.random
        # Assign tasks to workers 
        await self.distribute_workers()
       
        await self.get_coordinates(nexus)

        # Train new workers
        await self.train_workers(nexus)

        # Build More Supply Sources
        await self.add_new_supply(nexus)

        # Build Gateways
        await self.build_gateway(nexus)

        # Build Assimilators 
        await self.add_more_gas(nexus)

        # Build Infantries
        await self.train_infantries(UnitTypeId.ZEALOT)

        # Build Cybernetics Core
        await self.build_cybernetics_core(nexus)

       
        # Build Stargates
        await self.build_stargates(nexus)

        # Build VoidRays
        await self.manufacture_voidrays(UnitTypeId.VOIDRAY)

        # Attacks

    async def train_infantries(self, UnitType):
        for GW in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.can_afford(UnitType) and self.units(UnitType).amount < 9 :
                GW.train(UnitType)
    
        if self.units(UnitTypeId.VOIDRAY).amount > 5: 
            for unit in self.units(UnitType).ready.idle:
                targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(unit)
                    unit.attack(target)
                else:
                    unit.attack(self.enemy_start_locations[0])
               
    async def manufacture_voidrays(self, UnitType):
        for SG in self.structures(UnitTypeId.STARGATE).ready.idle:
            if self.can_afford(UnitType):
                SG.train(UnitType)

        if self.units(UnitType).amount > 5:
            for unit in self.units(UnitType).ready.idle:
                if unit.weapon_cooldown > 0:
                    unit(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(unit)
                    unit.attack(target)
                else:
                    #unit.attack(self.enemy_start_locations[0])
                    unit.attack(self.enemy_start_locations[0])

    async def get_coordinates(self, nexus):
        NSPs = self.game_info.map_ramps
        print("There are ", len(NSPs), "RAMP in the Map")
        print("The Closet RAMP position is:\n", self.main_base_ramp)

        print(
            "Our starting position: \n", 
            "X:", nexus.position3d.x,"\n", 
            "Y:", nexus.position3d.y,"\n",  
            "Elevation:",nexus.position3d.z, "\n"
        )

    # CONSTANTLY ADDING MORE WORKERS
    async def train_workers(self, nexus):
        if (
            self.can_afford(UnitTypeId.PROBE)
            and nexus.is_idle
            and self.workers.amount < self.townhalls.amount * 22
        ):
            nexus.train(UnitTypeId.PROBE)     

    # CONSTANTLY ADD MORE SUPPLIES UNTIL REACHING LIMITS
    async def add_new_supply(self, nexus):
        if (self.supply_left < 4 and self.already_pending(UnitTypeId.PYLON) == 0):
            if self.can_afford(UnitTypeId.PYLON):
                if self.supply_used > 16:
                    await self.build(UnitTypeId.PYLON, near=nexus.position.towards(self.main_base_ramp.barracks_correct_placement,3))
                else:
                    await self.build(
                        UnitTypeId.PYLON, 
                        Point2((
                            self.main_base_ramp.top_center.x + 3,
                            self.main_base_ramp.top_center.y + 3,
                        )))

    # ADD more Gas 
    async def add_more_gas(self, nexus):
        vgs = self.vespene_geyser.closer_than(15, nexus)
        for vg in vgs:
            if self.can_afford(UnitTypeId.ASSIMILATOR):
                await self.build(UnitTypeId.ASSIMILATOR, vg)
                    
    # Build Infantry Training Buildings
    async def build_gateway(self, nexus):
        if not self.structures(UnitTypeId.GATEWAY):
            if self.can_afford(UnitTypeId.GATEWAY) and self.already_pending(UnitTypeId.GATEWAY) == 0:
                await self.build(UnitTypeId.GATEWAY, self.main_base_ramp.barracks_correct_placement)

    # Build Cybernetics Core to unlock Level 2 Building        
    async def build_cybernetics_core(self, nexus):
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.can_afford(UpgradeId.PROTOSSAIRARMORSLEVEL1)
            and self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL1) == 0
        ):
            ccore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            ccore.research(UpgradeId.PROTOSSAIRARMORSLEVEL1)

        if not self.structures(UnitTypeId.CYBERNETICSCORE):
            pylon_ready = self.structures(UnitTypeId.PYLON).ready
            if pylon_ready:
                if self.can_afford(UnitTypeId.CYBERNETICSCORE) and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0:
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon_ready.closest_to(nexus))

    # Build STARGATES to create AIR UNITS
    async def build_stargates(self, nexus):
        if self.can_afford(UnitTypeId.STARGATE) and self.structures(UnitTypeId.STARGATE).amount < 3:
            pylon_ready = self.structures(UnitTypeId.PYLON).ready
            await self.build(UnitTypeId.STARGATE, near=pylon_ready.closest_to(nexus))

    def on_end(self, result):
        print("Game ended.")
        # Do things here after the game ends



class ICBot(BotAI):
    NAME: str = "CaSink"
    """This bot's name"""
    RACE: Race = Race.Zerg