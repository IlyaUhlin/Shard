"""
CLI клиент для управления игрой через tkinter.
Запускается отдельно от игрового сервера и сервера хранения.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import threading
from typing import Optional


class GameClient:
    """Клиент для подключения к игровому серверу."""
    
    def __init__(self, host: str = 'localhost', port: int = 6000):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        
    def connect(self) -> bool:
        """Подключение к серверу."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(5.0)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def send_command(self, command: str, **kwargs) -> dict:
        """Отправка команды серверу."""
        if not self.socket:
            if not self.connect():
                return {"status": "error", "message": "Not connected"}
        
        request = {"command": command, **kwargs}
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = json.loads(self.socket.recv(4096).decode('utf-8'))
            return response
        except Exception as e:
            self.socket = None
            return {"status": "error", "message": str(e)}
    
    def disconnect(self):
        """Отключение от сервера."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None


class GameGUI:
    """Графический интерфейс на tkinter."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("World Simulation - God Mode")
        self.root.geometry("800x600")
        
        self.client = GameClient()
        self.connected = False
        self.update_timer = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка интерфейса."""
        # Панель подключения
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky=tk.W)
        self.host_entry = ttk.Entry(conn_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=tk.W)
        self.port_entry = ttk.Entry(conn_frame, width=8)
        self.port_entry.insert(0, "6000")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self._toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=10)
        
        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=5, padx=10)
        
        # Панель управления
        control_frame = ttk.LabelFrame(self.root, text="Game Control", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_style = {'padx': 20, 'pady': 5}
        
        self.start_btn = ttk.Button(control_frame, text="Start", command=lambda: self._send_cmd("start"))
        self.start_btn.grid(row=0, column=0, **btn_style)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", command=lambda: self._send_cmd("stop"))
        self.stop_btn.grid(row=0, column=1, **btn_style)
        
        self.pause_btn = ttk.Button(control_frame, text="Pause", command=lambda: self._send_cmd("pause"))
        self.pause_btn.grid(row=0, column=2, **btn_style)
        
        self.tick_btn = ttk.Button(control_frame, text="Single Tick", command=self._do_tick)
        self.tick_btn.grid(row=0, column=3, **btn_style)
        
        self.save_btn = ttk.Button(control_frame, text="Save", command=lambda: self._send_cmd("save"))
        self.save_btn.grid(row=0, column=4, **btn_style)
        
        self.load_btn = ttk.Button(control_frame, text="Load", command=lambda: self._send_cmd("load"))
        self.load_btn.grid(row=0, column=5, **btn_style)
        
        # Панель статистики
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=15, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка обновления
        refresh_frame = ttk.Frame(self.root)
        refresh_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.refresh_btn = ttk.Button(refresh_frame, text="Refresh State", command=self._refresh_state)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.auto_update_var = tk.BooleanVar(value=False)
        self.auto_check = ttk.Checkbutton(refresh_frame, text="Auto-update", 
                                          variable=self.auto_update_var,
                                          command=self._toggle_auto_update)
        self.auto_check.pack(side=tk.LEFT, padx=20)
        
    def _toggle_connection(self):
        """Переключение подключения."""
        if self.connected:
            self.client.disconnect()
            self.connected = False
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Disconnected", foreground="red")
            self._set_controls_state(tk.DISABLED)
        else:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            self.client.host = host
            self.client.port = port
            
            if self.client.connect():
                self.connected = True
                self.connect_btn.config(text="Disconnect")
                self.status_label.config(text="Connected", foreground="green")
                self._set_controls_state(tk.NORMAL)
                self._refresh_state()
            else:
                messagebox.showerror("Error", "Failed to connect to server")
    
    def _set_controls_state(self, state):
        """Установка состояния элементов управления."""
        for btn in [self.start_btn, self.stop_btn, self.pause_btn, 
                    self.tick_btn, self.save_btn, self.load_btn]:
            btn.config(state=state)
    
    def _send_cmd(self, cmd: str, **kwargs):
        """Отправка команды и отображение результата."""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        
        response = self.client.send_command(cmd, **kwargs)
        self._show_response(cmd, response)
        
        if cmd in ["start", "stop", "pause"]:
            self._refresh_state()
    
    def _do_tick(self):
        """Выполнение одного тика."""
        if not self.connected:
            return
        
        response = self.client.send_command("tick")
        self._show_response("tick", response)
        self._refresh_state()
    
    def _refresh_state(self):
        """Обновление состояния игры."""
        if not self.connected:
            return
        
        state_resp = self.client.send_command("get_state")
        map_resp = self.client.send_command("get_map")
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        if state_resp.get("status") == "ok":
            state = state_resp["data"]
            self.stats_text.insert(tk.END, f"=== Game State ===\n")
            self.stats_text.insert(tk.END, f"Tick: {state.get('tick', 0)}\n")
            self.stats_text.insert(tk.END, f"Running: {state.get('running', False)}\n")
            self.stats_text.insert(tk.END, f"Paused: {state.get('paused', False)}\n")
            self.stats_text.insert(tk.END, f"Creatures: {state.get('creatures_count', 0)}\n")
            self.stats_text.insert(tk.END, f"Energy Sources: {state.get('energy_sources_count', 0)}\n")
        
        if map_resp.get("status") == "ok":
            map_data = map_resp["data"]
            self.stats_text.insert(tk.END, f"\n=== Map ({map_data.get('width', 0)}x{map_data.get('height', 0)}) ===\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def _show_response(self, cmd: str, response: dict):
        """Отображение ответа сервера."""
        status = response.get("status", "unknown")
        message = response.get("message", "")
        data = response.get("data", {})
        
        if status == "ok":
            print(f"[{cmd}] OK: {message}")
            if data:
                print(f"  Data: {data}")
        else:
            print(f"[{cmd}] ERROR: {message}")
            messagebox.showerror(f"{cmd} Error", message)
    
    def _toggle_auto_update(self):
        """Переключение автообновления."""
        if self.auto_update_var.get():
            self._auto_update()
        else:
            if self.update_timer:
                self.root.after_cancel(self.update_timer)
                self.update_timer = None
    
    def _auto_update(self):
        """Автоматическое обновление."""
        if self.auto_update_var.get() and self.connected:
            self._refresh_state()
            self.update_timer = self.root.after(1000, self._auto_update)


def main():
    """Запуск CLI приложения."""
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
