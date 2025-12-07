"""
Expansión segura para IME/CJK/Coreano.
Estrategia:
1) Guardar clipboard actual.
2) Colocar texto objetivo en clipboard.
3) Simular Ctrl+V usando SendInput (Win32), evitando inyectar keycodes directos que rompen IME.
4) Restaurar clipboard original.
"""
import time
import win32con
import win32api
import win32clipboard
from ctypes import Structure, c_ulong, POINTER, sizeof, windll

class KEYBDINPUT(Structure):
    _fields_ = [("wVk", c_ulong),
                ("wScan", c_ulong),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", c_ulong)]

class INPUT(Structure):
    _fields_ = [("type", c_ulong),
                ("ki", KEYBDINPUT)]

def _send_vk(vk, flags=0):
    ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
    inp = INPUT(type=win32con.INPUT_KEYBOARD, ki=ki)
    windll.user32.SendInput(1, POINTER(INPUT)(inp), sizeof(INPUT))

def _press_ctrl_v():
    _send_vk(win32con.VK_CONTROL)
    _send_vk(ord('V'))
    _send_vk(ord('V'), win32con.KEYEVENTF_KEYUP)
    _send_vk(win32con.VK_CONTROL, win32con.KEYEVENTF_KEYUP)

def send_text_ime_safe(text: str):
    if not text:
        return
    # backup clipboard
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            backup = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        else:
            backup = None
    except Exception:
        backup = None
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()

    time.sleep(0.05)
    _press_ctrl_v()
    time.sleep(0.05)

    # restore clipboard
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        if backup is not None:
            win32clipboard.SetClipboardText(backup, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
    except Exception:
        pass