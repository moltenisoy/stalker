"""
Monitor nativo de sistema (CPU, RAM, Disco, Red) y procesos.
- Métricas rápidas vía psutil (bajo overhead); opcional WMI para precisión extendida.
- Procesos ordenables por CPU/RAM.
- Kill de procesos con PID.
- Background refresh con sampling configurable.
- Atajos a herramientas del sistema (Task Manager, Startup Apps, dfrgui).
"""
import time
import psutil
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Literal, Optional
from threading import Thread, Lock

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
    def __init__(self, config=None):
        self._last_disk = psutil.disk_io_counters()
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()
        
        # Configuration
        self.config = config
        self._sampling_interval = 2.0
        self._process_refresh_interval = 3.0
        self._process_limit = 15
        
        if config:
            self._sampling_interval = config.get_syshealth_config("sampling_interval")
            self._process_refresh_interval = config.get_syshealth_config("process_refresh_interval")
            self._process_limit = config.get_syshealth_config("process_limit")
        
        # Background refresh mechanism
        self._cached_procs: List[ProcInfo] = []
        self._cached_procs_lock = Lock()
        self._cached_sort_by: Literal["cpu", "ram"] = "cpu"
        self._last_proc_refresh = 0
        self._refresh_thread: Optional[Thread] = None
        self._running = False
        
        # Cached snapshot for sampling
        self._cached_snapshot: Optional[ResourceSnapshot] = None

    def snapshot(self, use_sampling: bool = True) -> ResourceSnapshot:
        """
        Get current system resource snapshot.
        
        Args:
            use_sampling: If True, respect sampling interval to reduce overhead.
                         If False, force immediate snapshot.
        """
        now = time.time()
        
        # Check if we should return cached snapshot (low overhead mode)
        if use_sampling and self._cached_snapshot and (now - self._last_time) < self._sampling_interval:
            # Return cached snapshot if within sampling interval
            return self._cached_snapshot
        
        # Calculate time delta for rate calculations
        dt = max(now - self._last_time, 0.001)

        # Fetch fresh metrics
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

        # Create and cache snapshot
        self._cached_snapshot = ResourceSnapshot(
            cpu_percent=cpu,
            ram_used_gb=vm.used / (1024**3),
            ram_total_gb=vm.total / (1024**3),
            disk_read_mb_s=disk_read_mb_s,
            disk_write_mb_s=disk_write_mb_s,
            net_up_mb_s=net_up_mb_s,
            net_down_mb_s=net_down_mb_s,
            timestamp=now,
        )
        
        return self._cached_snapshot

    def start_background_refresh(self):
        """Start background thread for process list refresh."""
        if self._running:
            return
        self._running = True
        self._refresh_thread = Thread(target=self._refresh_loop, daemon=True)
        self._refresh_thread.start()
    
    def stop_background_refresh(self):
        """Stop background refresh thread."""
        self._running = False
        if self._refresh_thread:
            self._refresh_thread.join(timeout=2)
    
    def _refresh_loop(self):
        """Background loop to refresh process list."""
        while self._running:
            try:
                now = time.time()
                if now - self._last_proc_refresh >= self._process_refresh_interval:
                    # Refresh process list
                    procs = self._fetch_procs(self._cached_sort_by, self._process_limit)
                    with self._cached_procs_lock:
                        self._cached_procs = procs
                    self._last_proc_refresh = now
                time.sleep(1)  # Check every second
            except Exception:
                pass  # Silently ignore errors in background thread
    
    def _fetch_procs(self, by: Literal["cpu", "ram"] = "cpu", limit: int = 8) -> List[ProcInfo]:
        """Fetch and sort process list."""
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
    
    def top_procs(self, by: Literal["cpu", "ram"] = "cpu", limit: int = 8, use_cache: bool = True) -> List[ProcInfo]:
        """
        Get top processes sorted by CPU or RAM.
        
        Args:
            by: Sort by "cpu" or "ram"
            limit: Maximum number of processes to return
            use_cache: If True and background refresh is enabled, use cached results
        """
        if use_cache and self._running:
            # Check if sort order changed
            if by != self._cached_sort_by:
                self._cached_sort_by = by
                # Force immediate refresh for new sort order
                procs = self._fetch_procs(by, limit)
                with self._cached_procs_lock:
                    self._cached_procs = procs
                return procs
            
            # Return cached results
            with self._cached_procs_lock:
                return self._cached_procs[:limit]
        
        # Fetch fresh results
        return self._fetch_procs(by, limit)

    def kill(self, pid: int, force: bool = False) -> tuple[bool, str]:
        """
        Kill a process by PID.
        
        Args:
            pid: Process ID to kill
            force: If True, use kill() instead of terminate()
        
        Returns:
            Tuple of (success, message)
        """
        try:
            p = psutil.Process(pid)
            name = p.name()
            
            if force:
                p.kill()
            else:
                p.terminate()
            
            # Wait for process to terminate
            p.wait(timeout=3)
            return True, f"Proceso '{name}' (PID {pid}) terminado exitosamente"
        except psutil.NoSuchProcess:
            return False, f"Proceso con PID {pid} no existe"
        except psutil.AccessDenied:
            return False, f"Acceso denegado para terminar proceso con PID {pid}"
        except psutil.TimeoutExpired:
            # If timeout, try force kill
            if not force:
                try:
                    p.kill()
                    return True, f"Proceso (PID {pid}) terminado forzosamente"
                except Exception:
                    pass
            return False, f"No se pudo terminar proceso con PID {pid}"
        except Exception as e:
            return False, f"Error al terminar proceso: {str(e)}"
    
    @staticmethod
    def open_task_manager() -> tuple[bool, str]:
        """Open Windows Task Manager."""
        try:
            subprocess.Popen(["taskmgr.exe"])
            return True, "Task Manager abierto"
        except Exception as e:
            return False, f"Error al abrir Task Manager: {str(e)}"
    
    @staticmethod
    def open_startup_apps() -> tuple[bool, str]:
        """Open Windows Startup Apps settings."""
        try:
            # Windows 10/11 Startup Apps
            subprocess.Popen(["explorer", "shell:startup"])
            return True, "Startup Apps abierto"
        except Exception as e:
            return False, f"Error al abrir Startup Apps: {str(e)}"
    
    @staticmethod
    def open_defragmenter() -> tuple[bool, str]:
        """Open Windows Disk Defragmenter."""
        try:
            subprocess.Popen(["dfrgui.exe"])
            return True, "Defragmentador de disco abierto"
        except Exception as e:
            return False, f"Error al abrir defragmentador: {str(e)}"
    
    @staticmethod
    def open_resource_monitor() -> tuple[bool, str]:
        """Open Windows Resource Monitor."""
        try:
            subprocess.Popen(["resmon.exe"])
            return True, "Monitor de recursos abierto"
        except Exception as e:
            return False, f"Error al abrir monitor de recursos: {str(e)}"
    
    @staticmethod
    def open_system_info() -> tuple[bool, str]:
        """Open Windows System Information."""
        try:
            subprocess.Popen(["msinfo32.exe"])
            return True, "Información del sistema abierta"
        except Exception as e:
            return False, f"Error al abrir información del sistema: {str(e)}"