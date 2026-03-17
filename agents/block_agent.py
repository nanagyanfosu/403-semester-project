import random
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from utilities.logger import get_logger


class BlockAgent(Agent):

    def __init__(self, jid, password, block_name, coordinator_jid, rooms):

        super().__init__(jid, password)

        self.block_name = block_name
        self.coordinator_jid = coordinator_jid
        self.rooms = rooms

        self.capacity = 5000
        self.tank_level = 5000

        self.threshold = 1000
        self.critical = 300

        self.waiting_for_refill = False

        self.logger = get_logger(block_name)
        


    class TankMonitor(CyclicBehaviour):

        async def run(self):

            await asyncio.sleep(3)

            consumption = random.randint(100,250)

# simulate rare leak
            if random.random() < 0.05:
                consumption = random.randint(500,700)

            self.agent.tank_level -= consumption

# leak detection
            if consumption > 450:

                leak_msg = Message(to=self.agent.coordinator_jid)
                leak_msg.set_metadata("performative","LEAK_ALERT")
                leak_msg.body = self.agent.block_name

                await self.send(leak_msg)

                print(f"{self.agent.block_name} detected pipe leak!")

            if self.agent.tank_level < 0:
                self.agent.tank_level = 0

            print(f"{self.agent.block_name} tank current level: {self.agent.tank_level}L")

            self.agent.logger.info(f"Tank level {self.agent.tank_level}")
            

            if (
                self.agent.tank_level <= self.agent.threshold
                and not self.agent.waiting_for_refill
            ):

                msg = Message(to=self.agent.coordinator_jid)

                msg.set_metadata("performative","REQUEST_REFILL")

                msg.body = self.agent.block_name

                await self.send(msg)

                self.agent.waiting_for_refill = True

                print(f"{self.agent.block_name} requested tank refill")

                self.agent.logger.info("Refill requested")


            if self.agent.tank_level <= self.agent.critical:

                msg = Message(to=self.agent.coordinator_jid)

                msg.set_metadata("performative","EMERGENCY_ALERT")

                msg.body = self.agent.block_name

                await self.send(msg)

                self.agent.logger.info("Emergency alert")


            msg = await self.receive(timeout=1)

            if msg:

                if msg.get_metadata("performative") == "REFILL_COMPLETE":

                    print(f"{self.agent.block_name} tank has been successfully refilled")

                    self.agent.tank_level = self.agent.capacity

                    self.agent.waiting_for_refill = False

                    self.agent.logger.info("Tank refill has successfully been completed")
    
        
    async def setup(self):

        print(f"{self.block_name} agent started")

        self.add_behaviour(self.TankMonitor())
        