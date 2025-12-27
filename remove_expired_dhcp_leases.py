#!/usr/bin/env python3
import json
from datetime import datetime, timezone
import requests
import os

# ================= CONFIGURATION =================
LEASES_FILE = "/opt/AdGuardHome/data/leases.json"
CACHE_FILE = "/tmp/adguard_dhcp_cache.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/<webhookID>/<webhookToken>"
# =================================================

# Load leases
with open(LEASES_FILE, "r") as f:
    data = json.load(f)

now = datetime.now(timezone.utc)

def is_active(lease):
    if lease.get("static", False):
        return True
    expires = lease.get("expires")
    if not expires:
        return False
    lease_time = datetime.fromisoformat(expires)
    return lease_time > now

# Count before cleanup
total_before = len(data["leases"])

# Keep only active leases
active_leases = [l for l in data["leases"] if is_active(l)]
removed = total_before - len(active_leases)
data["leases"] = active_leases

# Save cleaned leases
with open(LEASES_FILE, "w") as f:
    json.dump(data, f, indent=4)

# === Update cache ===
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
    # Keep only cached entries that still exist in active leases
    active_macs = {l["mac"] for l in active_leases if not l.get("static", False)}
    new_cache = [d for d in cache if d.get("mac") in active_macs]
    with open(CACHE_FILE, "w") as f:
        json.dump(new_cache, f)

# Console output
print(f"Cleaned up {removed} expired dynamic leases. Total leases now: {len(active_leases)}")

# Discord notification
if removed > 0 and DISCORD_WEBHOOK_URL:
    message = f"✅ Cleaned up {removed} expired dynamic DHCP leases in AdGuard Home."
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("Error sending Discord notification:", e)
