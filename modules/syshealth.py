"""
Monitor nativo de sistema (CPU, RAM, Disco, Red) y procesos.
- Métricas rápidas vía psutil (bajo overhead); opcional WMI para precisión extendida.
- Procesos ordenables por CPU/RAM.
- Kill de procesos con PID.
"""
import time
import psutil
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Literal

@dataclass
class ResourceSnapshot:
    cpu_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_read_mb_s: float
    disk_write_mb_s: float
    net_up_mb_s: float
    net_down_mb_s: float
    timestamp: float

@dataclass
class ProcInfo:
    pid: int
    name: str
    cpu: float
    ram_mb: float
    username: str

class SysHealth:
    def __init__(self):
        self._last_disk = psutil.disk_io_counters()
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()

    def snapshot(self) -> ResourceSnapshot:
        now = time.time()
        dt = max(now - self._last_time, 0.001)

        disk = psutil.disk_io_counters()
        net = psutil.net_io_counters()
        disk_read_mb_s = (disk.read_bytes - self._last_disk.read_bytes) / (1024 * 1024) / dt
        disk_write_mb_s = (disk.write_bytes - self._last_disk.write_bytes) / (1024 * 1024) / dt
        net_down_mb_s = (net.bytes_recv - self._last_net.bytes_recv) / (1024 * 1024) / dt
        net_up_mb_s = (net.bytes_sent - self._last_net.bytes_sent) / (1024 * 1024) / dt

        self._last_disk = disk
        self._last_net = net
        self._last_time = now

        vm = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)

        return ResourceSnapshot(
            cpu_percent=cpu,
            ram_used_gb=vm.used / (1024**3),
            ram_total_gb=vm.total / (1024**3),
            disk_read_mb_s=disk_read_mb_s,
            disk_write_mb_s=disk_write_mb_s,
            net_up_mb_s=net_up_mb_s,
            net_down_mb_s=net_down_mb_s,
            timestamp=now,
        )

    def top_procs(self, by: Literal["cpu", "ram"] = "cpu", limit: int = 8) -> List[ProcInfo]:
        procs = []
        for p in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_info"]):
            try:
                procs.append(
                    ProcInfo(
                        pid=p.info["pid"],
                        name=p.info.get("name") or "",
                        cpu=p.info.get("cpu_percent") or 0.0,
                        ram_mb=(p.info.get("memory_info").rss if p.info.get("memory_info") else 0) / (1024 * 1024),
                        username=p.info.get("username") or "",
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        key = (lambda x: x.cpu) if by == "cpu" else (lambda x: x.ram_mb)
        return sorted(procs, key=key, reverse=True)[:limit]

    def kill(self, pid: int) -> bool:
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=2)
            return True
        except Exception:
            return False