import time
import platform
import subprocess
import ctypes
import base64
import os
import io
import logging
import threading
import socket
import requests
import psutil

try:
    from PIL import ImageGrab
    SCREENSHOT_OK = True
except ImportError:
    SCREENSHOT_OK = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SERVER_URL = "http://YOUR_SERVER_IP:8765"
AGENT_SECRET = "YOUR_SECRET_KEY"
POLL_INTERVAL = 3
PING_INTERVAL = 5

OS = platform.system()
HEADERS = {"X-Secret": AGENT_SECRET, "Content-Type": "application/json"}

shell_cwd: str = os.path.expanduser("~")


def _get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return ""


def _get_broadcast(local_ip):
    if not local_ip:
        return "255.255.255.255"
    parts = local_ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.255"
    return "255.255.255.255"


def ping_loop():
    while True:
        try:
            local_ip = _get_local_ip()
            broadcast = _get_broadcast(local_ip)
            requests.post(
                f"{SERVER_URL}/api/ping",
                headers=HEADERS,
                json={"ip": local_ip, "broadcast": broadcast},
                timeout=5,
            )
        except Exception as e:
            log.warning(str(e))
        time.sleep(PING_INTERVAL)


def send_result(task_id, res_type, content):
    try:
        requests.post(
            f"{SERVER_URL}/api/tasks/{task_id}/result",
            json={"type": res_type, "content": content},
            headers=HEADERS,
            timeout=30,
        )
    except Exception as e:
        log.error(str(e))


def handle_lock(task_id, _):
    try:
        if OS == "Windows":
            ctypes.windll.user32.LockWorkStation()
        elif OS == "Linux":
            subprocess.run(["loginctl", "lock-session"])
        elif OS == "Darwin":
            subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        send_result(task_id, "ok", "")
    except Exception as e:
        send_result(task_id, "error", str(e))


def handle_shutdown(task_id, _):
    try:
        send_result(task_id, "ok", "")
        time.sleep(1)
        if OS == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "5"])
        else:
            subprocess.run(["shutdown", "-h", "+0"])
    except Exception as e:
        send_result(task_id, "error", str(e))


def handle_screenshot(task_id, _):
    if not SCREENSHOT_OK:
        send_result(task_id, "error", "no pillow")
        return
    try:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        send_result(task_id, "photo", base64.b64encode(buf.getvalue()).decode())
    except Exception as e:
        send_result(task_id, "error", str(e))


def _run_cmd(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd)
    return r.stdout.decode(errors="ignore"), r.stderr.decode(errors="ignore"), r.returncode


def handle_cmd(task_id, payload):
    cmd = payload.get("command", "")
    try:
        out, err, code = _run_cmd(cmd)
        send_result(task_id, "text", f"{out}\n{err}\nexit={code}")
    except Exception as e:
        send_result(task_id, "error", str(e))


def handle_shell_cmd(task_id, payload):
    global shell_cwd
    cmd = payload.get("command", "")

    if cmd.startswith("cd"):
        path = cmd[2:].strip() or os.path.expanduser("~")
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.join(shell_cwd, path)
        if os.path.isdir(path):
            shell_cwd = path
        send_result(task_id, "shell_result", {"output": "", "new_cwd": shell_cwd})
        return

    try:
        out, err, code = _run_cmd(cmd, shell_cwd)
        send_result(task_id, "shell_result", {"output": out + err, "new_cwd": shell_cwd})
    except Exception as e:
        send_result(task_id, "shell_result", {"output": str(e), "new_cwd": shell_cwd})


def handle_download(task_id, payload):
    path = os.path.expanduser(payload.get("path", ""))
    if not os.path.isfile(path):
        send_result(task_id, "error", "not found")
        return
    with open(path, "rb") as f:
        send_result(task_id, "file", {
            "filename": os.path.basename(path),
            "data_b64": base64.b64encode(f.read()).decode()
        })


def handle_upload(task_id, payload):
    try:
        path = os.path.expanduser(payload.get("remote_path", "file"))
        data = base64.b64decode(payload.get("data_b64", ""))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        send_result(task_id, "ok", "")
    except Exception as e:
        send_result(task_id, "error", str(e))


def handle_apps_list(task_id, _):
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        procs.append(f"{p.info['pid']} {p.info['name']}")
    send_result(task_id, "text", "\n".join(procs[:100]))


def handle_apps_start(task_id, payload):
    try:
        subprocess.Popen(payload.get("name"))
        send_result(task_id, "ok", "")
    except Exception as e:
        send_result(task_id, "error", str(e))


def handle_apps_stop(task_id, payload):
    name = payload.get("name", "")
    for p in psutil.process_iter(["name"]):
        if name in p.info["name"]:
            p.terminate()
    send_result(task_id, "ok", "")


HANDLERS = {
    "lock": handle_lock,
    "shutdown": handle_shutdown,
    "screenshot": handle_screenshot,
    "cmd": handle_cmd,
    "shell_cmd": handle_shell_cmd,
    "download": handle_download,
    "upload": handle_upload,
    "apps_list": handle_apps_list,
    "apps_start": handle_apps_start,
    "apps_stop": handle_apps_stop,
}


def poll_loop():
    while True:
        try:
            r = requests.get(f"{SERVER_URL}/api/tasks/pending", headers=HEADERS, timeout=10)
            for t in r.json().get("tasks", []):
                threading.Thread(target=HANDLERS[t["type"]], args=(t["id"], t.get("payload", {}))).start()
        except:
            pass
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    threading.Thread(target=ping_loop, daemon=True).start()
    poll_loop()