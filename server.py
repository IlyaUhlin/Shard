"""
Игровой сервер симуляции мира.
Запускается отдельно от CLI и Storage сервера.
"""
import socket
import json
import threading
import time
from typing import Dict, Any, Optional

from core.game_loop import GameLoop
from core.map import Map
from core.serializers.entity_serializer import EntitySerializer


class GameServer:
    """Сервер игры, управляющий симуляцией."""
    
    def __init__(self, width: int = 20, height: int = 20,
                 num_creatures: int = 5, num_energy_sources: int = 10,
                 storage_host: str = 'localhost', storage_port: int = 5000):
        self.game = GameLoop(width, height, num_creatures, num_energy_sources)
        self.storage_host = storage_host
        self.storage_port = storage_port
        self.running = False
        self.paused = False
        self.tick_delay = 0.2
        self.clients = []
        self.server_socket: Optional[socket.socket] = None
        
    def connect_to_storage(self) -> Optional[socket.socket]:
        """Подключение к серверу хранения."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.storage_host, self.storage_port))
            sock.settimeout(5.0)
            return sock
        except Exception as e:
            print(f"Failed to connect to storage: {e}")
            return None
    
    def save_to_storage(self):
        """Сохранение состояния в сервер хранения."""
        sock = self.connect_to_storage()
        if not sock:
            return False
        
        try:
            data = {
                "tick": self.game.tick,
                "map": self.game.map.to_dict(),
                "entities": {}
            }
            
            for entity in self.game.map.get_all_entities():
                data["entities"][entity.id] = EntitySerializer.to_dict(entity)
            
            request = {
                "command": "save",
                "tick": self.game.tick,
                "map": data["map"],
                "entities": data["entities"]
            }
            
            sock.send(json.dumps(request).encode('utf-8'))
            response = json.loads(sock.recv(4096).decode('utf-8'))
            print(f"Save response: {response}")
            return response.get("status") == "ok"
        except Exception as e:
            print(f"Save error: {e}")
            return False
        finally:
            sock.close()
    
    def load_from_storage(self) -> bool:
        """Загрузка состояния из сервера хранения."""
        sock = self.connect_to_storage()
        if not sock:
            return False
        
        try:
            request = {"command": "load"}
            sock.send(json.dumps(request).encode('utf-8'))
            response = json.loads(sock.recv(4096).decode('utf-8'))
            
            if response.get("status") == "ok" and response.get("data"):
                world_data = response["data"]
                self.game.tick = world_data.get("tick", 0)
                # Нужно восстановить map и entities
                print(f"Loaded world at tick {self.game.tick}")
                return True
            else:
                print("No saved world found")
                return False
        except Exception as e:
            print(f"Load error: {e}")
            return False
        finally:
            sock.close()
    
    def handle_client(self, client_socket: socket.socket, address):
        """Обработка запросов CLI клиентов."""
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                request = json.loads(data.decode('utf-8'))
                response = {"status": "error", "data": None}
                
                cmd = request.get("command")
                
                if cmd == "start":
                    self.game.start()
                    self.running = True
                    response = {"status": "ok", "message": "Game started"}
                
                elif cmd == "stop":
                    self.game.stop()
                    self.running = False
                    response = {"status": "ok", "message": "Game stopped"}
                
                elif cmd == "pause":
                    self.paused = not self.paused
                    response = {"status": "ok", "paused": self.paused}
                
                elif cmd == "tick":
                    if not self.paused:
                        stats = self.game.run_tick()
                        response = {"status": "ok", "data": stats}
                    else:
                        response = {"status": "error", "message": "Game paused"}
                
                elif cmd == "get_state":
                    state = {
                        "tick": self.game.tick,
                        "running": self.running,
                        "paused": self.paused,
                        "creatures_count": len(self.game.map.get_creatures()),
                        "energy_sources_count": len(self.game.map.get_energy_sources())
                    }
                    response = {"status": "ok", "data": state}
                
                elif cmd == "get_map":
                    response = {"status": "ok", "data": self.game.map.to_dict()}
                
                elif cmd == "save":
                    if self.save_to_storage():
                        response = {"status": "ok", "message": "Saved to storage"}
                    else:
                        response = {"status": "error", "message": "Save failed"}
                
                elif cmd == "load":
                    if self.load_from_storage():
                        response = {"status": "ok", "message": "Loaded from storage"}
                    else:
                        response = {"status": "error", "message": "Load failed"}
                
                elif cmd == "ping":
                    response = {"status": "ok", "message": "pong"}
                
                client_socket.send(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
    
    def start_server(self, host: str = 'localhost', port: int = 6000):
        """Запуск игрового сервера."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        
        print(f"Game server started on {host}:{port}")
        print(f"Connecting to storage at {self.storage_host}:{self.storage_port}...")
        
        # Игровой цикл в отдельном потоке
        game_thread = threading.Thread(target=self._game_loop)
        game_thread.daemon = True
        game_thread.start()
        
        while True:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)
                print(f"CLI client connected: {address}")
                
                thread = threading.Thread(target=self.handle_client,
                                         args=(client_socket, address))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print("\nShutting down game server...")
                self.running = False
                break
            except Exception as e:
                print(f"Server error: {e}")
    
    def _game_loop(self):
        """Внутренний игровой цикл."""
        while self.running:
            if not self.paused:
                self.game.run_tick()
                
                if len(self.game.map.get_creatures()) == 0:
                    print("All creatures died!")
                    self.paused = True
            
            time.sleep(self.tick_delay)


def run_game_server(host: str = 'localhost', port: int = 6000,
                   storage_host: str = 'localhost', storage_port: int = 5000,
                   width: int = 20, height: int = 20,
                   creatures: int = 5, energy: int = 10):
    """Запуск игрового сервера."""
    server = GameServer(width, height, creatures, energy, storage_host, storage_port)
    server.start_server(host, port)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Game Server for World Simulation")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind")
    parser.add_argument("--port", type=int, default=6000, help="Port to bind")
    parser.add_argument("--storage-host", type=str, default="localhost", help="Storage server host")
    parser.add_argument("--storage-port", type=int, default=5000, help="Storage server port")
    parser.add_argument("--width", type=int, default=20, help="World width")
    parser.add_argument("--height", type=int, default=20, help="World height")
    parser.add_argument("--creatures", type=int, default=5, help="Number of creatures")
    parser.add_argument("--energy", type=int, default=10, help="Number of energy sources")
    args = parser.parse_args()
    
    run_game_server(args.host, args.port, args.storage_host, args.storage_port,
                   args.width, args.height, args.creatures, args.energy)
