"""
企鹅奇才 · 桌面客户端
==================
用法: python desktop.py

调用 Windows 11 内置 Edge WebView2 创建原生窗口。
无需安装任何额外依赖。
"""
import sys, os, threading, time, subprocess, socket, json, atexit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
PORT = int(os.environ.get('PORT', 5199))

# ── 1. 启动 Flask 后端 ──
from web_app import app

def run_flask():
    app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)

t = threading.Thread(target=run_flask, daemon=True)
t.start()

print("正在启动企鹅奇才...")
for i in range(60):
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect(('127.0.0.1', PORT))
        s.close()
        break
    except:
        time.sleep(0.5)

print(f"✓ 后端就绪 → http://127.0.0.1:{PORT}")

# ── 2. 用 Edge App Mode 创建桌面窗口 ──
# Windows 11 自带 Edge，--app 模式隐藏浏览器 UI，看起来像原生桌面程序
edge_paths = [
    os.path.expandvars('%ProgramFiles(x86)%\\Microsoft\\Edge\\Application\\msedge.exe'),
    os.path.expandvars('%ProgramFiles%\\Microsoft\\Edge\\Application\\msedge.exe'),
    'msedge',
]

browser_exe = None
for exe in edge_paths:
    try:
        if exe == 'msedge':
            # 从 PATH 中找
            import shutil
            exe = shutil.which('msedge') or shutil.which('edge')
            if exe:
                browser_exe = exe
                break
        elif os.path.exists(exe):
            browser_exe = exe
            break
    except:
        continue

if browser_exe:
    proc = subprocess.Popen(
        [browser_exe, f'--app=http://127.0.0.1:{PORT}/',
         '--no-sandbox', '--disable-extensions'],
        close_fds=True
    )
    print(f"✓ 桌面窗口已打开 (PID: {proc.pid})")
    print("  关闭窗口或按 Ctrl+C 退出")
else:
    print("Edge 未找到，请在浏览器中打开:")
    print(f"  http://127.0.0.1:{PORT}/")

# ── 3. 等待退出 ──
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n正在关闭...")

print("企鹅奇才已退出")
