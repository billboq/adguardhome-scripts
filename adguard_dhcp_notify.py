#!/usr/bin/env python3
import json
import time
import os
import requests

# ================= CONFIGURATION =================
LEASES_FILE = "/opt/AdGuardHome/data/leases.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/<webhookID>/<webhookToken>"
POLL_INTERVAL = 30  # seconds
CACHE_FILE = "/tmp/adguard_dhcp_cache.json"
# =================================================

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

def save_cache(leases):
    with open(CACHE_FILE, "w") as f:
        json.dump(leases, f)

def get_leases():
    if not os.path.exists(LEASES_FILE):
        print(f"Leases file not found: {LEASES_FILE}")
        return []

    with open(LEASES_FILE, "r") as f:
        try:
            data = json.load(f)
            return data.get("leases", [])
        except Exception as e:
            print("Error reading leases file:", e)
            return []

def notify_discord(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("Error sending Discord message:", e)

def main():
    print("Starting DHCP monitor...")
    old_leases = load_cache()

    while True:
        leases = get_leases()
        new_devices = []

        for lease in leases:
            # Skip static leases
            if lease.get("static", True):
                continue
            # Check if this MAC is already in cache
            if not any(d.get("mac") == lease.get("mac") for d in old_leases):
                new_devices.append(lease)

        for device in new_devices:
            ip = device.get("ip")
            mac = device.get("mac")
            hostname = device.get("hostname", "Unknown")
            message = f"New device connected: `{hostname}` - IP: `{ip}` - MAC: `{mac}`"
            notify_discord(message)
            print(message)

        # Update cache with dynamic leases only
        dynamic_leases = [d for d in leases if not d.get("static", True)]
        save_cache(dynamic_leases)
        old_leases = dynamic_leases

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
