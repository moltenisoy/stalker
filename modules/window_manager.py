import ctypes
from ctypes import wintypes
import win32con
import win32gui
import win32api

SPI_GETWORKAREA = 0x0030

def _get_work_area():
    rect = wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect  # left, top, right, bottom

def _get_foreground_hwnd():
    return win32gui.GetForegroundWindow()

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