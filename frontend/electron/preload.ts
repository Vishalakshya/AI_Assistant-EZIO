import { contextBridge, ipcRenderer } from 'electron';

// Expose safe, strict APIs to the React renderer
// Context Isolation completely blocks React from accessing `fs`, `child_process`, or `process.env`

contextBridge.exposeInMainWorld('electronAPI', {
  // Security/Confirmation UX bridging
  spawnConfirmationWindow: (token: string, message: string) => 
    ipcRenderer.invoke('spawn-confirmation-window', { token, message }),
    
  closeConfirmationWindow: () => 
    ipcRenderer.send('close-confirmation-window'),

  // Environment detection
  getPlatform: () => process.platform,
});

// TypeScript declaration for React
declare global {
  interface Window {
    electronAPI: {
      spawnConfirmationWindow: (token: string, message: string) => Promise<boolean>;
      closeConfirmationWindow: () => void;
      getPlatform: () => string;
    };
  }
}
