from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from utilities.logger import get_logger


class CoordinatorAgent(Agent):

    def __init__(self, jid, password, vendor_jid, block_rooms):

        super().__init__(jid,password)

        self.vendor_jid = vendor_jid
        self.block_rooms = block_rooms

        self.pending_requests = set()

        self.logger = get_logger("Coordinator")


    class CoordinationBehaviour(CyclicBehaviour):

        async def run(self):

            msg = await self.receive(timeout=5)

            if not msg:
                return

            perf = msg.get_metadata("performative")
            block = msg.body


            if perf == "REQUEST_REFILL":

                if block in self.agent.pending_requests:

                    return

                self.agent.pending_requests.add(block)

                print(f"Coordinator: Refill request from {block}")

                self.agent.logger.info(f"Request from {block}")

                vendor_msg = Message(to=self.agent.vendor_jid)

                vendor_msg.set_metadata("performative","CHECK_WATER")

                vendor_msg.body = block

                await self.send(vendor_msg)


            elif perf == "VENDOR_ACCEPT":

                block = msg.body

                print(f"Vendor has accepted delivery for {block}")

                self.agent.logger.info(f"Vendor accepted {block}")

                confirm = Message(to=f"{block.lower()}@localhost")

                confirm.set_metadata("performative","REFILL_COMPLETE")

                confirm.body = block

                await self.send(confirm)

                self.agent.pending_requests.remove(block)


            elif perf == "VENDOR_REJECT":

                print("Vendor rejected request")

                self.agent.logger.info("Vendor out of water")


            elif perf == "EMERGENCY_ALERT":

                print(f"**************************************")
                print(f"Emergency water shortage in {block}")
                print(f"**************************************")

                self.agent.logger.info("Emergency alert received")

                rooms = self.agent.block_rooms[f"{block.lower()}@localhost"]

                for room in rooms:

                    print(f"Notify {room}: There is water shortage in your block. Conserve water.")


            elif perf == "LEAK_ALERT":

                block = msg.body

                print(f"Coordinator received leak alert from {block}")

                maintenance_msg = Message(to="maintenance@localhost")
                maintenance_msg.set_metadata("performative","MAINTENANCE_REQUEST")
                maintenance_msg.body = block

                await self.send(maintenance_msg)

            elif perf == "REPAIR_COMPLETE":

                block = msg.body

                print(f"Maintenance has repaired leak at {block}")

                self.agent.logger.info(f"Repair complete for {block}")

    async def setup(self):

        print("Coordinator started")

        self.add_behaviour(self.CoordinationBehaviour())