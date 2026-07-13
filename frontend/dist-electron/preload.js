"use strict";
const electron = require("electron");
electron.contextBridge.exposeInMainWorld("electronAPI", {
  // Security/Confirmation UX bridging
  spawnConfirmationWindow: (token, message) => electron.ipcRenderer.invoke("spawn-confirmation-window", { token, message }),
  closeConfirmationWindow: () => electron.ipcRenderer.send("close-confirmation-window"),
  // Environment detection
  getPlatform: () => process.platform
});
