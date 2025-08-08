from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QLineEdit, QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import QThread, Signal, QTimer
from datetime import datetime
import socket
import logging
import subprocess
import sys
import os

class ReceiverThread(QThread):
    message_received = Signal(str)
    connection_lost = Signal()

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    self.connection_lost.emit()
                    break
                self.message_received.emit(data.decode())
            except socket.error:
                self.connection_lost.emit()
                break
            except Exception as e:
                logging.error(f"Receiver thread error: {e}")
                break

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
        self.wait(3000)

class ChatWidget(QWidget):
    def __init__(self, username, server_host='127.0.0.1', server_port=12345):
        super().__init__()
        self.username = username
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.receiver = None
        self.connection_attempts = 0
        self.max_attempts = 3  # Sníženo pro rychlejší detekci
        self.server_process = None  # Pro sledování procesu serveru
        self.server_started_by_me = False  # Flag zda jsem spustil server

        # UI prvky
        self.chat_area = QListWidget()
        self.chat_area.setAlternatingRowColors(True)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Napište zprávu...")
        
        self.send_button = QPushButton("Odeslat")
        self.retry_button = QPushButton("Zkusit znovu připojit")
        self.status_label = QLabel("Stav: Nepřipojeno")
        
        # Styling
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-weight: bold;
            }
        """)

        self.retry_button.clicked.connect(self.try_connect)
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.chat_area, 1)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.retry_button)
        
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        self.setLayout(layout)
        
        self.setMinimumSize(300, 500)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Timer pro automatické pokusy o připojení
        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(2000)  # Zkráceno na 2 sekundy
        self.reconnect_timer.timeout.connect(self.try_connect)

        self.disable_chat()
        self.try_connect()

    def start_server(self):
        """Spustí chat server jako samostatný proces."""
        if self.server_started_by_me:
            return
            
        try:
            # Cesta k chat_server.py
            script_dir = os.path.dirname(__file__)
            server_script = os.path.join(script_dir, "chat_server.py")
            
            if not os.path.exists(server_script):
                self.status_label.setText("Stav: Soubor chat_server.py nenalezen")
                return
            
            # Spuštění serveru jako subprocess
            self.server_process = subprocess.Popen([
                sys.executable, server_script
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.server_started_by_me = True
            self.status_label.setText("Stav: Spouštím vlastní server...")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3cd;
                    color: #856404;
                    padding: 5px;
                    border: 1px solid #ffeaa7;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            
            # Počkej chvilku a zkus se připojit
            QTimer.singleShot(3000, self.try_connect_after_server_start)
            
        except Exception as e:
            logging.error(f"Nepodařilo se spustit server: {e}")
            self.status_label.setText("Stav: Chyba při spouštění serveru")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 5px;
                    border: 1px solid #f5c6cb;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)

    def try_connect_after_server_start(self):
        """Pokus o připojení po spuštění serveru."""
        self.connection_attempts = 0  # Reset pokusů
        self.max_attempts = 5  # Více pokusů po spuštění serveru
        self.try_connect()

    def try_connect(self):
        if self.connection_attempts >= self.max_attempts:
            if not self.server_started_by_me:
                # Pokud jsme se nepřipojili a server ještě nebyl spuštěn
                self.status_label.setText("Stav: Server nedostupný, spouštím vlastní...")
                self.start_server()
                return
            else:
                self.status_label.setText(f"Stav: Připojení selhalo i po spuštění serveru")
                self.status_label.setStyleSheet("""
                    QLabel {
                        background-color: #f8d7da;
                        color: #721c24;
                        padding: 5px;
                        border: 1px solid #f5c6cb;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                """)
                self.reconnect_timer.stop()
                return
            
        self.connection_attempts += 1
        
        try:
            # Cleanup existing connections
            if self.receiver:
                self.receiver.stop()
                self.receiver = None
            if self.sock:
                self.sock.close()

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2.0)
            self.sock.connect((self.server_host, self.server_port))
            self.sock.settimeout(None)

            # Připojení úspěšné
            self.receiver = ReceiverThread(self.sock)
            self.receiver.message_received.connect(self.show_message)
            self.receiver.connection_lost.connect(self.on_connection_lost)
            self.receiver.start()

            self.enable_chat()
            
            # Zobraz správný status podle toho, zda jsme spustili server
            if self.server_started_by_me:
                self.status_label.setText("Stav: Připojeno (vlastní server)")
            else:
                self.status_label.setText("Stav: Připojeno")
                
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #d4edda;
                    color: #155724;
                    padding: 5px;
                    border: 1px solid #c3e6cb;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            self.reconnect_timer.stop()
            self.connection_attempts = 0
            
        except Exception as e:
            self.disable_chat()
            if self.server_started_by_me:
                self.status_label.setText(f"Stav: Připojování k vlastnímu serveru... ({self.connection_attempts}/{self.max_attempts})")
            else:
                self.status_label.setText(f"Stav: Nepřipojeno ({self.connection_attempts}/{self.max_attempts})")
                
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 5px;
                    border: 1px solid #f5c6cb;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            if self.connection_attempts < self.max_attempts:
                self.reconnect_timer.start()

    def on_connection_lost(self):
        """Handle connection lost signal from receiver thread"""
        self.disable_chat()
        self.status_label.setText("Stav: Spojení ztraceno, zkouším znovu...")
        self.connection_attempts = 0
        self.max_attempts = 3  # Reset na původní hodnotu
        self.reconnect_timer.start()

    def enable_chat(self):
        self.chat_area.setEnabled(True)
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.retry_button.setVisible(False)

    def disable_chat(self):
        self.chat_area.setEnabled(False)
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.retry_button.setVisible(True)

    def send_message(self):
        msg = self.message_input.text().strip()
        if msg and self.sock:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                full_msg = f"{current_time}:\n{self.username}: {msg}"
                self.sock.sendall(full_msg.encode('utf-8'))
                self.message_input.clear()
                # Zobrazit vlastní zprávu lokálně
                # self.show_message(full_msg)
            except Exception as e:
                self.status_label.setText("Stav: Odeslání selhalo")
                self.disable_chat()
                self.reconnect_timer.start()

    def show_message(self, msg):
        self.chat_area.addItem(msg)
        self.chat_area.scrollToBottom()

    def closeEvent(self, event):
        """Ukončení widgetu - zastavit timery a ukončit server pokud byl spuštěn"""
        self.reconnect_timer.stop()
        if self.receiver:
            self.receiver.stop()
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        
        # Ukončit server pokud byl spuštěn tímto widgetem
        if self.server_started_by_me and self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=3)
            except:
                try:
                    self.server_process.kill()
                except:
                    pass
                    
        event.accept()
