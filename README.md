# RATbot
# PC Control Bot

Удалённое управление компьютером через Telegram.

## Возможности

- выполнение команд
- интерактивный shell
- скриншоты
- загрузка и скачивание файлов
- управление процессами
- выключение ПК

## Установка

### сервер

```bash
pip install aiogram aiohttp
```

### агент

``` bash
pip install requests pillow psutil
```

## настройка

в обоих файлах:

```python
AGENT_SECRET = "YOUR_SECRET"
SERVER_URL = "http://IP:8765"
```

в server_bot.py:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
ALLOWED_USER_ID = YOUR_ID
```

## запуск

сервер:

``` bash
python server_bot.py
```

агент:

``` bash
python pc_agent.py
```

## команды


/cmd <команда>
/screenshot
/shutdown
/lock


## безопасность

- используется секретный ключ
- доступ только по Telegram ID
