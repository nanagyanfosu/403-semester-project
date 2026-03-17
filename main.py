import asyncio

from agents.block_agent import BlockAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.vendor_agent import VendorAgent
from agents.maintenance_agent import MaintenanceAgent


async def main():

    block_rooms = {

        "blocka@localhost":[f"RoomA{i}" for i in range(1,11)],
        "blockb@localhost":[f"RoomB{i}" for i in range(1,11)],
        "blockc@localhost":[f"RoomC{i}" for i in range(1,11)],
    }


    blockA = BlockAgent(
        "blockA@localhost",
        "password000",
        "BlockA",
        "coordinator@localhost",
        block_rooms["blocka@localhost"]
    )

    blockB = BlockAgent(
        "blockB@localhost",
        "password111",
        "BlockB",
        "coordinator@localhost",
        block_rooms["blockb@localhost"]
    )

    blockC = BlockAgent(
        "blockC@localhost",
        "password222",
        "BlockC",
        "coordinator@localhost",
        block_rooms["blockc@localhost"]
    )


    coordinator = CoordinatorAgent(
        "coordinator@localhost",
        "password333",
        "vendor@localhost",
        block_rooms
    )

    vendor = VendorAgent(
        "vendor@localhost",
        "password444"
    )
    maintenance = MaintenanceAgent(
        "maintenance@localhost",
        "password555"
    )


    await blockA.start(auto_register=True)
    await blockB.start(auto_register=True)
    await blockC.start(auto_register=True)

    await coordinator.start(auto_register=True)
    await vendor.start(auto_register=True)
    await maintenance.start(auto_register=True)


    print("\nSimulation running...\n")

    await asyncio.sleep(120)


    await blockA.stop()
    await blockB.stop()
    await blockC.stop()
    await coordinator.stop()
    await vendor.stop()
    await maintenance.stop()

if __name__ == "__main__":
    asyncio.run(main())