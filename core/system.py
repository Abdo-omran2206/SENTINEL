import os
import platform
import getpass

class SystemInfo:
    def get_info(self):
        info = {
            "Device Name": platform.node(),
            "Operating System": platform.system(),
            "OS Version": platform.release(),
            "Username": getpass.getuser(),
            "Processor": platform.processor(),
            "Cores": os.cpu_count(),
        }

        # Threads (logical cores)
        try:
            import psutil
            info["Threads"] = psutil.cpu_count(logical=True)
        except:
            info["Threads"] = "Not available (install psutil)"

        return info