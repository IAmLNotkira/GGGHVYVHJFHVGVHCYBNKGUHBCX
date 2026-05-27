import os
import sys
import subprocess
import minecraft_launcher_lib

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)

from PyQt5.QtGui import QFont, QPalette, QColor

from cache import save_account, load_account
from auth import login_microsoft


# ---------------------------------
# CROSS PLATFORM GAME DIRECTORY
# ---------------------------------
def get_game_directory():
    home = os.path.expanduser("~")

    # Windows
    if sys.platform.startswith("win"):
        return os.path.join(
            os.getenv("APPDATA"),
            ".my_new_launcher"
        )

    # macOS
    elif sys.platform == "darwin":
        return os.path.join(
            home,
            "Library",
            "Application Support",
            ".my_new_launcher"
        )

    # Linux
    else:
        return os.path.join(
            home,
            ".my_new_launcher"
        )


GAME_DIR = get_game_directory()

os.makedirs(GAME_DIR, exist_ok=True)


# ---------------------------------
# MAIN WINDOW
# ---------------------------------
class Launcher(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MyLauncher")
        self.setFixedSize(500, 420)

        self.apply_theme()

        layout = QVBoxLayout()

        # Title
        self.title = QLabel("MINECRAFT LAUNCHER")
        self.title.setFont(QFont("Arial", 16))
        layout.addWidget(self.title)

        # Username
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Offline username")
        layout.addWidget(self.name_input)

        # Server IP
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Server IP (optional)")
        layout.addWidget(self.server_input)

        # Minecraft version
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("Minecraft Version (example: 1.20.1)")
        layout.addWidget(self.version_input)

        # Status
        self.status = QLabel("Ready")
        layout.addWidget(self.status)

        # ---------------------------------
        # MICROSOFT LOGIN
        # ---------------------------------
        self.login_btn = QPushButton("Sign in with Microsoft")
        self.login_btn.clicked.connect(self.microsoft_login)
        layout.addWidget(self.login_btn)

        # Launch button
        self.launch_btn = QPushButton("LAUNCH MINECRAFT")
        self.launch_btn.clicked.connect(self.launch_game)
        layout.addWidget(self.launch_btn)

        self.setLayout(layout)

        # Load cached account
        self.auth = load_account()

        if self.auth:
            self.status.setText(
                f"Logged in as {self.auth.get('username', 'Unknown')}"
            )

    # ---------------------------------
    # DARK THEME
    # ---------------------------------
    def apply_theme(self):
        p = QPalette()

        p.setColor(QPalette.Window, QColor("#1e1e1e"))
        p.setColor(QPalette.WindowText, QColor("white"))

        self.setPalette(p)

    # ---------------------------------
    # MICROSOFT LOGIN
    # ---------------------------------
    def microsoft_login(self):
        try:
            self.status.setText("Opening Microsoft login...")

            auth = login_microsoft(GAME_DIR)

            self.auth = auth

            save_account(auth)

            self.status.setText(
                f"Logged in as {auth['username']}"
            )

            QMessageBox.information(
                self,
                "Success",
                "Microsoft login successful!"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Login Error",
                str(e)
            )

            self.status.setText("Login failed")

    # ---------------------------------
    # LAUNCH GAME
    # ---------------------------------
    def launch_game(self):
        try:
            version = self.version_input.text().strip()

            if not version:
                version = "1.20.1"

            self.status.setText("Installing Minecraft files...")

            # Install version if missing
            minecraft_launcher_lib.install.install_minecraft_version(
                version,
                GAME_DIR
            )

            self.status.setText("Preparing launch...")

            # ---------------------------------
            # AUTH OPTIONS
            # ---------------------------------
            if self.auth:
                options = {
                    "username": self.auth["username"],
                    "uuid": self.auth["uuid"],
                    "token": self.auth["token"],
                }

            else:
                # Offline mode
                username = self.name_input.text().strip()

                if not username:
                    username = "Player"

                options = {
                    "username": username
                }

            # ---------------------------------
            # GET LAUNCH COMMAND
            # ---------------------------------
            command = minecraft_launcher_lib.command.get_minecraft_command(
                version,
                GAME_DIR,
                options
            )

            self.status.setText("Launching Minecraft...")

            subprocess.Popen(command)

            self.status.setText("Minecraft launched!")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Error",
                str(e)
            )

            self.status.setText("Launch failed")


# ---------------------------------
# RUN APP
# ---------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Launcher()
    window.show()

    sys.exit(app.exec_())