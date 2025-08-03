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
        while self.running:
            try:
                message = client.recv(1024)
                if not message:
                    break
                    
                # Přepošli zprávu všem klientům
                self.broadcast(message, client)
                
            except socket.error:
                break
                
        self.clients.remove(client)
        client.close()

    def broadcast(self, message, sender):
        for client in self.clients[:]:  # Copy list to avoid modification during iteration
            if client != sender:
                try:
                    client.send(message)
                except:
                    self.clients.remove(client)

    def stop(self):
        self.running = False
        for client in self.clients:
            client.close()
        self.server.close()

if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nUkončuji server...")
        server.stop()
