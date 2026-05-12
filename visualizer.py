"""
Модуль визуализации игрового мира с использованием curses.
Отображает карту, существ, источники энергии и статистику в реальном времени.
"""
import curses
import time
from typing import Optional, Dict, Any
from core.map import Map
from core.game_loop import GameLoop
from core.enums import Direction
from entities.creature import Creature
from entities.energy_source import EnergySource
from entities.wall import Wall


class Visualizer:
    """Визуализатор игрового мира на базе curses."""
    
    # Символы для отображения
    SYMBOLS = {
        'empty': ' ',
        'wall': '█',
        'creature': '☺',
        'energy_source': '●',
        'border_h': '─',
        'border_v': '│',
        'corner_tl': '┌',
        'corner_tr': '┐',
        'corner_bl': '└',
        'corner_br': '┘',
    }
    
    # Цвета (если терминал поддерживает)
    COLOR_EMPTY = 1
    COLOR_CREATURE = 2
    COLOR_ENERGY = 3
    COLOR_WALL = 4
    COLOR_BORDER = 5
    COLOR_INFO = 6
    
    def __init__(self, game: GameLoop):
        self.game = game
        self.stdscr = None
        self.running = False
        self.paused = False
        self.tick_delay = 0.2  # Задержка между тиками в секундах
        self.selected_creature: Optional[Creature] = None
        self.message = ""
        self.message_time = 0
        
    def setup_colors(self):
        """Настройка цветов."""
        curses.start_color()
        curses.use_default_colors()
        
        if curses.can_change_color():
            try:
                curses.init_pair(self.COLOR_EMPTY, curses.COLOR_WHITE, -1)
                curses.init_pair(self.COLOR_CREATURE, curses.COLOR_GREEN, -1)
                curses.init_pair(self.COLOR_ENERGY, curses.COLOR_YELLOW, -1)
                curses.init_pair(self.COLOR_WALL, curses.COLOR_RED, -1)
                curses.init_pair(self.COLOR_BORDER, curses.COLOR_CYAN, -1)
                curses.init_pair(self.COLOR_INFO, curses.COLOR_MAGENTA, -1)
            except:
                pass
        else:
            curses.init_pair(self.COLOR_CREATURE, curses.COLOR_GREEN, -1)
            curses.init_pair(self.COLOR_ENERGY, curses.COLOR_YELLOW, -1)
            curses.init_pair(self.COLOR_WALL, curses.COLOR_RED, -1)
            curses.init_pair(self.COLOR_BORDER, curses.COLOR_CYAN, -1)
            curses.init_pair(self.COLOR_INFO, curses.COLOR_MAGENTA, -1)
    
    def init_screen(self, stdscr):
        """Инициализация экрана."""
        self.stdscr = stdscr
        curses.curs_set(0)  # Скрыть курсор
        self.stdscr.nodelay(True)  # Неблокирующий ввод
        self.stdscr.timeout(50)  # Таймаут для getch() в мс
        self.setup_colors()
        
    def get_map_display_size(self) -> tuple:
        """Получить размеры для отображения карты."""
        height, width = self.stdscr.getmaxyx()
        # Оставляем место для панели информации (снизу) и заголовка (сверху)
        map_height = height - 8
        map_width = min(width - 2, self.game.map.width * 2)
        return map_height, map_width
    
    def draw_border(self, start_x: int, start_y: int, width: int, height: int):
        """Рисование рамки вокруг карты."""
        try:
            # Горизонтальные линии
            for x in range(start_x + 1, start_x + width):
                self.stdscr.addch(start_y, x, self.SYMBOLS['border_h'], 
                                 curses.color_pair(self.COLOR_BORDER))
                self.stdscr.addch(start_y + height - 1, x, self.SYMBOLS['border_h'],
                                 curses.color_pair(self.COLOR_BORDER))
            
            # Вертикальные линии
            for y in range(start_y + 1, start_y + height - 1):
                self.stdscr.addch(y, start_x, self.SYMBOLS['border_v'],
                                 curses.color_pair(self.COLOR_BORDER))
                self.stdscr.addch(y, start_x + width - 1, self.SYMBOLS['border_v'],
                                 curses.color_pair(self.COLOR_BORDER))
            
            # Углы
            self.stdscr.addch(start_y, start_x, self.SYMBOLS['corner_tl'],
                             curses.color_pair(self.COLOR_BORDER))
            self.stdscr.addch(start_y, start_x + width - 1, self.SYMBOLS['corner_tr'],
                             curses.color_pair(self.COLOR_BORDER))
            self.stdscr.addch(start_y + height - 1, start_x, self.SYMBOLS['corner_bl'],
                             curses.color_pair(self.COLOR_BORDER))
            self.stdscr.addch(start_y + height - 1, start_x + width - 1, self.SYMBOLS['corner_br'],
                             curses.color_pair(self.COLOR_BORDER))
        except curses.error:
            pass  # Игнорируем ошибки рисования за пределами экрана
    
    def draw_map(self, start_x: int, start_y: int):
        """Отрисовка карты."""
        grid = self.game.map._grid
        width = self.game.map.width
        height = self.game.map.height
        
        for y in range(height):
            for x in range(width):
                entity = grid.get((x, y))
                symbol = self.SYMBOLS['empty']
                color = curses.color_pair(self.COLOR_EMPTY)
                
                if isinstance(entity, Creature):
                    symbol = self.SYMBOLS['creature']
                    color = curses.color_pair(self.COLOR_CREATURE)
                    # Подсветка выбранного существа
                    if self.selected_creature and entity.id == self.selected_creature.id:
                        color = curses.color_pair(self.COLOR_INFO) | curses.A_BOLD
                elif isinstance(entity, EnergySource):
                    symbol = self.SYMBOLS['energy_source']
                    color = curses.color_pair(self.COLOR_ENERGY)
                elif isinstance(entity, Wall):
                    symbol = self.SYMBOLS['wall']
                    color = curses.color_pair(self.COLOR_WALL)
                
                try:
                    # Рисуем символ (каждая клетка занимает 2 символа ширины для пропорций)
                    self.stdscr.addstr(start_y + y, start_x + x * 2, symbol * 2, color)
                except curses.error:
                    pass
    
    def draw_info_panel(self, start_y: int):
        """Отрисовка информационной панели."""
        height, width = self.stdscr.getmaxyx()
        
        creatures = self.game.map.get_creatures()
        energy_sources = self.game.map.get_energy_sources()
        
        # Статистика
        info_lines = [
            f" Tick: {self.game.tick} ",
            f" Creatures: {len(creatures)} ",
            f" Energy sources: {len(energy_sources)} ",
            f" Status: {'PAUSED' if self.paused else 'RUNNING'} ",
            f" Speed: {1/self.tick_delay:.1f} tps ",
        ]
        
        # Информация о выбранном существе
        if self.selected_creature:
            sc = self.selected_creature
            info_lines.append(f" Selected: ID={sc.id} E={sc.energy:.1f} Pos=({sc.x},{sc.y}) ")
        else:
            info_lines.append(" No creature selected ")
        
        # Сообщение
        if self.message and time.time() - self.message_time < 3:
            info_lines.append(f" >> {self.message} ")
        
        # Отрисовка
        for i, line in enumerate(info_lines[:5]):
            try:
                self.stdscr.addstr(start_y + i, 2, line, curses.color_pair(self.COLOR_INFO) | curses.A_BOLD)
            except curses.error:
                pass
        
        # Список существ с энергией
        try:
            self.stdscr.addstr(start_y, width // 2, " Creatures (ID:Energy) ", 
                              curses.color_pair(self.COLOR_INFO))
            for i, c in enumerate(creatures[:5]):
                marker = "*" if self.selected_creature and c.id == self.selected_creature.id else " "
                line = f"{marker} {c.id}:{c.energy:.0f}"
                self.stdscr.addstr(start_y + i + 1, width // 2, line,
                                  curses.color_pair(self.COLOR_CREATURE))
        except curses.error:
            pass
    
    def draw_help(self, start_y: int):
        """Отрисовка подсказок."""
        height, width = self.stdscr.getmaxyx()
        help_text = "Keys: [Space]Pause [Q]uit [+/-]Speed [1-9]Select [S]ave [L]oad [R]estart [H]elp"
        try:
            self.stdscr.addstr(start_y, max(0, (width - len(help_text)) // 2), 
                              help_text, curses.A_REVERSE)
        except curses.error:
            pass
    
    def show_message(self, msg: str):
        """Показать временное сообщение."""
        self.message = msg
        self.message_time = time.time()
    
    def handle_input(self):
        """Обработка пользовательского ввода."""
        try:
            key = self.stdscr.getch()
        except:
            return
        
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == ord(' '):
            self.paused = not self.paused
            self.show_message("Paused" if self.paused else "Resumed")
        elif key == ord('+') or key == ord('='):
            self.tick_delay = max(0.05, self.tick_delay - 0.05)
            self.show_message(f"Speed: {1/self.tick_delay:.1f} tps")
        elif key == ord('-') or key == ord('_'):
            self.tick_delay = min(2.0, self.tick_delay + 0.05)
            self.show_message(f"Speed: {1/self.tick_delay:.1f} tps")
        elif key >= ord('1') and key <= ord('9'):
            idx = key - ord('1')
            creatures = self.game.map.get_creatures()
            if idx < len(creatures):
                self.selected_creature = creatures[idx]
                self.show_message(f"Selected creature {creatures[idx].id}")
        elif key == ord('s') or key == ord('S'):
            filename = f"save_{self.game.tick}.json"
            self.game.save(filename)
            self.show_message(f"Saved to {filename}")
        elif key == ord('l') or key == ord('L'):
            self.show_message("Load not available in visual mode")
        elif key == ord('r') or key == ord('R'):
            self.game.__init__(num_creatures=5, num_energy_sources=10)
            self.show_message("World restarted")
        elif key == ord('h') or key == ord('H'):
            self.show_message("Help: Space=Pause, Q=Quit, +/-=Speed, 1-9=Select")
        elif self.selected_creature:
            # Бог может перемещать выбранное существо
            direction = None
            if key == curses.KEY_UP:
                direction = Direction.UP
            elif key == curses.KEY_DOWN:
                direction = Direction.DOWN
            elif key == curses.KEY_LEFT:
                direction = Direction.LEFT
            elif key == curses.KEY_RIGHT:
                direction = Direction.RIGHT
            
            if direction:
                if self.game.map.move_entity(self.selected_creature.id, direction):
                    self.show_message(f"Moved creature {self.selected_creature.id} {direction.value}")
                else:
                    self.show_message(f"Cannot move {direction.value}")
    
    def run(self, stdscr):
        """Основной цикл визуализации."""
        self.init_screen(stdscr)
        self.running = True
        
        while self.running:
            # Обработка ввода
            self.handle_input()
            
            if not self.paused:
                # Один тик игры
                self.game.run_tick()
                
                # Проверка окончания игры
                if len(self.game.map.get_creatures()) == 0:
                    self.show_message("All creatures died! Press R to restart")
                    self.paused = True
                
                # Обновление выбранного существа
                if self.selected_creature:
                    if self.selected_creature.energy <= 0:
                        self.selected_creature = None
            
            # Отрисовка
            self.stdscr.clear()
            
            height, width = self.stdscr.getmaxyx()
            map_height = min(height - 10, self.game.map.height)
            map_width = self.game.map.width
            
            # Центрирование карты
            start_x = max(1, (width - map_width * 2) // 2)
            start_y = 2
            
            self.draw_border(start_x, start_y, map_width * 2 + 2, map_height + 2)
            self.draw_map(start_x + 1, start_y + 1)
            self.draw_info_panel(height - 8)
            self.draw_help(height - 2)
            
            self.stdscr.refresh()
            
            # Задержка для контроля скорости
            time.sleep(self.tick_delay)
        
        self.game.stop()


def run_visual(game: GameLoop):
    """Запуск визуализатора."""
    visualizer = Visualizer(game)
    curses.wrapper(visualizer.run)


if __name__ == "__main__":
    # Тестовый запуск
    game = GameLoop(width=20, height=15, num_creatures=5, num_energy_sources=8)
    game.start()
    run_visual(game)
