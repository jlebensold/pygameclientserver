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
RECONNECT_DELAY = 2  # seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameClient:
    def __init__(self, host='localhost'):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Multiplayer Game - Client")
        self.clock = pygame.time.Clock()
        self.running = True
        self.other_clients = {}  # {client_id: {'pos': pos, 'color': color}}
        self.host_data = None  # {'pos': pos, 'color': color}
        self.server_host = host
        self.socket = None
        self.connected = False
        
        # Generate random position and color
        self.pos = [random.randint(50, WINDOW_SIZE[0]-50), random.randint(50, WINDOW_SIZE[1]-50)]
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        
        self.connect_to_server()

    def send_message(self, message):
        try:
            message_data = json.dumps(message).encode()
            length_data = struct.pack('!I', len(message_data))
            self.socket.sendall(length_data + message_data)
        except Exception as e:
            print(f"Error sending message: {e}")
            raise

    def receive_message(self):
        try:
            # Receive message length (4 bytes)
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            message_length = struct.unpack('!I', length_data)[0]
            
            # Receive the actual message
            message_data = b''
            while len(message_data) < message_length:
                chunk = self.socket.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return message_data.decode()
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, PORT))
            self.connected = True
            
            # Send initial data
            initial_data = {
                'pos': self.pos,
                'color': self.color
            }
            self.send_message(initial_data)
            print(f"Connected to server with color {self.color}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.connected = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None

    def update_position(self):
        while self.running:
            if not self.connected:
                time.sleep(RECONNECT_DELAY)
                self.connect_to_server()
                continue

            # Generate new random position
            self.pos = [random.randint(50, WINDOW_SIZE[0]-50), random.randint(50, WINDOW_SIZE[1]-50)]
            update_data = {'pos': self.pos}
            try:
                self.send_message(update_data)
            except:
                print("Failed to send position update, will attempt to reconnect")
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
            time.sleep(3)  # Update every 3 seconds

    def receive_game_state(self):
        while self.running:
            if not self.connected:
                time.sleep(0.1)
                continue

            try:
                data = self.receive_message()
                if not data:
                    print("Server disconnected, will attempt to reconnect")
                    self.connected = False
                    if self.socket:
                        try:
                            self.socket.close()
                        except:
                            pass
                        self.socket = None
                    continue

                game_state = json.loads(data)
                self.other_clients = game_state.get('clients', {})
                self.host_data = game_state.get('host')
            except Exception as e:
                print(f"Error receiving game state: {e}")
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None

    def run(self):
        # Start position update thread
        update_thread = threading.Thread(target=self.update_position)
        update_thread.daemon = True
        update_thread.start()

        # Start receive thread
        receive_thread = threading.Thread(target=self.receive_game_state)
        receive_thread.daemon = True
        receive_thread.start()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill(BLACK)
            
            # Draw other clients
            for client_data in self.other_clients.values():
                pos = client_data['pos']
                color = client_data['color']
                pygame.draw.circle(self.screen, color, pos, 20)
            
            # Draw host player
            if self.host_data:
                pos = self.host_data['pos']
                color = self.host_data['color']
                pygame.draw.circle(self.screen, color, pos, 20)
                # Draw "HOST" text above host player
                font = pygame.font.Font(None, 24)
                text = font.render("HOST", True, color)
                text_rect = text.get_rect(center=(pos[0], pos[1] - 30))
                self.screen.blit(text, text_rect)
            
            # Draw self
            pygame.draw.circle(self.screen, self.color, self.pos, 20)

            # Draw connection status
            status_text = "Connected" if self.connected else "Disconnected"
            status_color = (0, 255, 0) if self.connected else (255, 0, 0)
            font = pygame.font.Font(None, 36)
            text = font.render(status_text, True, status_color)
            self.screen.blit(text, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

if __name__ == "__main__":
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    client = GameClient(host)
    client.run()
