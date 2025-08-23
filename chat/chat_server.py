import socket
import threading
import json
import os

class ChatServer:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "chat_config.json")
        print(f"Načítám konfiguraci z: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.host = config.get("server_ip", "127.0.0.1")
            self.port = config.get("server_port", 12345)
            print(f"Konfigurace načtena: host={self.host}, port={self.port}")
        except Exception as e:
            print(f"Chyba při načítání konfigurace: {e}")
            self.host = "0.0.0.0"
            self.port = 12345
            print(f"Použitá výchozí konfigurace: host={self.host}, port={self.port}")
        self.clients = []
        self.running = True

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print(f"Chat server spuštěn na {self.host}:{self.port}")
            while self.running:
                try:
                    client, addr = self.server.accept()
                    print(f"PŘIPOJEN KLIENT: {addr}")
                    self.clients.append(client)
                    print(f"CELKEM KLIENTŮ: {len(self.clients)}")
                    thread = threading.Thread(target=self.handle_client, args=(client,))
                    thread.daemon = True
                    thread.start()
                    print(f"THREAD SPUŠTĚN PRO KLIENTA: {addr}")
                except socket.error as e:
                    print(f"Socket error v main loop: {e}")
                    break
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server.close()

    def handle_client(self, client):
        print(f"HANDLER SPUŠTĚN pro klienta: {client}")
        while self.running:
            try:
                print(f"ČEKÁM NA ZPRÁVU od: {client}")
                message = client.recv(1024)
                if not message:
                    print(f"PRÁZDNÁ ZPRÁVA - odpojuji: {client}")
                    break
                decoded_message = message.decode('utf-8', errors='ignore')
                print(f"PŘIJATA ZPRÁVA: '{decoded_message}'")
                self.broadcast(message, client)
            except socket.error as e:
                print(f"Socket error v handle_client: {e}")
                break
            except Exception as e:
                print(f"Neočekávaná chyba v handle_client: {e}")
                break
        if client in self.clients:
            self.clients.remove(client)
        try:
            client.close()
        except:
            pass
        print(f"KLIENT ODPOJEN. Zbývá: {len(self.clients)}")
        
        # Pošleme zprávu o odpojení všem ostatním klientům
        if len(self.clients) > 0:
            disconnect_msg = f"*** Uživatel se odpojil z chatu ***"
            self.broadcast_disconnect_message(disconnect_msg.encode('utf-8'))

    def broadcast_disconnect_message(self, message):
        """Pošle zprávu o odpojení všem klientům"""
        print(f"=== DISCONNECT BROADCAST START ===")
        print(f"Zpráva o odpojení: {message}")
        disconnected_clients = []
        
        for i, client in enumerate(self.clients):
            print(f"Posílám zprávu o odpojení klientovi #{i}")
            try:
                client.send(message)
                print(f"✓ Zpráva o odpojení odeslána klientovi #{i}")
            except Exception as e:
                print(f"✗ Chyba při odesílání zprávy o odpojení klientovi #{i}: {e}")
                disconnected_clients.append(client)
        
        # Vyčištění odpojených klientů
        for client in disconnected_clients:
            if client in self.clients:
                self.clients.remove(client)
            try:
                client.close()
            except:
                pass
        print(f"=== DISCONNECT BROADCAST END ===")

    def broadcast(self, message, sender):
        print(f"=== BROADCAST START ===")
        print(f"Zpráva k odeslání: {message}")
        print(f"Počet příjemců: {len(self.clients)}")
        disconnected_clients = []
        
        # Pošleme zprávu VŠEM klientům (včetně odesílatele)
        # protože server a client jsou různé instance aplikace
        for i, client in enumerate(self.clients):
            print(f"Posílám zprávu klientovi #{i}")
            try:
                client.send(message)
                print(f"✓ Odesláno klientovi #{i}")
            except Exception as e:
                print(f"✗ Chyba při odesílání klientovi #{i}: {e}")
                disconnected_clients.append(client)
                
        # Vyčištění odpojených klientů
        for client in disconnected_clients:
            if client in self.clients:
                self.clients.remove(client)
            try:
                client.close()
            except:
                pass
        print(f"=== BROADCAST END ===")

    def broadcast_from_widget(self, message, sender_socket=None):
        """Broadcast zprávy z widgetu (server posílá zprávu)"""
        print(f"=== WIDGET BROADCAST START ===")
        print(f"Zpráva z widgetu: {message}")
        print(f"Počet příjemců: {len(self.clients)}")
        disconnected_clients = []
        
        # Pošleme zprávu POUZE ostatním klientům (ne server widgetu)
        for i, client in enumerate(self.clients):
            if client == sender_socket:
                print(f"Přeskakuji server widget #{i}")
                continue
                
            print(f"Posílám zprávu z widgetu ostatnímu klientovi #{i}")
            try:
                client.send(message)
                print(f"✓ Odesláno z widgetu klientovi #{i}")
            except Exception as e:
                print(f"✗ Chyba při odesílání z widgetu klientovi #{i}: {e}")
                disconnected_clients.append(client)
                
        # Vyčištění odpojených klientů
        for client in disconnected_clients:
            if client in self.clients:
                self.clients.remove(client)
            try:
                client.close()
            except:
                pass
        print(f"=== WIDGET BROADCAST END ===")

    def stop(self):
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        try:
            self.server.close()
        except:
            pass

if __name__ == "__main__":
    print("Spouštím chat server...")
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nUkončuji server...")
        server.stop()