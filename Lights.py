# Lights.py
import asyncio
from kasa import Discover

PLUG2_IP = "192.168.18.161"   # Plug 2

async def _plug_action(host, action, timeout=10):
    try:
        # Timebox the entire connect+command
        async with asyncio.timeout(timeout):
            dev = await Discover.discover_single(host)  # <— key change
            await dev.update()

            if action == "on":
                await dev.turn_on()
            elif action == "off":
                await dev.turn_off()
            elif action == "toggle":
                await (dev.turn_off() if getattr(dev, "is_on", False) else dev.turn_on())

            await dev.update()
            return dev.is_on
    except TimeoutError:
        print(f"Plug2 timeout connecting to {host}")
        return None
    except Exception as e:
        print("Plug2 error:", e)
        return None

def plug2(action):
    return asyncio.run(_plug_action(PLUG2_IP, action))
