_clipboard_content = ""


def OpenClipboard():
    return True


def CloseClipboard():
    return True


def EmptyClipboard():
    global _clipboard_content
    _clipboard_content = ""
    return True


def GetClipboardData(format=None):
    return _clipboard_content


def SetClipboardText(text, format=None):
    global _clipboard_content
    _clipboard_content = text if text is not None else ""
    return True


def SetClipboardData(format, text):
    return SetClipboardText(text, format)


def IsClipboardFormatAvailable(format):
    return bool(_clipboard_content)
