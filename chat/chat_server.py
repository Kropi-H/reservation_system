import socket
import threading

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
            print(f"Chat server spuštěn na {self.host}:{self.port}")
            
            while self.running:
                try:
                    client, addr = self.server.accept()
                    print(f"Připojen klient: {addr}")
                    self.clients.append(client)
                    print(f"Celkem připojených klientů: {len(self.clients)}")
                    
                    thread = threading.Thread(target=self.handle_client, args=(client,))
                    thread.daemon = True
                    thread.start()
                except socket.error:
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server.close()

    def handle_client(self, client):
        print(f"Spouštím handler pro klienta: {client}")
        while self.running:
            try:
                print(f"Čekám na zprávu od klienta: {client}")
                message = client.recv(1024)
                if not message:
                    print(f"Žádná zpráva od klienta: {client} - odpojuji")
                    break
                    
                decoded_message = message.decode('utf-8', errors='ignore')
                print(f"Přijata zpráva od {client}: '{decoded_message}'")
                
                # Přepošli zprávu všem klientům
                self.broadcast(message, client)
                
            except socket.error as e:
                print(f"Client error pro {client}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error pro {client}: {e}")
                break
                
        # Odstranit klienta ze seznamu při odpojení
        if client in self.clients:
            self.clients.remove(client)
        try:
            client.close()
        except:
            pass
        print(f"Klient {client} odpojen. Zbývá klientů: {len(self.clients)}")

    def broadcast(self, message, sender):
        print(f"=== BROADCAST START ===")
        print(f"Zpráva: {message}")
        print(f"Odesílatel: {sender}")
        print(f"Počet klientů: {len(self.clients)}")
        print(f"Seznam klientů: {self.clients}")
        
        disconnected_clients = []
        
        for i, client in enumerate(self.clients):
            print(f"Posílám zprávu klientovi #{i}: {client}")
            try:
                client.send(message)
                print(f"✓ Zpráva úspěšně odeslána klientovi #{i}")
            except Exception as e:
                print(f"✗ Chyba při odesílání klientovi #{i}: {e}")
                disconnected_clients.append(client)
        
        # Odstranit odpojené klienty
        for client in disconnected_clients:
            if client in self.clients:
                self.clients.remove(client)
            try:
                client.close()
            except:
                pass
        
        print(f"=== BROADCAST END ===")

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
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nUkončuji server...")
        server.stop()
