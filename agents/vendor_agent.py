import asyncio
from collections import deque
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from utilities.logger import get_logger


class VendorAgent(Agent):

    def __init__(self, jid, password):

        super().__init__(jid,password)

        self.water_stock = 30000
        self.truck_capacity = 5000

        self.delivery_queue = deque()

        self.truck_busy = False

        self.logger = get_logger("Vendor")

        self.trucks = {
            "Truck1": {"capacity": 5000, "available": True},
            "Truck2": {"capacity": 5000, "available": True},
            "Truck3": {"capacity": 5000, "available": True},
        }


    class VendorBehaviour(CyclicBehaviour):

        async def run(self):

            msg = await self.receive(timeout=1)

            if msg:

                if msg.get_metadata("performative") == "CHECK_WATER":

                    block = msg.body

                    available_truck = None

                    for truck, status in self.agent.trucks.items():

                        if status == "available":
                            available_truck = truck
                            break


                        if available_truck:

                            print(f"{available_truck} delivering water to {block}")

                            self.agent.trucks[available_truck] = "busy"

                            await asyncio.sleep(6)

                            print(f"{available_truck} returned from {block}")

                            self.agent.trucks[available_truck] = "available"

                        else:

                            print(f"No trucks available. Queuing request for {block}")

                            self.agent.delivery_queue.append(block)


                self.agent.truck_busy = True

                print(f"Vendor truck delivering to {block}")

                self.agent.logger.info(f"Truck dispatched to {block}")

                await asyncio.sleep(6)

                self.agent.water_stock -= self.agent.truck_capacity

                reply = Message(to="coordinator@localhost")

                reply.set_metadata("performative","VENDOR_ACCEPT")

                reply.body = block

                await self.send(reply)

                print(f"Delivery complete for {block}")

                print(f"**************************************")

                print(f"Vendor water stock remaining {self.agent.water_stock}L")

                self.agent.truck_busy = False

                if self.agent.delivery_queue:
                    next_block = self.agent.delivery_queue.popleft()

                    print(f"Processing next delivery for {next_block}")

                    self.agent.truck_busy = True

                    await asyncio.sleep(6)

                    print(f"Delivery complete for {next_block}")

                    print(f"**************************************")

                    print(f"Vendor water stock remaining {self.agent.water_stock}L")

                    self.agent.truck_busy = False


    async def setup(self):

        print("Vendor started")

        self.add_behaviour(self.VendorBehaviour())