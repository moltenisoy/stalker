def MonitorFromWindow(hwnd, flag=None):
    return {"hwnd": hwnd}


def GetMonitorInfo(monitor):
    # Return a minimal monitor info structure compatible with usage in code
    return {"Monitor": (0, 0, 1920, 1080), "Work": (0, 0, 1920, 1080)}


def EnumDisplayMonitors():
    return [(object(), None)]

