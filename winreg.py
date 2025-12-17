HKEY_CURRENT_USER = object()
KEY_SET_VALUE = 0
REG_SZ = 1


def OpenKey(*_args, **_kwargs):
    class DummyKey:
        def __enter__(self_inner):
            return self_inner

        def __exit__(self_inner, exc_type, exc, tb):
            return False
    return DummyKey()


def CreateKey(*_args, **_kwargs):
    return OpenKey()


def SetValueEx(*_args, **_kwargs):
    return None
