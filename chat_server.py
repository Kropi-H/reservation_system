import socket
import threading
import sys

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.clients = []
        self.running = True

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print(f"🟢 Chat server spuštěn na {self.host}:{self.port}")
            print("📋 Čekám na připojení klientů...")
            print("⌨️  Stiskněte Ctrl+C pro ukončení serveru")
            
            while self.running:
                try:
                    client, addr = self.server.accept()
                    print(f"✅ Připojen klient: {addr}")
                    self.clients.append(client)
                    
                    thread = threading.Thread(target=self.handle_client, args=(client, addr))
                    thread.daemon = True
                    thread.start()
                except socket.error as e:
                    if self.running:
                        print(f"❌ Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.cleanup()

    def handle_client(self, client, addr):
        while self.running:
            try:
                message = client.recv(1024)
                if not message:
                    break
                    
                decoded_message = message.decode('utf-8')
                print(f"📨 Zpráva od {addr}: {decoded_message}")
                
                # Přepošli zprávu všem ostatním klientům
                self.broadcast(message, client)
                
            except socket.error as e:
                print(f"❌ Chyba při komunikaci s {addr}: {e}")
                break
                
        print(f"🔌 Klient {addr} se odpojil")
        if client in self.clients:
            self.clients.remove(client)
        client.close()

    def broadcast(self, message, sender):
        """Pošle zprávu všem klientům kromě odesílatele"""
        disconnected = []
        for client in self.clients[:]:  # Copy list to avoid modification during iteration
            if client != sender:
                try:
                    client.send(message)
                except:
                    disconnected.append(client)
        
        # Odstraň odpojené klienty
        for client in disconnected:
            if client in self.clients:
                self.clients.remove(client)

    def cleanup(self):
        """Vyčistí všechna připojení"""
        print("🧹 Ukončuji server a zavírám připojení...")
        self.running = False
        
        for client in self.clients[:]:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        
        try:
            self.server.close()
        except:
            pass

    def stop(self):
        """Zastaví server"""
        self.running = False
        try:
            self.server.close()
        except:
            pass

if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Ukončuji server...")
        server.stop()
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")
        server.stop()