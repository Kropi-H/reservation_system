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
                
                # Přepošli zprávu všem klientům
                self.broadcast(message, client)
                
            except socket.error as e:
                print(f"Socket error v handle_client: {e}")
                break
            except Exception as e:
                print(f"Neočekávaná chyba v handle_client: {e}")
                break
                
        # Odstranit klienta ze seznamu při odpojení
        if client in self.clients:
            self.clients.remove(client)
        try:
            client.close()
        except:
            pass
        print(f"KLIENT ODPOJEN. Zbývá: {len(self.clients)}")

    def broadcast(self, message, sender):
        print(f"=== BROADCAST START ===")
        print(f"Zpráva k odeslání: {message}")
        print(f"Počet příjemců: {len(self.clients)}")
        
        disconnected_clients = []
        
        for i, client in enumerate(self.clients):
            print(f"Posílám zprávu klientovi #{i}")
            try:
                client.send(message)
                print(f"✓ Odesláno klientovi #{i}")
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
    print("Spouštím chat server...")
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nUkončuji server...")
        server.stop()