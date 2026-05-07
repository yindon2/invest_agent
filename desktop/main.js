const { app, BrowserWindow, dialog, Menu } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

let mainWindow = null;
let pythonProcess = null;
const FLASK_PORT = 5199; // 企鹅奇才专用端口

// ---- 启动 Python Flask 后端 ----
function startFlask() {
  return new Promise((resolve, reject) => {
    // 查找 Python 可执行文件
    const pythonCandidates = [
      'python', 'python3', 'py',
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python313', 'python.exe'),
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python312', 'python.exe'),
    ];

    // 项目根目录（desktop 的上级）
    const appDir = path.join(__dirname, '..');

    function tryPython(index) {
      if (index >= pythonCandidates.length) {
        reject(new Error('找不到 Python，请确保已安装 Python 3.10+'));
        return;
      }

      const pythonExe = pythonCandidates[index];
      // 先检查是否存在
      if (pythonExe.includes('\\') && !fs.existsSync(pythonExe)) {
        tryPython(index + 1);
        return;
      }

      const proc = spawn(pythonExe, ['-u', 'web_app.py'], {
        cwd: appDir,
        env: { ...process.env, PORT: String(FLASK_PORT), PYTHONIOENCODING: 'utf-8' },
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true,
      });

      proc.stdout.on('data', (data) => {
        const text = data.toString();
        console.log('[Flask]', text.trim());
        if (text.includes('Running on')) {
          resolve(proc);
        }
      });

      proc.stderr.on('data', (data) => {
        console.error('[Flask:err]', data.toString().trim());
      });

      proc.on('error', () => {
        tryPython(index + 1);
      });

      proc.on('exit', (code) => {
        console.log(`Flask exited with code ${code}`);
        if (pythonProcess === proc) pythonProcess = null;
      });

      pythonProcess = proc;

      // 超时后备：等待端口就绪
      setTimeout(() => {
        checkPort(FLASK_PORT)
          .then(() => resolve(proc))
          .catch(() => tryPython(index + 1));
      }, 8000);
    }

    tryPython(0);
  });
}

function checkPort(port) {
  return new Promise((resolve, reject) => {
    const req = http.get(`http://127.0.0.1:${port}/`, (res) => {
      if (res.statusCode === 200) resolve();
      else reject();
    });
    req.on('error', reject);
    req.setTimeout(3000, () => { req.destroy(); reject(); });
  });
}

// ---- 创建主窗口 ----
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 800,
    minHeight: 600,
    title: '企鹅奇才 · AI 投资分析',
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    backgroundColor: '#0d1117',
    show: false,
  });

  // 自定义菜单（精简）
  const menu = Menu.buildFromTemplate([
    {
      label: '企鹅奇才',
      submenu: [
        { label: '关于', role: 'about' },
        { type: 'separator' },
        { label: '退出', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() },
      ],
    },
    {
      label: '编辑',
      submenu: [
        { label: '撤销', role: 'undo' },
        { label: '重做', role: 'redo' },
        { type: 'separator' },
        { label: '剪切', role: 'cut' },
        { label: '复制', role: 'copy' },
        { label: '粘贴', role: 'paste' },
      ],
    },
    {
      label: '视图',
      submenu: [
        { label: '开发者工具', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: '重新加载', role: 'reload' },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  mainWindow.loadURL(`http://127.0.0.1:${FLASK_PORT}/`);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ---- 应用生命周期 ----
app.whenReady().then(async () => {
  try {
    await startFlask();
    createWindow();
  } catch (err) {
    dialog.showErrorBox('启动失败', `无法启动 Python 后端:\n\n${err.message}\n\n请确保已安装 Python 3.10+ 和所需依赖 (pip install -r requirements.txt)`);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  killPython();
  app.quit();
});

app.on('before-quit', () => {
  killPython();
});

function killPython() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}
