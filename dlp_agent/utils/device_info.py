import socket
import uuid
import platform
import os
import getpass

def get_device_info() -> dict:
    """Collect comprehensive device metadata that matches the dashboard schema."""
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "127.0.0.1"

    mac = uuid.getnode()
    mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))

    return {
        "agent_id": mac_address,         # Using MAC as the unique device ID
        "device_name": hostname,
        "hostname": hostname,
        "ip_address": ip_address,
        "mac_address": mac_address,
        "os": platform.system(),
        "os_version": platform.version(),
        "cpu": platform.processor(),
        "architecture": platform.machine(),
        "username": getpass.getuser(),
    }
