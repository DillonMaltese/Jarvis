# Lights.py
import asyncio, json, os, time
from typing import Optional
from kasa import Device, Discover

PLUG2_ALIAS = "Plug 2"   # match the alias shown by your finder
CACHE_FILE   = os.path.join(os.path.dirname(__file__), ".kasa_cache.json")
CACHE_TTL_S  = 3600

def _load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(d):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(d, f)
    except Exception:
        pass

async def _resolve_by_alias(alias: str) -> Optional[Device]:
    cache = _load_cache()
    now = time.time()
    if alias in cache:
        ip, ts = cache[alias].get("ip"), cache[alias].get("ts", 0)
        if ip and (now - ts) < CACHE_TTL_S:
            try:
                dev = await Device.connect(ip)
                await dev.update()
                return dev
            except Exception:
                pass  # fall through to discovery

    devices = await Discover.discover(timeout=10)
    for addr, dev in devices.items():
        await dev.update()
        if getattr(dev, "alias", "") == alias:
            cache[alias] = {"ip": addr, "ts": now}
            _save_cache(cache)
            return dev
    return None

async def _plug_action(alias: str, action: str, timeout=10):
    try:
        async with asyncio.timeout(timeout):
            dev = await _resolve_by_alias(alias)
            if dev is None:
                print(f"Plug2 not found by alias: {alias}")
                return None

            if action == "on":
                await dev.turn_on()
            elif action == "off":
                await dev.turn_off()
            elif action == "toggle":
                await (dev.turn_off() if getattr(dev, "is_on", False) else dev.turn_on())

            await dev.update()
            return dev.is_on
    except asyncio.TimeoutError:
        print(f"Plug2 timeout while resolving/commanding alias '{alias}'")
        return None
    except Exception as e:
        print("Plug2 error:", e)
        return None
    finally:
        try:
            await dev.disconnect()
        except Exception:
            pass

def plug2(action: str):
    return asyncio.run(_plug_action(PLUG2_ALIAS, action))
