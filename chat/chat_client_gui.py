from PySide6.QtWidgets import *
from PySide6.QtCore import QThread, Signal
import socket, sys

class ReceiverThread(QThread):
    message_received = Signal(str)

    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.message_received.emit(data.decode())
            except:
                break

class ChatClient(QWidget):
    def __init__(self, username, host='127.0.0.1', port=12345):
        super().__init__()
        self.setWindowTitle(f"Chat - {username}")
        self.username = username

        # Připojení k serveru
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # Vláken pro příjem zpráv
        self.receiver = ReceiverThread(self.sock)
        self.receiver.message_received.connect(self.show_message)
        self.receiver.start()

        # GUI komponenty
        self.chat_area = QListWidget()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Odeslat")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.chat_area)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        self.setLayout(layout)

        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

    def send_message(self):
        msg = self.message_input.text().strip()
        if msg:
            full_msg = f"{self.username}: {msg}"
            self.sock.sendall(full_msg.encode())
            self.message_input.clear()

    def show_message(self, msg):
        self.chat_area.addItem(msg)
        self.chat_area.scrollToBottom()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    name, ok = QInputDialog.getText(None, "Uživatel", "Zadej své jméno:")
    if ok and name:
        window = ChatClient(name, host="127.0.0.1")  # ← zde změň IP serveru v LAN
        window.resize(400, 500)
        window.show()
        sys.exit(app.exec())
