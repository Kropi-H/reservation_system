from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QLineEdit, QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt
from datetime import datetime
import socket
import logging
import subprocess
import sys
import os
import json

class ReceiverThread(QThread):
    message_received = Signal(str)
    connection_lost = Signal()

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.running = True


    def run(self):
        print("ReceiverThread: Spouštím receiver thread")
        while self.running:
            try:
                print("ReceiverThread: Čekám na data...")
                data = self.sock.recv(1024)
                if not data:
                    print("ReceiverThread: Žádná data - spojení ukončeno")
                    self.connection_lost.emit()
                    break
                message = data.decode('utf-8', errors='ignore')
                print(f"ReceiverThread: Přijata zpráva: '{message}' (délka: {len(message)})")
                self.message_received.emit(message)
                print("ReceiverThread: Signal message_received emitted")
            except socket.error as e:
                print(f"ReceiverThread: Socket error: {e}")
                if self.running:
                    self.connection_lost.emit()
                break
            except Exception as e:
                print(f"ReceiverThread: Unexpected error: {e}")
                break
        print("ReceiverThread: Končím receiver thread")

    def stop(self):
        print("ReceiverThread: Zastavuji thread")
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
        self.max_attempts = 3
        self.server_process = None
        self.server_started_by_me = False
        self.chat_server = None  # Reference na interní server
        self.last_sent_message = None  # Pro filtrování duplikátů
        self.last_sent_message = None  # Sledování poslední odeslané zprávy
        
        # Načtení konfigurace pro zjištění režimu
        self.load_config()

        # UI prvky
        self.chat_area = QListWidget()
        self.chat_area.setAlternatingRowColors(True)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Napište zprávu...")
        
        self.send_button = QPushButton("Odeslat")
        self.retry_button = QPushButton("Zkusit znovu připojit")
        self.status_label = QLabel("Stav: Nepřipojeno")
        
        # Přidání titulku chatu
        self.title_label = QLabel("💬 Chat")
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #2e7d32;
                color: white;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px 6px 0 0;
                margin: 0;
            }
        """)
        
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
        layout.addWidget(self.title_label)
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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Timer pro automatické pokusy o připojení
        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(2000)
        self.reconnect_timer.timeout.connect(self.try_connect)

        self.disable_chat()
        
        # Zpožděné připojení - dá GUI čas na zobrazení
        QTimer.singleShot(1000, self.try_connect)

    def load_config(self):
        """Načte konfiguraci z chat_config.json"""
        try:
            config_path = self.get_config_path()
            print(f"ChatWidget: Načítám konfiguraci z {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"ChatWidget: Konfigurace načtena: {self.config}")
            
            # Aktualizace parametrů připojení z konfigurace
            if "server_ip" in self.config:
                self.server_host = self.config["server_ip"]
            if "server_port" in self.config:
                self.server_port = self.config["server_port"]
            if "username" in self.config:
                self.username = self.config["username"]
                
            print(f"ChatWidget: Použité připojení: {self.server_host}:{self.server_port}, user: {self.username}")
            
        except Exception as e:
            print(f"ChatWidget: Chyba při načítání konfigurace: {e}")
            self.config = {
                "mode": "client",
                "auto_start_server": False
            }
            print(f"ChatWidget: Použitá výchozí konfigurace: {self.config}")
    
    def get_config_path(self):
        """Získá správnou cestu ke konfiguračnímu souboru podle prostředí a OS"""
        import sys
        import platform
        
        if getattr(sys, 'frozen', False):
            # Produkční executable - použij OS-specifické umístění
            system = platform.system().lower()
            
            if system == 'windows':
                # Windows: AppData\Local
                base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            elif system == 'darwin':  # macOS
                # macOS: ~/Library/Application Support
                base_dir = os.path.expanduser('~/Library/Application Support')
            else:  # Linux a další Unix-like systémy
                # Linux: ~/.config (XDG_CONFIG_HOME)
                base_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            
            app_dir = os.path.join(base_dir, "ReservationSystem")
            
            # Vytvoř složku, pokud neexistuje
            os.makedirs(app_dir, exist_ok=True)
            
            config_path = os.path.join(app_dir, "chat_config.json")
            print(f"ChatWidget: PROD {platform.system()} - config v: {config_path}")
            
            # Backward kompatibilita - přesuň config z vedle executable
            old_config = os.path.join(os.path.dirname(sys.executable), "chat_config.json")
            if os.path.exists(old_config) and not os.path.exists(config_path):
                try:
                    import shutil
                    shutil.move(old_config, config_path)
                    print(f"ChatWidget: Přesunut config z {old_config} do {config_path}")
                except Exception as e:
                    print(f"ChatWidget: Chyba při přesunu: {e}")
        else:
            # Vývojové prostředí - původní lokace
            config_path = os.path.join(os.path.dirname(__file__), "chat_config.json")
            print(f"ChatWidget: DEV režim - config v: {config_path}")
        
        return config_path

    def try_connect(self):
        # Pokud je v konfiguraci režim "server", spusť server a TAKÉ se připoj jako client
        if self.config.get("mode") == "server":
            if not self.server_started_by_me:
                print("ChatWidget: Režim server - spouštím server a připojuji se jako client")
                self.start_server()
                # Po spuštění serveru se připojíme jako client pro příjem zpráv od ostatních
                QTimer.singleShot(2000, self.try_connect_as_server_client)
                return
            elif not self.sock:
                # Server už běží, ale nejsme připojeni jako client
                print("ChatWidget: Server běží, připojuji se jako client pro příjem zpráv")
                self.try_connect_as_server_client()
                return
        
        if self.connection_attempts >= self.max_attempts:
            if not self.server_started_by_me and self.config.get("mode") != "server":
                self.status_label.setText("Stav: Server nedostupný, spouštím vlastní...")
                self.start_server()
                return
            else:
                self.status_label.setText(f"Stav: Připojení selhalo i po spuštění serveru")
                self.reconnect_timer.stop()
                return
            
        self.connection_attempts += 1
        print(f"ChatWidget: Pokus o připojení #{self.connection_attempts}")
        
        self._do_connect()
    
    def _do_connect(self):
        """Skutečné připojení k serveru"""
        
        try:
            # Cleanup existing connections
            if self.receiver:
                self.receiver.stop()
                self.receiver = None
            if self.sock:
                self.sock.close()

            print(f"ChatWidget: Vytvářím socket...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2.0)
            
            print(f"ChatWidget: Připojuji se k {self.server_host}:{self.server_port}")
            self.sock.connect((self.server_host, self.server_port))
            self.sock.settimeout(None)
            print(f"ChatWidget: Úspěšně připojeno k {self.server_host}:{self.server_port}")

            # Připojení úspěšné
            self.receiver = ReceiverThread(self.sock)
            self.receiver.message_received.connect(self.on_message_received, Qt.QueuedConnection)
            self.receiver.connection_lost.connect(self.on_connection_lost, Qt.QueuedConnection)
            
            print("ChatWidget: Signály připojeny")
            self.receiver.start()
            print("ChatWidget: ReceiverThread spuštěn")

            # Test připojení - odešli test zprávu ihned po připojení
            QTimer.singleShot(1000, self.test_message_display)

            self.enable_chat()
            
            if self.server_started_by_me or self.config.get("mode") == "server":
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
            print(f"ChatWidget: Chyba při připojování: {e}")
            self.disable_chat()
            if self.server_started_by_me:
                self.status_label.setText(f"Stav: Připojování k vlastnímu serveru... ({self.connection_attempts}/{self.max_attempts})")
            else:
                self.status_label.setText(f"Stav: Nepřipojeno ({self.connection_attempts}/{self.max_attempts})")
                
            if self.connection_attempts < self.max_attempts:
                self.reconnect_timer.start()

    def start_server(self):
        """Spustí chat server - buď jako subprocess nebo interně."""
        if self.server_started_by_me:
            return
            
        try:
            # Pokud je config mode == "server", spustí interní server
            if self.config.get("mode") == "server":
                print("ChatWidget: Spouštím interní server")
                from .chat_server import ChatServer
                self.chat_server = ChatServer()
                # Spustíme server v threadu
                import threading
                server_thread = threading.Thread(target=self.chat_server.start, daemon=True)
                server_thread.start()
                self.server_started_by_me = True
                print("ChatWidget: Interní server spuštěn")
                return
            
            # Jinak spustíme externí server proces
            script_dir = os.path.dirname(os.path.abspath(__file__))
            server_script = os.path.join(script_dir, "chat_server.py")
            
            if not os.path.exists(server_script):
                self.status_label.setText("Stav: Soubor chat_server.py nenalezen")
                return
            
            self.server_process = subprocess.Popen([
                sys.executable, server_script
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.server_started_by_me = True
            self.status_label.setText("Stav: Spouštím vlastní server...")
            
            QTimer.singleShot(3000, self.try_connect_after_server_start)
            
        except Exception as e:
            print(f"ChatWidget: Nepodařilo se spustit server: {e}")
            self.status_label.setText("Stav: Chyba při spouštění serveru")

    def try_connect_after_server_start(self):
        """Pokusí se připojit po spuštění serveru"""
        print("ChatWidget: Pokouším se připojit po spuštění serveru")
        self.connection_attempts = 0
        self.max_attempts = 5
        self.try_connect()

    def try_connect_as_server_client(self):
        """Server widget se připojí jako client pro příjem zpráv od ostatních"""
        print("ChatWidget: Server widget se připojuje jako client")
        self.connection_attempts = 0
        
        # Pokud server běží na 0.0.0.0, klient se musí připojit na localhost
        original_host = self.server_host
        if self.server_host == "0.0.0.0":
            self.server_host = "127.0.0.1"
            print(f"ChatWidget: Změna adresy pro připojení z {original_host} na {self.server_host}")
        
        self._do_connect()
        
        # Obnovit původní host pro další operace
        self.server_host = original_host

    def test_message_display(self):
        print("ChatWidget: Odesílám zprávu o připojení všem")
        connection_msg = f"*** {self.username} se připojil ve {datetime.now().strftime('%H:%M')} ***"

        # Všichni (server i client) posílají zprávy stejným způsobem
        if self.sock:
            print(f"ChatWidget: Posílám zprávu o připojení přes socket")
            self.sock.sendall(connection_msg.encode('utf-8'))

    def on_message_received(self, msg):
        """Zpracuje přijatou zprávu"""
        print(f"ChatWidget: Přijata zpráva: '{msg}'")
        self.show_message(msg)

    def show_message(self, msg):
        print(f"ChatWidget: show_message volána s: '{msg}' (délka: {len(msg)})")
        try:
            self.chat_area.addItem(msg)
            self.chat_area.scrollToBottom()
            print(f"ChatWidget: Zpráva přidána do chat_area. Celkem položek: {self.chat_area.count()}")
        except Exception as e:
            print(f"ChatWidget: Chyba při zobrazování zprávy: {e}")

    def on_connection_lost(self):
        print("ChatWidget: Spojení ztraceno")
        self.disable_chat()
        self.status_label.setText("Stav: Spojení ztraceno, zkouším znovu...")
        self.connection_attempts = 0
        self.max_attempts = 3
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
        if msg:
            try:
                full_msg = f"{datetime.now().strftime('%H:%M')} {self.username}:\n> {msg}"
                print(f"ChatWidget: Odesílám zprávu: {full_msg}")
                
                # Server a Client posílají zprávy stejným způsobem - přes socket
                if self.sock:
                    print(f"ChatWidget: Posílám zprávu přes socket")
                    self.sock.sendall(full_msg.encode('utf-8'))
                else:
                    print(f"ChatWidget: Žádné spojení pro odeslání zprávy")
                    return
                
                self.message_input.clear()
                
            except Exception as e:
                print(f"ChatWidget: Chyba při odesílání: {e}")
                self.status_label.setText("Stav: Odeslání selhalo")
                self.disable_chat()
                self.reconnect_timer.start()

    def closeEvent(self, event):
        print("ChatWidget: Ukončování...")
        self.reconnect_timer.stop()
        if self.receiver:
            self.receiver.stop()
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        
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