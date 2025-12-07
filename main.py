import sys
from PySide6.QtWidgets import QApplication
from core.app import LauncherApp

def main():
    app = QApplication(sys.argv)
    launcher = LauncherApp(app)
    launcher.start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()