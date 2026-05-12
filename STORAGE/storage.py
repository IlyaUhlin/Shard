"""
Сервер хранения данных игры.
Управляет состоянием мира и предоставляет доступ через сокет.
Запускается отдельно от игры и CLI.
"""
import socket
import json
import threading
import pickle
from typing import Dict, Any, Optional
from core.map import Map
from entities.creature import Creature
from entities.energy_source import EnergySource
from entities.wall import Wall
from core.serializers.entity_serializer import EntitySerializer


class StorageServer:
    """Сервер для хранения и управления состоянием игры."""
    
    def __init__(self, host: str = 'localhost', port: int = 5000):
        self.host = host
        self.port = port
        self.world_state: Dict[str, Any] = {}
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.clients = []
        
    def save_world(self, tick: int, map_data: Map, entities: Dict[str, Any]):
        """Сохранение состояния мира."""
        self.world_state = {
            "tick": tick,
            "map": map_data.to_dict(),
            "entities": {}
        }
        
        for entity in map_data.get_all_entities():
            self.world_state["entities"][entity.id] = EntitySerializer.to_dict(entity)
            
        return True
    
    def load_world(self) -> Optional[Dict[str, Any]]:
        """Загрузка состояния мира."""
        if not self.world_state:
            return None
        return self.world_state.copy()
    
    def handle_client(self, client_socket: socket.socket, address):
        """Обработка запросов клиента."""
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                request = json.loads(data.decode('utf-8'))
                response = {"status": "error", "data": None}
                
                cmd = request.get("command")
                
                if cmd == "save":
                    tick = request.get("tick", 0)
                    map_dict = request.get("map")
                    entities = request.get("entities", {})
                    
                    if map_dict:
                        map_obj = Map(map_dict["width"], map_dict["height"])
                        self.save_world(tick, map_obj, entities)
                        response = {"status": "ok", "message": "World saved"}
                
                elif cmd == "load":
                    world = self.load_world()
                    if world:
                        response = {"status": "ok", "data": world}
                    else:
                        response = {"status": "error", "message": "No saved world"}
                
                elif cmd == "get_state":
                    response = {"status": "ok", "data": self.world_state}
                
                elif cmd == "ping":
                    response = {"status": "ok", "message": "pong"}
                
                client_socket.send(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
    
    def start(self):
        """Запуск сервера."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"Storage server started on {self.host}:{self.port}")
        
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)
                print(f"Client connected: {address}")
                
                thread = threading.Thread(target=self.handle_client, 
                                         args=(client_socket, address))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")
                    
    def stop(self):
        """Остановка сервера."""
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        if self.server_socket:
            self.server_socket.close()
        print("Storage server stopped")


def run_server(host: str = 'localhost', port: int = 5000):
    """Запуск сервера хранения."""
    server = StorageServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Storage Server for World Simulation")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind")
    args = parser.parse_args()
    
    run_server(args.host, args.port)
