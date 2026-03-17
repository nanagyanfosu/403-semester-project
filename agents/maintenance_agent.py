import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from utilities.logger import get_logger


class MaintenanceAgent(Agent):

    def __init__(self, jid, password):
        super().__init__(jid,password)
        self.logger = get_logger("Maintenance")


    class RepairBehaviour(CyclicBehaviour):

        async def run(self):

            msg = await self.receive(timeout=5)

            if not msg:
                return

            if msg.get_metadata("performative") == "MAINTENANCE_REQUEST":

                block = msg.body

                print(f"Maintenance repairing leak at {block}")

                self.agent.logger.info(f"Repair started for {block}")

                await asyncio.sleep(5)

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative","REPAIR_COMPLETE")
                reply.body = block

                await self.send(reply)

                # print(f"Leak fixed at {block}")


    async def setup(self):

        print("Maintenance agent started")

        self.add_behaviour(self.RepairBehaviour())