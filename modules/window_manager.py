import ctypes
from ctypes import wintypes
import win32con
import win32gui
import win32api
import win32process
from typing import Dict, Optional

SPI_GETWORKAREA = 0x0030

def _get_work_area():
    rect = wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect  # left, top, right, bottom

def _get_foreground_hwnd():
    return win32gui.GetForegroundWindow()

def get_active_window_info() -> Dict[str, str]:
    """
    Get information about the currently active window.
    
    Returns:
        Dictionary with window title, class, and process name
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        
        # Get window title
        title = win32gui.GetWindowText(hwnd)
        
        # Get window class
        window_class = win32gui.GetClassName(hwnd)
        
        # Get process name
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            import psutil
            process = psutil.Process(pid)
            process_name = process.name()
        except:
            process_name = ""
        
        return {
            "hwnd": hwnd,
            "title": title,
            "class": window_class,
            "process": process_name,
            "pid": pid
        }
    except Exception as e:
        print(f"Error getting active window info: {e}")
        return {
            "hwnd": 0,
            "title": "",
            "class": "",
            "process": "",
            "pid": 0
        }

def detect_app_context() -> Optional[str]:
    """
    Detect the current application context based on active window.
    
    Returns:
        App context identifier (e.g., 'vscode', 'browser', 'explorer') or None
    """
    info = get_active_window_info()
    title = info["title"].lower()
    process = info["process"].lower()
    window_class = info["class"].lower()
    
    # VSCode detection
    if "visual studio code" in title or "code.exe" in process:
        return "vscode"
    
    # Browser detection
    if any(browser in process for browser in ["chrome.exe", "firefox.exe", "msedge.exe"]):
        return "browser"
    
    # File Explorer detection
    if "explorer.exe" in process and "cabinetw" in window_class:
        return "explorer"
    
    # Figma detection
    if "figma" in title.lower():
        return "figma"
    
    # Terminal detection
    if any(term in process for term in ["cmd.exe", "powershell.exe", "windowsterminal.exe"]):
        return "terminal"
    
    # Office apps
    if "winword.exe" in process:
        return "word"
    if "excel.exe" in process:
        return "excel"
    if "powerpnt.exe" in process:
        return "powerpoint"
    
    return None

def _get_monitor_info_from_hwnd(hwnd):
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    return win32api.GetMonitorInfo(monitor)

def _move(hwnd, x, y, w, h):
    win32gui.SetWindowPos(hwnd, None, x, y, w, h, win32con.SWP_NOZORDER | win32con.SWP_NOOWNERZORDER)

def snap_left():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    width = (wa.right - wa.left) // 2
    _move(hwnd, wa.left, wa.top, width, wa.bottom - wa.top)

def snap_right():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    width = (wa.right - wa.left) // 2
    _move(hwnd, wa.left + width, wa.top, width, wa.bottom - wa.top)

def snap_top():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    _move(hwnd, wa.left, wa.top, wa.right - wa.left, (wa.bottom - wa.top)//2)

def snap_bottom():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    _move(hwnd, wa.left, wa.top + (wa.bottom - wa.top)//2, wa.right - wa.left, (wa.bottom - wa.top)//2)

def snap_quadrant(position: str):
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    half_w = (wa.right - wa.left)//2
    half_h = (wa.bottom - wa.top)//2
    x = wa.left if "left" in position else wa.left + half_w
    y = wa.top if "top" in position else wa.top + half_h
    _move(hwnd, x, y, half_w, half_h)

def maximize():
    hwnd = _get_foreground_hwnd()
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def center():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x = wa.left + ((wa.right - wa.left) - w)//2
    y = wa.top + ((wa.bottom - wa.top) - h)//2
    _move(hwnd, x, y, w, h)

def move_next_monitor():
    hwnd = _get_foreground_hwnd()
    info = _get_monitor_info_from_hwnd(hwnd)
    monitors = win32api.EnumDisplayMonitors()
    current_idx = 0
    for idx, mon in enumerate(monitors):
        if mon[0] == info["Monitor"]:
            current_idx = idx
            break
    next_idx = (current_idx + 1) % len(monitors)
    next_info = win32api.GetMonitorInfo(monitors[next_idx][0])
    wa = next_info["Work"]
    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x = wa[0] + ((wa[2] - wa[0]) - w)//2
    y = wa[1] + ((wa[3] - wa[1]) - h)//2
    _move(hwnd, x, y, w, h)