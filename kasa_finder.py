import asyncio
from kasa import Discover

async def main():
    devices = await Discover.discover(timeout=10)
    if not devices:
        print("No devices found.")
        return
    for addr, dev in devices.items():
        await dev.update()
        print(f"Found {dev.alias} ({dev.model}) at {addr} is_on={dev.is_on}")

asyncio.run(main())
