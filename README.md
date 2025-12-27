# adguardhome-scripts
Scripts for Adguard Home DHCP

## remove_expired_dhcp_leases.py
'remove_expired_dhcp_leases.py' script removes expired DHCP entries from Adguard Hom DHCP Server, even the ones not shown in GUI.
Adapt 'CONFIGURATION' variables according to your config.
This script can be used in a cron job

## adguard_dhcp_notify.py
'adguard_dhcp_notify.py' script sends a Discord notification when a new DHCP entry is created on Adguard Home DHCP Server.
Adapt 'CONFIGURATION' variables according to your config.
This script should be runned as a service. Follow the guide below for the how-to.

### 1. Create a systemd service file

Create a new file:

```bash
vim /etc/systemd/system/adguard-dhcp-monitor.service
```

Add the following content (adjust paths as needed):

```ini
[Unit]
Description=AdGuard Home DHCP Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/scripts
ExecStart=/usr/bin/python3 /root/scripts/adguard_dhcp_notify.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Reload systemd

```bash
systemctl daemon-reload
```

### 3. Enable service at startup

```bash
systemctl enable adguard-dhcp-monitor.service
```

### 4. Start the service now

```bash
systemctl start adguard-dhcp-monitor.service
```

### 5. Check status & logs

```bash
systemctl status adguard-dhcp-monitor.service
```
