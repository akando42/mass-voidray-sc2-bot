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
        hatch: Unit = self.townhalls[0]

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
        print("Game ended. ", result)
        # Do things here after the game ends

class ICBot(BotAI):
    NAME: str = "CaSink"
    """This bot's name"""
    RACE: Race = Race.Zerg

    battlecruisers_count = 0

    def __init__(self):
        ### Initiating built in Classes
        sc2.BotAI.__init__(self)

    async def on_start(self):
        print("Starting Game")
        await self.moveWorkers()

    async def on_step(self, iteration):

        target = Point2((95,75))
        final_target = Point2((10,10))
        defense_pos = Point2((target.x, target.y-10))

        await self.battleCruiserCount()
    
        if self.battlecruisers_count == 0:
            print("No Battle Cruiser Left")
            await self.distribute_workers()
            await self.hydraAttack(final_target)
        else:
            await self.hydraAttack(target)
            print("There are ", self.battlecruisers_count, " battlecruisers")
       
        await self.corruptAttack(defense_pos)

        await self.build_pool()

        await self.build_airdefense(defense_pos)    
        
    async def moveWorkers(self):
        townhalls = self.townhalls.ready
        # positions = [th.position for th in self.townhalls.ready]

        top_right_corner = self.game_info.map_size
        top_right = min(
            townhalls,
            key=lambda th: th.position.distance_to(top_right_corner)
        )

        bottom_right = min(
            townhalls,
            key=lambda th: (th.position.y, -th.position.x)
        )

        minerals = self.mineral_field.closer_than(10, top_right)
        if not minerals:
            return

        workers = self.workers
        if not workers:
            return

        for worker in workers:
            mineral = minerals.closest_to(worker)
            self.do(worker.gather(mineral))

    async def build_pool(self):
        townhalls = self.townhalls.ready

        top_right_corner = self.game_info.map_size
        top_right = min(
            townhalls,
            key=lambda th: th.position.distance_to(top_right_corner)
        )

        if not self.structures(UnitTypeId.SPAWNINGPOOL):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL) and self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
                print("Building Pool ", top_right)
                await self.build(
                    UnitTypeId.SPAWNINGPOOL, 
                    near=top_right
                )

    async def build_airdefense(self, position):
        # Check requirement
        if not self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            return

        # Check resources
        if self.minerals < 75:
            return

        if len(self.structures(UnitTypeId.SPORECRAWLER)) > 16:
            return

        if self.battlecruisers_count == 0:
            return

        # Get a worker
        worker = self.workers.random
        if not worker:
            return

        # Issue build order
        print("Building Air Defense")
        await self.build(
            UnitTypeId.SPORECRAWLER, 
            near=position, 
            build_worker=worker
        )

    async def hydraAttack(self, target):
        # print("Hydra Attacking")
        hydras = self.units(UnitTypeId.HYDRALISK)
        if not hydras:
            return

        ### FIND TOP MIDDLE
        top_middle = self.game_info.map_size / 2
        # top_middle = top_middle.with_y(self.game_info.map_size.y)

        ### FIND MAP CENTER
        map_center = self.game_info.map_center

        ### FIND ENEMY STARTING POSITION
        ### enemy_base = self.enemy_start_locations[0]

        ### FIND TOP MIDDLE
        map_size = self.game_info.map_size
        top_middle = Point2((map_size.x / 2, map_size.y))

        # print("Map Center", map_center)
        # print("Top Middle", top_middle)
        # print("Map Size", self.game_info.map_size)

        # target = Point2((70,78))

        ### 3 battle cruisers left
        ### Point2((70, 80))

        for hydra in hydras:    
            print("Hydra attacking ", target)     
            self.do(hydra.attack(target))

    async def corruptAttack(self, target):
        # print("Corrupts Attacking")
        corrupts = self.units(UnitTypeId.CORRUPTOR)
        if not corrupts:
            return

        ### FIND TOP MIDDLE
        map_size = self.game_info.map_size
        # target = Point2((map_size.x / 2, map_size.y))

        ### FIND MAP CENTER
        map_center = self.game_info.map_center


        for corrupt in corrupts:
            self.do(corrupt.attack(target))

    async def battleCruiserCount(self):
        battlecruisers = self.enemy_units(UnitTypeId.BATTLECRUISER)
        self.battlecruisers_count = len(battlecruisers) 

    async def on_end(self, result):
        print("Game ended. ", result)
