_hotkeys = {}


def add_hotkey(hotkey, callback=None, suppress=False, trigger_on_release=False):
    _hotkeys[hotkey] = callback
    return hotkey


def remove_hotkey(hotkey):
    _hotkeys.pop(hotkey, None)


def wait():
    return None


def send(keys):
    return None


def press(key):
    return None


def release(key):
    return None


def hook(callback, suppress=False):
    return None


def unhook(callback):
    return None

