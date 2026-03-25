import socket
import uuid
import platform


def get_device_info() -> dict:
    """Collect basic device metadata for the current machine."""
    device_name = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(device_name)
    except socket.gaierror:
        ip_address = "127.0.0.1"

    mac = uuid.getnode()
    mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))

    return {
        "device_name": device_name,
        "ip_address": ip_address,
        "mac_address": mac_address,
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
    }
