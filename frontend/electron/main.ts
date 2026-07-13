import { app, BrowserWindow, ipcMain, screen, shell, dialog } from 'electron';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';
import * as fs from 'fs';
import * as net from 'net';

let mainWindow: BrowserWindow | null = null;
let confirmWindow: BrowserWindow | null = null;
let splashWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

const isDev = process.env.NODE_ENV === 'development';

// Setup AppData folders for logs and config
const appDataPath = path.join(app.getPath('appData'), 'EZIO');
if (!fs.existsSync(appDataPath)) fs.mkdirSync(appDataPath, { recursive: true });
const logsDir = path.join(appDataPath, 'logs');
if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });

const backendLogPath = path.join(logsDir, 'backend.log');
const frontendLogPath = path.join(logsDir, 'frontend.log');

// Redirect console logs to file in production
if (!isDev) {
  const logStream = fs.createWriteStream(frontendLogPath, { flags: 'a' });
  console.log = (...args) => logStream.write(`[INFO] ${new Date().toISOString()} - ${args.join(' ')}\n`);
  console.error = (...args) => logStream.write(`[ERROR] ${new Date().toISOString()} - ${args.join(' ')}\n`);
}

function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 350,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  splashWindow.loadFile(path.join(__dirname, '../dist/splash.html')).catch(() => {
    // If no splash.html exists, just create main window directly
    createWindow();
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#09090b',
      symbolColor: '#fafafa',
    },
    show: false, // Don't show until ready
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  mainWindow.once('ready-to-show', () => {
    if (splashWindow) {
      splashWindow.close();
      splashWindow = null;
    }
    mainWindow?.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createConfirmationWindow(actionToken: string, message: string) {
  if (confirmWindow) {
    confirmWindow.focus();
    return;
  }
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  confirmWindow = new BrowserWindow({
    width: 450,
    height: 250,
    x: Math.round(width / 2 - 225),
    y: Math.round(height / 2 - 125),
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    modal: true,
    parent: mainWindow || undefined,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  const route = `#/confirm?token=${actionToken}&message=${encodeURIComponent(message)}`;
  if (isDev) {
    confirmWindow.loadURL(`http://localhost:5173/${route}`);
  } else {
    confirmWindow.loadFile(path.join(__dirname, '../dist/index.html'), { hash: route });
  }

  confirmWindow.flashFrame(true);
  confirmWindow.on('closed', () => { confirmWindow = null; });
}

// --- Backend Lifecycle Management ---
function startBackend() {
  const backendExe = isDev 
    ? path.join(__dirname, '../../backend/venv/Scripts/python.exe')
    : path.join(process.resourcesPath, 'backend', 'ezio-backend.exe');
  
  const backendArgs = isDev 
    ? [path.join(__dirname, '../../backend/run_app.py')]
    : [];

  const backendOut = fs.openSync(backendLogPath, 'a');
  const backendErr = fs.openSync(backendLogPath, 'a');

  console.log(`Starting backend: ${backendExe}`);
  try {
    backendProcess = spawn(backendExe, backendArgs, {
      cwd: isDev ? path.join(__dirname, '../../backend') : path.join(process.resourcesPath, 'backend'),
      detached: false,
      stdio: ['ignore', backendOut, backendErr]
    });

    backendProcess.on('error', (err) => {
      console.error('Failed to start backend process:', err);
      dialog.showErrorBox('Backend Error', `Failed to start EZIO Backend.\n${err.message}\nCheck logs at ${backendLogPath}`);
    });

    backendProcess.on('exit', (code, signal) => {
      console.log(`Backend exited with code ${code} and signal ${signal}`);
      if (code !== 0 && code !== null) {
        dialog.showErrorBox('Backend Crash', `The EZIO Backend crashed (code: ${code}).\nCheck logs at ${backendLogPath}`);
      }
    });
  } catch (e: any) {
    dialog.showErrorBox('Startup Error', `Could not launch backend.\n${e.message}`);
  }
}

function waitForBackend(port: number, retries: number, callback: () => void) {
  const socket = new net.Socket();
  socket.setTimeout(2000);
  
  socket.on('connect', () => {
    socket.destroy();
    callback();
  });
  
  socket.on('timeout', () => {
    socket.destroy();
    retry();
  });
  
  socket.on('error', () => {
    socket.destroy();
    retry();
  });

  const retry = () => {
    if (retries > 0) {
      setTimeout(() => waitForBackend(port, retries - 1, callback), 1000);
    } else {
      dialog.showErrorBox('Timeout', 'Backend failed to start in time. Check logs.');
      callback(); // Try opening window anyway to show error state in UI
    }
  };

  socket.connect(port, '127.0.0.1');
}

// --- IPC Bridges ---
ipcMain.handle('spawn-confirmation-window', async (event, { token, message }) => {
  if (!mainWindow || mainWindow.isMinimized() || !mainWindow.isVisible() || !mainWindow.isFocused()) {
    createConfirmationWindow(token, message);
    return true;
  }
  return false;
});

ipcMain.on('close-confirmation-window', () => {
  if (confirmWindow) {
    confirmWindow.close();
  }
});

app.whenReady().then(() => {
  startBackend();
  createSplashWindow();
  waitForBackend(8000, 30, () => {
    createWindow();
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('will-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
