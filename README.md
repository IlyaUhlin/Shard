# Shard - World Simulation Game

Симуляция мира с существами, источниками энергии и стенами.

## Архитектура

Проект состоит из трех независимых компонентов:

1. **Storage Server** (`STORAGE/storage.py`) - Сервер хранения данных (порт 5000)
2. **Game Server** (`server.py`) - Игровой сервер с логикой симуляции (порт 6000)
3. **CLI Client** (`CLI/cli.py`) - Графический интерфейс на tkinter для управления игрой

## Запуск

### 1. Запуск сервера хранения

```bash
python -m STORAGE.storage --host localhost --port 5000
```

### 2. Запуск игрового сервера (в новом терминале)

```bash
python server.py --host localhost --port 6000 --storage-host localhost --storage-port 5000
```

Параметры игрового сервера:
- `--width`, `--height` - размеры мира
- `--creatures` - количество существ
- `--energy` - количество источников энергии

### 3. Запуск CLI клиента (в новом терминале)

```bash
python -m CLI.cli
```

В интерфейсе:
1. Нажмите **Connect** для подключения к игровому серверу
2. Используйте кнопки **Start**, **Stop**, **Pause** для управления
3. **Single Tick** - выполнить один шаг симуляции
4. **Save/Load** - сохранение/загрузка состояния через storage сервер
5. Включите **Auto-update** для автоматического обновления статистики

## Структура проекта

```
/workspace
├── CLI/
│   └── cli.py          # GUI клиент на tkinter
├── STORAGE/
│   └── storage.py      # Сервер хранения
├── core/
│   ├── game_loop.py    # Логика игры
│   ├── map.py          # Карта мира
│   ├── dispatcher.py   # Диспетчер транзакций
│   ├── TransactionPool.py
│   └── enums.py
├── entities/
│   ├── entity.py
│   ├── creature.py
│   ├── energy_source.py
│   └── wall.py
├── server.py           # Игровой сервер
└── README.md
```

## Протокол взаимодействия

Компоненты общаются через JSON over TCP:

### Команды Game Server:
- `start` - запустить игру
- `stop` - остановить игру
- `pause` - пауза/продолжить
- `tick` - выполнить один тик
- `get_state` - получить состояние
- `get_map` - получить карту
- `save` - сохранить в storage
- `load` - загрузить из storage

### Команды Storage Server:
- `save` - сохранить состояние мира
- `load` - загрузить состояние мира
- `get_state` - получить текущее сохранение
- `ping` - проверка связи

## Требования

- Python 3.x
- tkinter (обычно входит в стандартную поставку Python)
