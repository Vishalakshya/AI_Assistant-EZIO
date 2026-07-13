"use strict";
const electron = require("electron");
const path = require("path");
const child_process = require("child_process");
const fs = require("fs");
const net = require("net");
function _interopNamespaceDefault(e) {
  const n = Object.create(null, { [Symbol.toStringTag]: { value: "Module" } });
  if (e) {
    for (const k in e) {
      if (k !== "default") {
        const d = Object.getOwnPropertyDescriptor(e, k);
        Object.defineProperty(n, k, d.get ? d : {
          enumerable: true,
          get: () => e[k]
        });
      }
    }
  }
  n.default = e;
  return Object.freeze(n);
}
const path__namespace = /* @__PURE__ */ _interopNamespaceDefault(path);
const fs__namespace = /* @__PURE__ */ _interopNamespaceDefault(fs);
const net__namespace = /* @__PURE__ */ _interopNamespaceDefault(net);
let mainWindow = null;
let confirmWindow = null;
let splashWindow = null;
let backendProcess = null;
const isDev = process.env.NODE_ENV === "development";
const appDataPath = path__namespace.join(electron.app.getPath("appData"), "EZIO");
if (!fs__namespace.existsSync(appDataPath)) fs__namespace.mkdirSync(appDataPath, { recursive: true });
const logsDir = path__namespace.join(appDataPath, "logs");
if (!fs__namespace.existsSync(logsDir)) fs__namespace.mkdirSync(logsDir, { recursive: true });
const backendLogPath = path__namespace.join(logsDir, "backend.log");
const frontendLogPath = path__namespace.join(logsDir, "frontend.log");
if (!isDev) {
  const logStream = fs__namespace.createWriteStream(frontendLogPath, { flags: "a" });
  console.log = (...args) => logStream.write(`[INFO] ${(/* @__PURE__ */ new Date()).toISOString()} - ${args.join(" ")}
`);
  console.error = (...args) => logStream.write(`[ERROR] ${(/* @__PURE__ */ new Date()).toISOString()} - ${args.join(" ")}
`);
}
function createSplashWindow() {
  splashWindow = new electron.BrowserWindow({
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
  splashWindow.loadFile(path__namespace.join(__dirname, "../dist/splash.html")).catch(() => {
    createWindow();
  });
}
function createWindow() {
  mainWindow = new electron.BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    titleBarStyle: "hidden",
    titleBarOverlay: {
      color: "#09090b",
      symbolColor: "#fafafa"
    },
    show: false,
    // Don't show until ready
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path__namespace.join(__dirname, "preload.js")
    }
  });
  if (isDev) {
    mainWindow.loadURL("http://localhost:5173");
  } else {
    mainWindow.loadFile(path__namespace.join(__dirname, "../dist/index.html"));
  }
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http")) {
      electron.shell.openExternal(url);
    }
    return { action: "deny" };
  });
  mainWindow.once("ready-to-show", () => {
    if (splashWindow) {
      splashWindow.close();
      splashWindow = null;
    }
    mainWindow == null ? void 0 : mainWindow.show();
  });
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}
function createConfirmationWindow(actionToken, message) {
  if (confirmWindow) {
    confirmWindow.focus();
    return;
  }
  const primaryDisplay = electron.screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;
  confirmWindow = new electron.BrowserWindow({
    width: 450,
    height: 250,
    x: Math.round(width / 2 - 225),
    y: Math.round(height / 2 - 125),
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    modal: true,
    parent: mainWindow || void 0,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path__namespace.join(__dirname, "preload.js")
    }
  });
  const route = `#/confirm?token=${actionToken}&message=${encodeURIComponent(message)}`;
  if (isDev) {
    confirmWindow.loadURL(`http://localhost:5173/${route}`);
  } else {
    confirmWindow.loadFile(path__namespace.join(__dirname, "../dist/index.html"), { hash: route });
  }
  confirmWindow.flashFrame(true);
  confirmWindow.on("closed", () => {
    confirmWindow = null;
  });
}
function startBackend() {
  const backendExe = isDev ? path__namespace.join(__dirname, "../../backend/venv/Scripts/python.exe") : path__namespace.join(process.resourcesPath, "backend", "ezio-backend.exe");
  const backendArgs = isDev ? [path__namespace.join(__dirname, "../../backend/run_app.py")] : [];
  const backendOut = fs__namespace.openSync(backendLogPath, "a");
  const backendErr = fs__namespace.openSync(backendLogPath, "a");
  console.log(`Starting backend: ${backendExe}`);
  try {
    backendProcess = child_process.spawn(backendExe, backendArgs, {
      cwd: isDev ? path__namespace.join(__dirname, "../../backend") : path__namespace.join(process.resourcesPath, "backend"),
      detached: false,
      stdio: ["ignore", backendOut, backendErr]
    });
    backendProcess.on("error", (err) => {
      console.error("Failed to start backend process:", err);
      electron.dialog.showErrorBox("Backend Error", `Failed to start EZIO Backend.
${err.message}
Check logs at ${backendLogPath}`);
    });
    backendProcess.on("exit", (code, signal) => {
      console.log(`Backend exited with code ${code} and signal ${signal}`);
      if (code !== 0 && code !== null) {
        electron.dialog.showErrorBox("Backend Crash", `The EZIO Backend crashed (code: ${code}).
Check logs at ${backendLogPath}`);
      }
    });
  } catch (e) {
    electron.dialog.showErrorBox("Startup Error", `Could not launch backend.
${e.message}`);
  }
}
function waitForBackend(port, retries, callback) {
  const socket = new net__namespace.Socket();
  socket.setTimeout(2e3);
  socket.on("connect", () => {
    socket.destroy();
    callback();
  });
  socket.on("timeout", () => {
    socket.destroy();
    retry();
  });
  socket.on("error", () => {
    socket.destroy();
    retry();
  });
  const retry = () => {
    if (retries > 0) {
      setTimeout(() => waitForBackend(port, retries - 1, callback), 1e3);
    } else {
      electron.dialog.showErrorBox("Timeout", "Backend failed to start in time. Check logs.");
      callback();
    }
  };
  socket.connect(port, "127.0.0.1");
}
electron.ipcMain.handle("spawn-confirmation-window", async (event, { token, message }) => {
  if (!mainWindow || mainWindow.isMinimized() || !mainWindow.isVisible() || !mainWindow.isFocused()) {
    createConfirmationWindow(token, message);
    return true;
  }
  return false;
});
electron.ipcMain.on("close-confirmation-window", () => {
  if (confirmWindow) {
    confirmWindow.close();
  }
});
electron.app.whenReady().then(() => {
  startBackend();
  createSplashWindow();
  waitForBackend(8e3, 30, () => {
    createWindow();
  });
  electron.app.on("activate", () => {
    if (electron.BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});
electron.app.on("will-quit", () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
electron.app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    electron.app.quit();
  }
});
