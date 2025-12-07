"""
PyInstaller hook for Stalker application.
This hook ensures that the default config.json is bundled with the executable.
"""
from PyInstaller.utils.hooks import collect_data_files

# Collect the default config file
datas = [
    ('config.default.json', '.'),
]
