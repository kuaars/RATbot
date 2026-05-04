import asyncio
import uuid
import time
import base64
import io
import json
import socket
import logging
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN"
ALLOWED_USER_ID = 123456789
AGENT_SECRET = "YOUR_SECRET_KEY"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

tasks = {}
agent_last_seen = 0


def is_owner(m: Message):
    return m.from_user.id == ALLOWED_USER_ID


async def new_task(chat_id, ttype, payload=None):
    tid = str(uuid.uuid4())
    tasks[tid] = {"chat_id": chat_id, "type": ttype, "payload": payload or {}, "status": "pending"}
    return tid


@dp.message(Command("start"))
async def start(m: Message):
    if not is_owner(m): return
    await m.answer("ready")


@dp.message(Command("cmd"))
async def cmd(m: Message):
    if not is_owner(m): return
    text = m.text.split(maxsplit=1)[1]
    tid = await new_task(m.chat.id, "cmd", {"command": text})
    await m.answer(tid)


async def api_pending(req):
    if req.headers.get("X-Secret") != AGENT_SECRET:
        return web.json_response({}, status=401)
    return web.json_response({"tasks": [
        {"id": k, "type": v["type"], "payload": v["payload"]}
        for k, v in tasks.items() if v["status"] == "pending"
    ]})


async def api_result(req):
    tid = req.match_info["task_id"]
    data = await req.json()
    t = tasks[tid]
    t["status"] = "done"

    if data["type"] == "text":
        await bot.send_message(t["chat_id"], data["content"])

    if data["type"] == "photo":
        img = base64.b64decode(data["content"])
        await bot.send_photo(t["chat_id"], BufferedInputFile(img, "screen.png"))

    return web.json_response({"ok": True})


async def main():
    app = web.Application()
    app.router.add_get("/api/tasks/pending", api_pending)
    app.router.add_post("/api/tasks/{task_id}/result", api_result)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 8765).start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())import asyncio
import uuid
import time
import base64
import io
import json
import socket
import logging
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN"
ALLOWED_USER_ID = 123456789
AGENT_SECRET = "YOUR_SECRET_KEY"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

tasks = {}
agent_last_seen = 0


def is_owner(m: Message):
    return m.from_user.id == ALLOWED_USER_ID


async def new_task(chat_id, ttype, payload=None):
    tid = str(uuid.uuid4())
    tasks[tid] = {"chat_id": chat_id, "type": ttype, "payload": payload or {}, "status": "pending"}
    return tid


@dp.message(Command("start"))
async def start(m: Message):
    if not is_owner(m): return
    await m.answer("ready")


@dp.message(Command("cmd"))
async def cmd(m: Message):
    if not is_owner(m): return
    text = m.text.split(maxsplit=1)[1]
    tid = await new_task(m.chat.id, "cmd", {"command": text})
    await m.answer(tid)


async def api_pending(req):
    if req.headers.get("X-Secret") != AGENT_SECRET:
        return web.json_response({}, status=401)
    return web.json_response({"tasks": [
        {"id": k, "type": v["type"], "payload": v["payload"]}
        for k, v in tasks.items() if v["status"] == "pending"
    ]})


async def api_result(req):
    tid = req.match_info["task_id"]
    data = await req.json()
    t = tasks[tid]
    t["status"] = "done"

    if data["type"] == "text":
        await bot.send_message(t["chat_id"], data["content"])

    if data["type"] == "photo":
        img = base64.b64decode(data["content"])
        await bot.send_photo(t["chat_id"], BufferedInputFile(img, "screen.png"))

    return web.json_response({"ok": True})


async def main():
    app = web.Application()
    app.router.add_get("/api/tasks/pending", api_pending)
    app.router.add_post("/api/tasks/{task_id}/result", api_result)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 8765).start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())import asyncio
import uuid
import time
import base64
import io
import json
import socket
import logging
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN"
ALLOWED_USER_ID = 123456789
AGENT_SECRET = "YOUR_SECRET_KEY"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

tasks = {}
agent_last_seen = 0


def is_owner(m: Message):
    return m.from_user.id == ALLOWED_USER_ID


async def new_task(chat_id, ttype, payload=None):
    tid = str(uuid.uuid4())
    tasks[tid] = {"chat_id": chat_id, "type": ttype, "payload": payload or {}, "status": "pending"}
    return tid


@dp.message(Command("start"))
async def start(m: Message):
    if not is_owner(m): return
    await m.answer("ready")


@dp.message(Command("cmd"))
async def cmd(m: Message):
    if not is_owner(m): return
    text = m.text.split(maxsplit=1)[1]
    tid = await new_task(m.chat.id, "cmd", {"command": text})
    await m.answer(tid)


async def api_pending(req):
    if req.headers.get("X-Secret") != AGENT_SECRET:
        return web.json_response({}, status=401)
    return web.json_response({"tasks": [
        {"id": k, "type": v["type"], "payload": v["payload"]}
        for k, v in tasks.items() if v["status"] == "pending"
    ]})


async def api_result(req):
    tid = req.match_info["task_id"]
    data = await req.json()
    t = tasks[tid]
    t["status"] = "done"

    if data["type"] == "text":
        await bot.send_message(t["chat_id"], data["content"])

    if data["type"] == "photo":
        img = base64.b64decode(data["content"])
        await bot.send_photo(t["chat_id"], BufferedInputFile(img, "screen.png"))

    return web.json_response({"ok": True})


async def main():
    app = web.Application()
    app.router.add_get("/api/tasks/pending", api_pending)
    app.router.add_post("/api/tasks/{task_id}/result", api_result)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 8765).start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())