import pygame
import socket
import json
import threading
import random
import time
import struct

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (800, 600)
FPS = 60
PORT = 5555

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameServer:
    def __init__(self):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Multiplayer Game - Host")
        self.clock = pygame.time.Clock()
        self.running = True
        self.clients = {}  # {client_id: {'addr': addr, 'pos': pos, 'color': color}}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', PORT))
        self.server_socket.listen(5)
        
        # Server player properties
        self.server_pos = [random.randint(50, WINDOW_SIZE[0]-50), random.randint(50, WINDOW_SIZE[1]-50)]
        self.server_color = (255, 0, 0)  # Red color for host
        self.last_update = time.time()
        
        print(f"Server started on port {PORT}")

    def receive_message(self, client_socket):
        try:
            # Receive message length (4 bytes)
            length_data = client_socket.recv(4)
            if not length_data:
                return None
            message_length = struct.unpack('!I', length_data)[0]
            
            # Receive the actual message
            message_data = b''
            while len(message_data) < message_length:
                chunk = client_socket.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return message_data.decode()
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None

    def send_message(self, client_socket, message):
        try:
            message_data = json.dumps(message).encode()
            length_data = struct.pack('!I', len(message_data))
            client_socket.sendall(length_data + message_data)
        except Exception as e:
            print(f"Error sending message: {e}")
            raise

    def update_server_position(self):
        current_time = time.time()
        if current_time - self.last_update >= 3:  # Update every 3 seconds
            self.server_pos = [random.randint(50, WINDOW_SIZE[0]-50), random.randint(50, WINDOW_SIZE[1]-50)]
            self.last_update = current_time

    def handle_client(self, client_socket, addr):
        client_id = addr[1]
        try:
            # Receive initial client data
            data = self.receive_message(client_socket)
            if not data:
                return
                
            client_data = json.loads(data)
            
            self.clients[client_id] = {
                'addr': addr,
                'pos': client_data['pos'],
                'color': client_data['color'],
                'socket': client_socket
            }
            print(f"Client {client_id} connected with color {client_data['color']}")
            
            while self.running:
                # Receive position updates
                data = self.receive_message(client_socket)
                if not data:
                    break
                    
                update_data = json.loads(data)
                if client_id in self.clients:
                    self.clients[client_id]['pos'] = update_data['pos']
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            if client_id in self.clients:
                print(f"Client {client_id} disconnected")
                del self.clients[client_id]
            try:
                client_socket.close()
            except:
                pass

    def accept_connections(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.daemon = True
                thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
                break

    def broadcast_game_state(self):
        while self.running:
            # Update server position
            self.update_server_position()
            
            game_state = {
                'clients': {
                    client_id: {
                        'pos': client_data['pos'],
                        'color': client_data['color']
                    }
                    for client_id, client_data in self.clients.items()
                },
                'host': {
                    'pos': self.server_pos,
                    'color': self.server_color
                }
            }
            
            # Create a list of clients to remove
            clients_to_remove = []
            
            for client_id, client_data in self.clients.items():
                try:
                    self.send_message(client_data['socket'], game_state)
                except:
                    print(f"Failed to send to client {client_id}, marking for removal")
                    clients_to_remove.append(client_id)
            
            # Remove disconnected clients
            for client_id in clients_to_remove:
                if client_id in self.clients:
                    try:
                        self.clients[client_id]['socket'].close()
                    except:
                        pass
                    del self.clients[client_id]
                    print(f"Removed disconnected client {client_id}")
            
            time.sleep(1/30)  # 30 updates per second

    def run(self):
        # Start connection acceptor thread
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

        # Start broadcast thread
        broadcast_thread = threading.Thread(target=self.broadcast_game_state)
        broadcast_thread.daemon = True
        broadcast_thread.start()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill(BLACK)
            
            # Draw all clients
            for client_data in self.clients.values():
                pos = client_data['pos']
                color = client_data['color']
                pygame.draw.circle(self.screen, color, pos, 20)
            
            # Draw server (host) player
            pygame.draw.circle(self.screen, self.server_color, self.server_pos, 20)
            
            # Draw "HOST" text above server player
            font = pygame.font.Font(None, 24)
            text = font.render("HOST", True, self.server_color)
            text_rect = text.get_rect(center=(self.server_pos[0], self.server_pos[1] - 30))
            self.screen.blit(text, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        self.server_socket.close()

if __name__ == "__main__":
    server = GameServer()
    server.run() 